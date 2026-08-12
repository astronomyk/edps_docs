Compacting a workflow
=====================

In this section we re-design a workflow following the same principles of the
reduction cascade of :doc:`simple`, but adding extra constraints driven by
different instrument and pipeline designs.

The general rule is to **keep a workflow as simple as possible**, minimising the
number of tasks and datasources whenever possible. There are two main cases where
it is possible to merge tasks and classification rules:

* If two tasks share the same **main input and recipe**, it should be possible to
  combine them in a single task, regardless of whether they differ in terms of
  associated inputs or other parameters.

* If several categories of files can be processed by the **same recipe**, and have
  the **same association rules**, it should be possible to include them in the same
  data source.

Keeping these considerations in mind, we present two different workflow designs
that exploit different methods to combine tasks and datasources. The first design
(:ref:`demo2`) is a "straightforward translation" of the data reduction
requirement; the second design (:ref:`demo3`) is a "simplified" version that
merges tasks and combines classification rules. **This second approach should be
adopted whenever possible.**


The pipeline specification
--------------------------

run_bias
~~~~~~~~

The bias recipe (``run_bias``) needs at least 3 raw bias input frames
(``DPR.TYPE = BIAS``). The inputs have to be grouped by the ``TPL.START``,
``ARM``, and ``INS1.SLIT`` keywords. The classification to be written in the
input sof must be either ``BIAS_VIS`` or ``BIAS_NIR``, depending on the type of
the inputs. The products are ``MASTERBIAS_VIS`` or ``MASTERBIAS_NIR``, depending
on inputs. The calibration plan foresees to take biases every day, but their
validity for scientifically valid reduction is 1 week.

.. code-block:: text

   -- Recipe: run_bias -----------------------------------------
   Inputs   number   Grouping keywords  Match keywords  dpr.type
   BIAS_VIS 3        TPL.START, ARM     N/A             BIAS
                     INS1.SLIT
   or;

   BIAS_NIR 3        TPL.START, ARM     N/A             BIAS
                     INS2.SLIT

   Products:
   MASTERBIAS_VIS or
   MASTERBIAS_NIR

   Validity ranges:
    Calibration plan: 1 day
    Sufficient quality for certification: 1 week
   -------------------------------------------------------------

run_flat
~~~~~~~~

The recipe to process the flat fields (``run_flat``) requires 3 flats as main
input (``DPR.TYPE = FLAT``), and they need to be flagged as ``FLAT_VIS`` or
``FLAT_NIR`` in the recipe input sof. The inputs have to be grouped by
``TPL.START``, ``ARM``, and ``INS1.SLIT`` and ``INS2.SLIT``. The recipe also
needs a masterbias, matching the same ``INSTRUME``, ``ARM``, and ``INS1.SLIT``
(if VIS observations) or ``INS2.SLIT`` (if NIR observations) as the input flats.
The calibration plan foresees the acquisition of flats every day, but a flat from
1 week is sufficient for scientifically valid results.

Optional inputs for the science is an offset sky (``DPR.TYPE = SKY``), that has
to match the same ``ARM``, ``INSTRUME`` and ``INS1.SLIT`` (if VIS observations) or
``INS2.SLIT`` (if NIR observation). The sky has to be either of the same
``tpl.start`` of the science, or within the same night for a quick check. If
observations are in NIR, also a static catalogue is needed.

.. code-block:: text

   -- Recipe: run_flat -----------------------------------------
   Inputs   number  Grouping Keywords  Match keywords          dpr.type
   FLAT_VIS 3       TPL.START, ARM     N/A                     FLAT
                    INS1.SLIT
   MASTERBIAS_VIS 1 N/A                INSTRUME, ARM, INS1.SLIT  N/A

   or:

   FLAT_NIR 3       TPL.START, ARM     N/A                     FLAT
                    INS2.SLIT
   MASTERBIAS_NIR 1 N/A                INSTRUME, ARM, INS2.SLIT  N/A

   Products:
   MASTERFLAT_VIS or
   MASTERFLAT_NIR
   Validity ranges:
    Calibration plan: 1 day
    Sufficient quality for certification: 1 week
   -------------------------------------------------------------

run_science
~~~~~~~~~~~

The science recipe (``run_science``) reduces science inputs independently
(``DPR.TYPE = SCIENCE``).

