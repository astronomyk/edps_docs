A complete simple workflow
==========================

In this section we implement a workflow with the same shape as the basic one in
:doc:`../workflow_guide/overview`, with the addition of classification and
association, detailed by a "hypothetical" instrument and pipeline.

The workflow graphic representation is exactly the ``demo0`` structure: three raw
types (``OBJECT``, ``FLAT``, ``BIAS``) feeding a ``bias`` → ``flat`` → ``object``
cascade, plus two static calibrations (``catalog``, ``SKY``) attached to
``object``.


The pipeline specification
--------------------------

The types of data, their association rules and the data reduction pipeline are
designed according to the following specifications.

run_bias
~~~~~~~~

The biases are processed with ``run_bias``, that needs at least 3 files with
``DPR.TYPE = BIAS`` that must have the same ``ARM`` and ``TPL.START`` header
keywords. The product is named ``MASTERBIAS``. Its validity range according to
the calibration plan is 1 day, but biases as old as 1 week are sufficient.

.. code-block:: text

   -- Recipe: run_bias -----------------------------------------
   Inputs   number    Grouping keywords   Match keywords
   BIAS     3         TPL.START, ARM      N/A
   Products:
   MASTERBIAS (validity: 1 day)
   Validity ranges:
    Calibration plan: 1 day
    Sufficient quality for certification: 1 week
   -------------------------------------------------------------

run_flat
~~~~~~~~

The flats are processed with ``run_flat``, that needs at least 3 files with
``DPR.TYPE = FLATS`` that must have the same ``ARM`` and ``TPL.START`` header
keywords. A ``MASTERBIAS`` is needed as associated input. The product is named
``MASTERFLAT``. Its validity range according to the calibration plan is 1 day,
but biases as old as 1 week are sufficient.

.. code-block:: text

   -- Recipe: run_flat -----------------------------------------
   Inputs    number   Grouping Keywords   Match keywords
   FLAT      3        TPL.START, ARM      N/A

   MASTERBIAS 1       N/A                 INSTRUME, ARM,
                                          INS.SLIT

   Products:
   MASTERFLAT (validity: 1 night)
   Validity ranges:
    Calibration plan: 1 day
    Sufficient quality for certification: 1 week
   -------------------------------------------------------------

run_science
~~~~~~~~~~~

Science frames are processed individually. They need a ``MASTERFLAT`` and a
``MASTERBIAS``, that must match ``ARM``, ``INSTRUME``, and ``INS.SLIT``. A
``SKY`` frame matching ``ARM`` and ``INS.SLIT`` is also needed; in the case of
VIS observations, it has also to match ``TPL.START`` (to follow the calibration
plan) or within 1 day for sufficient precision. In the case of NIR observations,
it has to match ``TPL.START`` otherwise the quality of the reduction is not good.

Optional calibration ``CATALOGUE`` is optional, and has to be provided only if
photometric calibration is needed. In the case of NIR observations, the input
``CATALOG`` has to match the ``ARM`` of the observations. In the case of VIS
observations, the input ``CATALOG`` needs to have either ``ARM=VIR`` or
``ARM=RED``.

.. code-block:: text

   -- Recipe: run_science --------------------------------------
   Inputs     number   Grouping keywords   Match keywords
   SCIENCE    1        ARCFILE             N/A

   SKY        1        ARCFILE             ARM, INS.SLIT (for VIS and NIR)
                                          TPL.START (preferred) or
                                          within 24 hrs, if VIS.
                                          TPL.START only if NIR.

   MASTERBIAS 1        N/A                 INSTRUME, ARM, INS.SLIT

   MASTERFLAT 1        N/A                 INSTRUME, ARM, INS.SLIT

   CATALOGUE  0        N/A                 ARM=NIR for NIR observations
                                          ARM=RED or ARM = VIS for VIS observations.

   Product:
   REDUCED_SCIENCE
   -------------------------------------------------------------


The workflow
------------