.. code-block:: text

   -- Recipe: run_science --------------------------------------
   Inputs      number Grouping keywords  Match keywords      dpr.type
   SCIENCE_VIS 1      MJD.OBS            N/A                 SCIENCE
   SKY         0      N/A                ARM, INS1.SLIT      SKY
                                         TPL.START (preferred) or
                                         within 24 hrs (quick check only)
   MASTERBIAS_VIS 1   N/A                INSTRUME, ARM, INS1.SLIT
   MASTERFLAT_VIS 1   N/A                INSTRUME, ARM, INS1.SLIT

   or:

   SCIENCE_NIR 1      MJD.OBS            N/A                 SCIENCE
   SKY         0      N/A                ARM, INS2.SLIT      SKY
                                         TPL.START (preferred) or
                                         within 24 hrs (quick check only)
   MASTERBIAS_NIR 1   N/A                INSTRUME, ARM, INS2.SLIT
   MASTERFLAT_NIR 1   N/A                INSTRUME, ARM, INS2.SLIT

   CATALOG            N/A                ARM

   Product:
   REDUCED_SCIENCE
   -------------------------------------------------------------

   Notes:
   1) ARM=VIS have slit width defined in INS1.SLIT. Values in INS2.SLIT
      could be wrong.

   2) ARM=NIR have slit width defined in INS2.SLIT. Values in INS1.SLIT
      could be wrong.

   3) A single observing template generates either VIS or NIR exposures.


.. _demo2:

First workflow: one task per tag
--------------------------------

This workflow represents a "straightforward translation" of the pipeline and
instrument description. Each tag is assigned a datasource and a task for
processing. For the bias case, we group the two biases tasks within one
sub-workflow to highlight the difference with the other tasks. In this example,
it is not necessary to determine the arm of the exposures via a dynamic
parameter, because each VIS and NIR type of observation have their own datasource
and task.

In the workflow layout, note the orange colour of the "bias" element, denoting
the sub-workflow that contains the two bias tasks (``bias_vis`` and ``bias_nir``).
In order to simplify the workflow layout, all the VIS/NIR tasks could be merged
into a subworkflow. In the next example, we show how to create a single task per
type (e.g. flat) that serves both arms.

.. code-block:: text
   :caption: The ``demo2_wkf`` layout

   Raw Types
   ┌──────────────────────────────────────────────────────────────────────┐
   │ RAW_SCIENCE_VIS  RAW_FLAT_VIS  RAW_BIAS_NIR  RAW_BIAS_VIS            │
   │ RAW_FLAT_NIR     RAW_SCIENCE_NIR                                     │
   └──────────────────────────────────┬───────────────────────────────────┘
                                 ( bias )              <- subworkflow (orange)
                                  ╱      ╲
                        ( flat_vis )      ( flat_nir )
                              │   Static Calibrations      │
                              │  ┌────────────────────┐    │
                              │  │ RAW_SKY_VIS        │    │
                              │  │ RAW_SKY_NIR        │    │
                              │  │ catalog            │    │
                              │  └────────────────────┘    │
                        ( science_vis )            ( science_nir )

demo2_wkf.py
~~~~~~~~~~~~

.. code-block:: python
   :caption: demo2_wkf.py
   :linenos:

   from edps import task, SCIENCE
   from .demo2_datasources import *
   from .demo2_subworkflow import bias_arm

   # --- Processing tasks --------------------------------------------------

   # Tasks for processing the biases
   # Instead of creating 2 tasks for different types of biases,
   # I "delegate" the task creation to a subworkflow
   # exploiting the fact that the 2 tasks have the same "structure"
   bias_vis_task = bias_arm(raw_bias_vis, 'vis')
   bias_nir_task = bias_arm(raw_bias_nir, 'nir')

   # - Tasks for processing the flat fields
   # Here it is shown how two tasks are created without using a subworkflow
   flat_vis_task = (task('flat_vis')
                    .with_recipe('run_flat')
                    .with_main_input(raw_flat_vis)
                    .with_associated_input(bias_vis_task, [MASTERBIAS_VIS])
                    .with_input_filter(MASTERBIAS_VIS)
                    .build())

   flat_nir_task = (task('flat_nir')
                    .with_recipe('run_flat')
                    .with_main_input(raw_flat_nir)
                    .with_associated_input(bias_nir_task, [MASTERBIAS_NIR])
                    .with_input_filter(MASTERBIAS_NIR)
                    .build())

   # - Tasks for science processing
   science_vis_task = (task('science_vis')
                       .with_recipe('run_science')
                       .with_meta_targets([SCIENCE])
                       .with_main_input(raw_science_vis)
                       .with_associated_input(raw_sky_vis, min_ret=0)  # sky is optional
                       .with_associated_input(bias_vis_task, [MASTERBIAS_VIS])
                       .with_associated_input(flat_vis_task, [MASTERFLAT_VIS])
                       .build())

   science_nir_task = (task('science_nir')
                       .with_recipe('run_science')
                       .with_meta_targets([SCIENCE])
                       .with_main_input(raw_science_nir)
                       .with_associated_input(raw_sky_nir, min_ret=0)  # sky is optional
                       .with_associated_input(bias_nir_task, [MASTERBIAS_NIR])
                       .with_associated_input(flat_nir_task, [MASTERFLAT_NIR])
                       .with_associated_input(static_catalog)
                       .build())

demo2_subworkflow.py
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo2_subworkflow.py
   :linenos:

   from edps import subworkflow, task
   from .demo2_datasources import *

   @subworkflow("bias", "")
   def bias_arm(raw_bias, tag):
       bias_task = (task('bias_' + tag)
                    .with_recipe('run_bias')
                    .with_main_input(raw_bias)
                    .build())
       return bias_task

Note ``'bias_' + tag``: this is how the subworkflow satisfies the requirement
that every task name in a workflow be unique, even when the subworkflow is
instantiated twice.

demo2_datasources.py
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo2_datasources.py
   :linenos:

   from edps import data_source, RelativeTimeRange
   from .demo2_classification import *
   from edps.generator.time_range import UNLIMITED, ONE_DAY, ONE_WEEK, SAME_NIGHT
   from . import demo2_keywords as kwd

   # Convention for Data sources Association rule levels:
   # Each data source can have several match function which correspond to different
   # quality levels for the selected data. The level is specified as a number that
   # follows this convention:
   #   level < 0: more restrictive than the calibration plan
   #   level = 0  follows the calibration plan
   #   level = 1  quality sufficient for QC1 certification
   #   level = 2  probably still acceptable quality
   #   level = 3  significant risk of bad quality results

   # standard matching keywords:

   setup1 = [kwd.tpl_start, kwd.arm, kwd.ins1_slit]
   setup2 = [kwd.tpl_start, kwd.arm, kwd.ins2_slit]

   raw_bias_vis = (data_source('RAW_BIAS_VIS')
                   .with_classification_rule(bias_vis_class)
                   .with_min_group_size(3)
                   .with_setup_keywords(setup1)
                   .with_grouping_keywords(setup1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=ONE_DAY, level=0)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=ONE_WEEK, level=1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=UNLIMITED, level=3)
                   .build())

   # Bias nir
   raw_bias_nir = (data_source('RAW_BIAS_NIR')
                   .with_classification_rule(bias_nir_class)
                   .with_min_group_size(3)
                   .with_setup_keywords(setup2)
                   .with_grouping_keywords(setup2)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=ONE_DAY, level=0)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=ONE_WEEK, level=1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=UNLIMITED, level=3)
                   .build())

   static_catalog = (data_source('catalog')
                     .with_classification_rule(static_catalog_class)
                     .with_match_keywords(['FILTER']).build())

   raw_flat_vis = (data_source('RAW_FLAT_VIS')
                   .with_classification_rule(flat_vis_class)
                   .with_min_group_size(3)
                   .with_setup_keywords(setup1)
                   .with_grouping_keywords(setup1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=ONE_DAY, level=0)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=ONE_WEEK, level=1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                        time_range=RelativeTimeRange(-365, 365), level=3)
                   .build())

   raw_flat_nir = (data_source('RAW_FLAT_NIR')
                   .with_classification_rule(flat_nir_class)
                   .with_min_group_size(3)
                   .with_setup_keywords(setup2)
                   .with_grouping_keywords(setup2)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=ONE_DAY, level=0)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=ONE_WEEK, level=1)
                   .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                        time_range=RelativeTimeRange(-365, 365), level=3)
                   .build())

   raw_science_vis = (data_source('RAW_SCIENCE_VIS')
                      .with_classification_rule(science_vis_class)
                      .with_grouping_keywords(['mjd-obs'])
                      .build())

   raw_science_nir = (data_source('RAW_SCIENCE_NIR')
                      .with_classification_rule(science_nir_class)
                      .with_grouping_keywords(['mjd-obs'])
                      .build())

   raw_sky_vis = (data_source('RAW_SKY_VIS')
                  .with_classification_rule(sky_vis_class)
                  .with_grouping_keywords(['mjd-obs'])
                  .with_match_keywords([kwd.instrume, kwd.arm,
                                        kwd.ins1_slit, kwd.tpl_start], level=0)
                  .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins1_slit],
                                       time_range=SAME_NIGHT, level=2)
                  .build())

   raw_sky_nir = (data_source('RAW_SKY_NIR')
                  .with_classification_rule(sky_nir_class)
                  .with_grouping_keywords(['mjd-obs'])
                  .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit,
                                        kwd.tpl_start], level=0)
                  .with_match_keywords([kwd.instrume, kwd.arm, kwd.ins2_slit],
                                       time_range=SAME_NIGHT, level=2)
                  .build())