demo1_wkf.py
~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_wkf.py
   :linenos:

   from edps import task, SCIENCE, alternative_association
   from .demo1_datasources import *
   from .demo1_rules import *
   from .demo1_task_functions import *

   # --- Processing tasks --------------------------------------------------

   # - Task to reduce raw biases
   bias_task = (task("bias")
                .with_recipe("run_bias")
                .with_main_input(raw_bias)
                .build())

   # - Task to reduce raw flats
   flat_task = (task("flat")
                .with_recipe("run_flat")
                .with_main_input(raw_flat)
                .with_associated_input(bias_task, [MASTERBIAS])
                .build())

   # The sky is associated under certain conditions, that depends on the properties of
   # the input data.
   # If the input is taken with arm=VIS, then the rules attach_sky_vis are used to
   # associate the sky exposure.
   # If the input is taken with arm=NIR, then the rules attach_sky_nir are used to
   # associate the sky exposure.
   alternative_sky = (alternative_association()
       .with_associated_input(raw_sky, condition=is_input_VIS, match_rules=attach_sky_vis)
       .with_associated_input(raw_sky, condition=is_input_NIR, match_rules=attach_sky_nir))

   # - Task to reduce science observations.
   # If the user wants to do photometric calibration, then a static catalogue is associated,
   # otherwise it is not associated. The choice is done by setting the parameter
   # flux_calibration in the demo1_parameters.file
   # flux_calibration = "TRUE", the static catalogue is associated, and the recipe
   #                            performs the flux calibration

   science_task = (task("object")
                   .with_recipe("run_science")
                   .with_dynamic_parameter("arm_used", which_arm)
                   .with_main_input(raw_science)
                   .with_alternative_associated_inputs(alternative_sky)
                   .with_associated_input(bias_task, [MASTERBIAS])
                   .with_associated_input(flat_task, [MASTERFLAT])
                   .with_associated_input(static_catalog, condition=perfor_photometric_calibration)
                   .with_meta_targets([SCIENCE])
                   .build())

demo1_datasources.py
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_datasources.py
   :linenos:

   from edps import data_source, RelativeTimeRange
   from .demo1_classification import *
   from . import demo1_keywords as kwd
   from edps.generator.time_range import UNLIMITED, ONE_DAY

   # Convention for Data sources Association rule levels:
   # Each data source can have several match function which correspond to different
   # quality levels for the selected data. The level is specified as a number that
   # follows this convention:
   #   level < 0: more restrictive than the calibration plan
   #   level = 0  follows the calibration plan
   #   level = 1  quality sufficient for QC1 certification
   #   level = 2  probably still acceptable quality
   #   level = 3  significant risk of bad quality results

   # --- General variables -------------------------------------------------
   # Header keywords that defines the instrument setup
   setup = [kwd.tpl_start, kwd.arm, kwd.ins_slit]
   # Header keywords to be used for the grouping
   grouping = [kwd.tpl_start, kwd.arm]

   # --- Raw data sources --------------------------------------------------

   # Raw biases
   raw_bias = (data_source("BIAS")
               .with_classification_rule(bias_class)
               .with_min_group_size(3)
               .with_setup_keywords(setup)
               .with_grouping_keywords(grouping)
               .with_match_keywords([kwd.arm], time_range=RelativeTimeRange(-3, 3), level=0)
               .with_match_keywords([kwd.arm], time_range=UNLIMITED, level=3)
               .build())

   # Raw flats
   raw_flat = (data_source("FLAT")
               .with_classification_rule(flat_class)
               .with_min_group_size(3)
               .with_setup_keywords(setup)
               .with_grouping_keywords(grouping)
               .with_match_keywords([kwd.arm, kwd.ins_slit], time_range=ONE_DAY, level=0)
               .with_match_keywords([kwd.arm, kwd.ins_slit], time_range=UNLIMITED, level=3)
               .build())

   # Raw sky exposures
   raw_sky = (data_source("SKY")
              .with_classification_rule(sky_class)
              .with_grouping_keywords([kwd.arcfile])
              .build())

   # Raw science exposures
   raw_science = (data_source("OBJECT")
                  .with_classification_rule(science_class)
                  .with_grouping_keywords([kwd.arcfile])
                  .build())

   # --- Static calibrations -----------------------------------------------

   # Catalogue of standard stars
   static_catalog = (data_source("catalog")
                     .with_classification_rule(static_catalog_class)
                     .with_match_function(rules.is_assoc_catalogue, time_range=UNLIMITED)
                     .build())

demo1_classification.py
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_classification.py
   :linenos:

   from edps import classification_rule
   from . import demo1_keywords as kwd
   from . import demo1_rules as rules

   # Dictionaries with general keywords
   demo             = {kwd.instrume: "DEMO"}
   calib_keywords   = {**demo, kwd.dpr_catg: "CALIB"}
   science_keywords = {**demo, kwd.dpr_catg: "SCIENCE"}

   # RAW FILES
   bias_class    = classification_rule('BIAS', {**calib_keywords, kwd.dpr_type: "BIAS"})
   flat_class    = classification_rule('FLAT', {**calib_keywords, kwd.dpr_type: "FLAT"})
   science_class = classification_rule('SCIENCE', {**science_keywords, kwd.dpr_type: "OBJECT"})
   sky_class     = classification_rule('SKY', {**science_keywords, kwd.dpr_type: "SKY"})

   # MASTER CALIBRATIONS
   MASTERBIAS = classification_rule("MASTERBIAS", {**demo, kwd.pro_catg: "MASTERBIAS"})
   MASTERFLAT = classification_rule('MASTERFLAT', {**demo, kwd.pro_catg: 'MASTERFLAT'})

   # STATIC CALIBRATIONS
   static_catalog_class = classification_rule('CATALOG', {**demo, kwd.pro_catg: 'CATALOG'})