demo2_classification.py
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo2_classification.py
   :linenos:

   from edps import classification_rule
   from . import demo2_keywords as kwd

   # Dictionaries with general keywords
   demo = {kwd.instrume: "DEMO"}
   vis  = {**demo, kwd.arm: "VIS"}
   nir  = {**demo, kwd.arm: "NIR"}

   # RAW FILES
   bias_vis_class = classification_rule('BIAS_VIS', {**vis, kwd.dpr_type: "BIAS"})
   bias_nir_class = classification_rule('BIAS_NIR', {**nir, kwd.dpr_type: "BIAS"})

   flat_vis_class = classification_rule('FLAT_VIS', {**vis, kwd.dpr_type: "FLAT"})
   flat_nir_class = classification_rule('FLAT_NIR', {**nir, kwd.dpr_type: "FLAT"})

   science_vis_class = classification_rule('SCIENCE_VIS', {**vis, kwd.dpr_type: "SCIENCE"})
   science_nir_class = classification_rule('SCIENCE_NIR', {**nir, kwd.dpr_type: "SCIENCE"})

   sky_vis_class = classification_rule('SKY', {**vis, kwd.dpr_type: "SKY"})
   sky_nir_class = classification_rule('SKY', {**nir, kwd.dpr_type: "SKY"})

   # MASTER CALIBRATIONS
   MASTERBIAS_VIS = classification_rule('MASTERBIAS_VIS', {**demo, kwd.pro_catg: 'MASTERBIAS_VIS'})
   MASTERBIAS_NIR = classification_rule('MASTERBIAS_NIR', {**demo, kwd.pro_catg: 'MASTERBIAS_NIR'})
   MASTERFLAT_VIS = classification_rule('MASTERFLAT_VIS', {**demo, kwd.pro_catg: 'MASTERFLAT_VIS'})
   MASTERFLAT_NIR = classification_rule('MASTERFLAT_NIR', {**demo, kwd.pro_catg: 'MASTERFLAT_NIR'})

   # STATIC CALIBRATIONS
   static_catalog_class = classification_rule('CATALOG', {**demo, kwd.pro_catg: 'CATALOG'})

.. warning::

   In the source manual, all four master-calibration rules above are printed with
   ``kwd.pro_catg: 'MASTERBIAS_VIS'`` — the same value copied four times. That is
   plainly a transcription slip in the original; the values have been corrected
   here to match each rule's own tag.

demo2_keywords.py
~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo2_keywords.py
   :linenos:

   # HEADER KEYWORDS USED FOR CLASSIFICATION, GROUPING, AND ASSOCIATION.
   instrume  = "instrume"
   arm       = "ARM"
   ins1_slit = "ins1.slit"
   ins2_slit = "ins2.slit"
   tpl_start = "tpl.start"
   mjd_obs   = "mjd-obs"
   dpr_type  = "dpr.type"
   pro_catg  = "pro.catg"


.. _demo3:

Simplified workflow: merged tasks
---------------------------------

This workflow represents a "simplification" of the pipeline and instrument
description. Similar classification rules (e.g. bias, flats) are combined into a
single data source, which is processed by a single task, regardless of the file
tag. Correct file association is carried on by **alternative and conditional
associations**.

Note that each box is a task, not a subworkflow with two tasks (one per ARM)
within it. It is the same layout as the basic ``demo0`` workflow, despite the
pipeline being different and differentiating between VIS and NIR categories. Note
that this solution is possible because both VIS and NIR observations are
processed with the same recipes.

.. code-block:: text
   :caption: The ``demo3_wkf`` layout — same shape as ``demo0``

   Raw Types
   ┌────────────────────────────────────────┐
   │ RAW_SCIENCE    RAW_FLAT    RAW_BIAS    │
   └──────┬────────────┬────────────┬───────┘
          │            │            ▼
          │            │        ( bias )
          │            ▼       ╱
          │        ( flat )◄──╯      Static Calibrations
          │            │             ┌────────────────────┐
          │            │             │ catalog   RAW_SKY  │
          ▼            ▼             └─────┬──────────┬───┘
        ─────────( science )◄──────────────┴──────────┘

demo3_wkf.py
~~~~~~~~~~~~

.. code-block:: python
   :caption: demo3_wkf.py
   :linenos:

   from edps import task, SCIENCE, alternative_association
   from .demo3_datasources import *
   from .demo3_task_functions import *
   from .demo3_rules import *

   bias_task = (task("bias")
                .with_recipe("run_bias")
                .with_main_input(raw_bias)
                .build())

   flat_task = (task("flat")
                .with_recipe("run_flat")
                .with_main_input(raw_flat)
                .with_associated_input(bias_task, [MASTERBIAS_VIS], condition=is_input_VIS,
                                       match_rules=attach_bias_and_flat_vis)
                .with_associated_input(bias_task, [MASTERBIAS_NIR], condition=is_input_NIR,
                                       match_rules=attach_bias_and_flat_nir)
                .with_dynamic_parameter("arm_used", which_observation_type)
                .build())

   alternative_sky = (alternative_association()
                      .with_associated_input(raw_sky, min_ret=0,
                                             condition=is_input_VIS, match_rules=attach_sky_vis)
                      .with_associated_input(raw_sky, min_ret=0,
                                             condition=is_input_NIR, match_rules=attach_sky_nir))

   science_task = (task("science")
                   .with_recipe("run_science")
                   .with_main_input(raw_science)
                   .with_alternative_associated_inputs(alternative_sky)
                   .with_associated_input(bias_task, [MASTERBIAS_VIS], condition=is_input_VIS,
                                          match_rules=attach_bias_and_flat_vis)
                   .with_associated_input(bias_task, [MASTERBIAS_NIR], condition=is_input_NIR,
                                          match_rules=attach_bias_and_flat_nir)
                   .with_associated_input(flat_task, [MASTERFLAT_VIS], condition=is_input_VIS,
                                          match_rules=attach_bias_and_flat_vis)
                   .with_associated_input(flat_task, [MASTERFLAT_NIR], condition=is_input_NIR,
                                          match_rules=attach_bias_and_flat_nir)
                   .with_associated_input(static_catalog)
                   .with_dynamic_parameter("arm_used", which_observation_type)
                   .with_meta_targets([SCIENCE])
                   .build())

demo3_datasources.py
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo3_datasources.py
   :linenos:

   from edps import data_source
   from .demo3_classification import *
   from . import demo2_keywords as kwd

   setup = [kwd.tpl_start, kwd.arm, kwd.ins1_slit, kwd.ins2_slit]
   # Grouping by tpl_start is sufficient under the assumption that
   # I do not have both VIS and NIR observations within the same
   # observing template.

   grouping = [kwd.tpl_start]

   # - Raw datasources
   raw_bias = (data_source('RAW_BIAS')
               .with_classification_rule(bias_vis_class)
               .with_classification_rule(bias_nir_class)
               .with_min_group_size(3)
               .with_setup_keywords(setup)
               .with_grouping_keywords(grouping)
               .build())

   raw_flat = (data_source('RAW_FLAT')
               .with_classification_rule(flat_vis_class)
               .with_classification_rule(flat_nir_class)
               .with_min_group_size(3)
               .with_setup_keywords(setup)
               .build())

   raw_science = (data_source('RAW_SCIENCE')
                  .with_classification_rule(science_vis_class)
                  .with_classification_rule(science_nir_class)
                  .with_grouping_keywords(['mjd-obs'])
                  .build())

   raw_sky = (data_source('RAW_SKY')
              .with_classification_rule(sky_vis_class)
              .with_classification_rule(sky_nir_class)
              .with_grouping_keywords(['mjd-obs'])
              .build())

   static_catalog = (data_source('catalog')
                     .with_classification_rule(static_catalog_class)
                     .with_match_keywords([kwd.arm]).build())