demo1_rules.py
~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_rules.py
   :linenos:

   # CLASSIFICATION RULES
   from edps.generator.time_range import *
   from edps import match_rules
   from . import demo1_keywords as kwd


   def is_demo(f):
       return f[kwd.instrume] == "DEMO"


   # The DPR.TYPE of sky exposures can be either SKY or OFFSET_SKY.
   def is_sky(f):
       return is_demo(f) and f[kwd.dpr_type] in ["SKY", "OFFSET_SKY"]


   # ASSOCIATION RULES
   #  - first, e.g. ref=trigger (e.g. science)
   #  - second, e.g. f=file to associate (e.g. calibration)

   def is_assoc_catalogue(ref, f):
       # I must have a match between arms, or for the VIS arm, I can associate a
       # catalogue with ARM=RED.
       return f[kwd.arm] == ref[kwd.arm] or (f[kwd.arm] == "RED" and ref[kwd.arm] == "VIS")


   # ASSOCIATION RULES THAT OVERRIDE THOSE SPECIFIED IN THE DATA_SOURCE

   setup = [kwd.instrume, kwd.arm, kwd.ins_slit]

   # The sky in the visual can be from the same night for decent quality
   attach_sky_vis = (match_rules()
                     .with_match_keywords(setup + [kwd.tpl_start], level=0)
                     .with_match_keywords(setup, time_range=SAME_NIGHT, level=1))

   # The sky in the NIR must be from the same template as the observation.
   attach_sky_nir = (match_rules()
                     .with_match_keywords(setup + [kwd.tpl_start], level=0))

demo1_keywords.py
~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_keywords.py
   :linenos:

   # HEADER KEYWORDS USED FOR CLASSIFICATION, GROUPING, AND ASSOCIATION.
   instrume  = "instrume"
   arm       = "ARM"
   ins_slit  = "ins.slit"
   tpl_start = "tpl.start"
   mjd_obs   = "mjd-obs"
   dpr_type  = "dpr.type"
   dpr_catg  = "dpr.catg"
   pro_catg  = "pro.catg"
   arcfile   = "arcfile"

demo1_task_functions.py
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo1_task_functions.py
   :linenos:

   from edps import get_parameter, JobParameters, ClassifiedFitsFile, List

   # --- Functions to determine the ARM of the input data -------------------
   def is_input_NIR(params: JobParameters) -> bool:
       return get_parameter(params, "arm_used") == "NIR"


   def is_input_VIS(params: JobParameters) -> bool:
       return get_parameter(params, "arm_used") == "VIS"


   def which_arm(files: List[ClassifiedFitsFile]):
       # Note: files are only the main input files, not the associated files
       arm = files[0].get_keyword_value("ARM", None)
       return arm


   # --- Function to read workflow parameters -------------------------------
   def perfor_photometric_calibration(params: JobParameters) -> bool:
       return get_parameter(params, "flux_calibration") == "TRUE"

demo1_parameters.yaml
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
   :caption: demo1_parameters.yaml
   :linenos:

   qc1_parameters:
     tags: [ qc1calib ]
     is_default: yes
     workflow_parameters:
       # flux_calibration = "TRUE", the static catalogue is associated, and the recipe
       #                            performs the flux calibration. Otherwise, the static
       #                            catalogue is not associated to the dataset.
       flux_calibration: "TRUE"
     recipe_parameters:
       # List the recipe parameters, ordered per task, to be adopted
       # For the parameters not listed, the recipe default are adopted.
       object:
         demo.run_science.trim: "TRUE"


Reading the example
-------------------

Three things in ``demo1_wkf.py`` are worth pausing over.

**The dynamic parameter comes first.**
   ``.with_dynamic_parameter("arm_used", which_arm)`` inspects the main input of
   each job and stores the ``ARM`` keyword. Everything downstream — the two
   ``condition=`` clauses on the sky association — reads that parameter. Without
   it, ``is_input_VIS`` and ``is_input_NIR`` have nothing to test.

**Alternatives express "one or the other, never both".**
   ``alternative_sky`` lists the VIS rule first and the NIR rule second. Because
   the two conditions are mutually exclusive, exactly one will fire.

**Optionality is expressed as a condition, not as** ``min_ret=0``.
   The static catalogue is attached only when ``flux_calibration`` is ``"TRUE"``.
   When the condition is False, the job is **not** checked for the catalogue at
   all and is still considered complete — which is different from
   ``min_ret=0``, where the association is always attempted.