demo3_task_functions.py
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo3_task_functions.py
   :linenos:

   from edps import get_parameter, JobParameters, ClassifiedFitsFile, List

   # These functions return TRUE/FALSE depending on the value
   # of the parameter "arm_used"
   def is_input_NIR(params: JobParameters) -> bool:
       return get_parameter(params, "arm_used") == 'NIR'

   def is_input_VIS(params: JobParameters) -> bool:
       return get_parameter(params, "arm_used") == 'VIS'

   # This function determines the value of the parameter arm_used,
   # depending on the value of the header keyword "ARM"
   def which_observation_type(files: List[ClassifiedFitsFile]):
       # Note: files are only the main input files, not the associated files
       arm = files[0].get_keyword_value('ARM', None)
       return "NIR" if arm == "NIR" else "VIS" if arm == "VIS" else None

demo3_rules.py
~~~~~~~~~~~~~~

.. code-block:: python
   :caption: demo3_rules.py
   :linenos:

   from edps import match_rules, ONE_DAY, ONE_WEEK, UNLIMITED, SAME_NIGHT
   from . import demo3_keywords as kwd

   # CLASSIFICATION RULES
   # none

   # ASSOCIATION RULES
   #  - first, e.g. ref=trigger (e.g. science)
   #  - second, e.g. f=file to associate (e.g. calibration)
   # none

   # ASSOCIATION RULES THAT OVERRIDE THOSE SPECIFIED IN THE DATA_SOURCE

   setup_vis = [kwd.instrume, kwd.arm, kwd.ins1_slit]
   setup_nir = [kwd.instrume, kwd.arm, kwd.ins2_slit]

   # Definition of two different matching rules, one for VIS (needs to look at ins1.slit)
   # and one for NIR (needs to look for ins2.slit).

   attach_bias_and_flat_vis = (match_rules()
                               .with_match_keywords(setup_vis, time_range=ONE_DAY, level=0)
                               .with_match_keywords(setup_vis, time_range=ONE_WEEK, level=1)
                               .with_match_keywords(setup_vis, time_range=UNLIMITED, level=3))

   attach_bias_and_flat_nir = (match_rules()
                               .with_match_keywords(setup_nir, time_range=ONE_DAY, level=0)
                               .with_match_keywords(setup_nir, time_range=ONE_WEEK, level=1)
                               .with_match_keywords(setup_nir, time_range=UNLIMITED, level=3))

   attach_sky_vis = (match_rules()
                     .with_match_keywords(setup_vis + [kwd.tpl_start], level=0)
                     .with_match_keywords(setup_vis, time_range=SAME_NIGHT, level=1))

   attach_sky_nir = (match_rules()
                     .with_match_keywords(setup_nir + [kwd.tpl_start], level=0)
                     .with_match_keywords(setup_nir, time_range=SAME_NIGHT, level=1))

demo3_classification.py and demo3_keywords.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are identical in content to their ``demo2`` counterparts above: the same
per-arm classification rules and the same header keyword definitions. What
changed is not *how files are classified* but *how many datasources and tasks
consume those classifications*.


What made the compaction possible
---------------------------------

Comparing ``demo2`` and ``demo3``, the reduction in size comes from three
mechanisms working together:

**One datasource, several classification rules.**
   ``raw_bias`` carries both ``bias_vis_class`` and ``bias_nir_class``. Files
   from two different classifications are still never grouped together, so the
   VIS and NIR biases remain separate groups — but there is only one datasource
   to maintain.

**A dynamic parameter to recover the distinction.**
   ``.with_dynamic_parameter("arm_used", which_observation_type)`` reads ``ARM``
   from each job's main input. That single parameter is what the merged task uses
   to decide which arm it is currently processing.

**Conditional associations with per-arm match rules.**
   Each ``.with_associated_input(...)`` is guarded by ``condition=is_input_VIS``
   or ``condition=is_input_NIR`` and carries its own ``match_rules=`` overriding
   what the datasource declares. This is what lets one task match on
   ``ins1.slit`` for VIS jobs and ``ins2.slit`` for NIR jobs.

The result is 3 tasks and 5 datasources instead of 6 tasks (one in a
subworkflow) and 9 datasources — for the same reduction.
