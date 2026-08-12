Classifications and associations
================================

Classification rules
--------------------

Classification rules are the backbone of the file classification process. Data
sources contain files that satisfy one or more classification rule. The default
classification rule contains two elements:

* A **string** with the tag the recipe processing the file expects.
* A **dictionary** listing the keywords and their values the file must have to
  fulfil that rule; or the name of a **function** that contains the conditions
  the file must fulfil. [#f1]_ Dictionaries are expected for "simple"
  classification rules, where the keywords must simply match some values.
  Functions are needed for more complicated relations.

.. rubric:: Footnotes

.. [#f1] If this second item is not provided, then the tag is expected to be also
   the ``PRO.CATG`` of the file itself.

Example of "simple" classification rules:

.. code-block:: python
   :linenos:

   from edps import classification_rule
   from . import espresso_keywords as kwd

   # Dictionaries containing the values of header keywords that define
   # calibrations and science data
   espresso         = {kwd.instrume: "ESPRESSO"}
   calib_keywords   = {**espresso, kwd.dpr_catg: "CALIB"}
   science_keywords = {**espresso, kwd.dpr_catg: "SCIENCE"}

   bias_class         = classification_rule("BIAS", {**calib_keywords,
                            kwd.dpr_type: "BIAS"})
   dark_class         = classification_rule("DARK", {**calib_keywords,
                            kwd.dpr_type: "DARK"})
   science_fp_class   = classification_rule('OBJ_FP', {**science_keywords,
                            kwd.dpr_type: "OBJECT,FP"})
   science_thar_class = classification_rule("OBJ_THAR", {**science_keywords,
                            kwd.dpr_type: "OBJECT,THAR"})

where ``instrume``, ``dpr_type``, and ``dpr_catg`` are defined in the keywords
file. It is recommended to use nested dictionaries and keep the condition of
``DPR.TYPE`` at the end.

Example of a "complex" classification rule:

.. code-block:: python
   :linenos:

   from edps import classification_rule
   from . import kmos_rules as rules
   reduced_class = classification_rule("SINGLE_CUBES", rules.is_single_cubes)

where ``is_single_cubes`` is a function expressing the conditions the file must
fulfil to be classified as ``"SINGLE_CUBES"``. It is described in
:ref:`rules-file`.

.. note::

   Two other functions ``ClassificationRule`` and ``ProductClassificationRule``
   are available, but their use-cases have been incorporated in the more generic
   ``classification_rule`` function.


How to associate calibrations
-----------------------------

Data sources or tasks are associated to a task by the so-called **association
rules**.

* In the case of **data sources**, the association rules are defined in the data
  source.
* In the case of **tasks**, the task inherits the association rule of the first
  main input up the reduction cascade, task by task, until the first data source
  is reached.

The rules attached to the data source can be overridden by rules attached to the
``.with_associated_input()`` method in the task (see
:ref:`same-datasource-different-rules`).

Association can be done in two ways:

* Using the ``.with_match_keywords()`` method. Here, one provides a list of
  keywords that the files must match ("simple" association).
* Using the ``.with_match_function()`` method. Here, one provides a function the
  files must obey ("complex" association).

Below, we show an example of "simple" association with the
``.with_match_keywords()`` method.

.. code-block:: python
   :linenos:

   from . import instrument_keywords as kwd

   raw_standard = (data_source('RAW_STANDARD')
                   .with_classification_rule(standard_class)
                   .with_grouping_keywords([kwd.tpl_start])
                   .with_match_keywords([kwd.det_id])
                   .build())

   standard = (task('STANDARD')
               .with_recipe('run_standard')
               .with_main_input(raw_standard)
               .build())

   science  = (task('SCIENCE')
               .with_recipe('run_science')
               .with_main_input(raw_science)
               .with_associated_input(standard, ['RESPONSE'])
               .build())

Where ``kwd.tpl_start`` and ``kwd.det_id`` are variables imported from the
keyword file ``instrument_keywords.py``; their values are ``"tpl.start"`` and
``"det.id"`` respectively.

In the case the association is done by other operations than a pure match, the
method ``.with_match_function()`` ("complex" associations) has to be used (see
:ref:`rules-file`).


.. _association-levels:

Multiple association levels and validity ranges
-----------------------------------------------

Associations can have multiple **quality levels**, depending on several factors,
the most common of which is the time range during which a calibration ensures a
product of a certain quality.

Therefore, data sources can have several ``.with_match_keywords`` and
``.with_match_function`` statements. The convention is to assign each statement a
different level (number) with the following meaning:

.. code-block:: python

   # Convention for Data sources Association rule levels:
   # Each data source can have several match function which correspond to
   # different quality levels for the selected data.
   # The level is specified as a number that follows this convention:
   #   level < 0: more restrictive than the calibration plan
   #   level = 0  follows the calibration plan
   #   level = 1  quality sufficient for QC1 certification
   #   level = 2  probably still acceptable quality
   #   level = 3  significant risk of bad quality results

Therefore, when writing the matching rules, it is fundamental to set it to the
appropriate quality level, so that one knows what is the expected quality of the
products. It is not mandatory to define a match rule for each level. Different
levels can have different rules and/or different validity ranges.


.. _raw-or-master:

Raw calibrations or master calibrations?
----------------------------------------

The order by which the calibration is searched and its type (raw or master)
depends on the order of the matching rules within the data source and on the
preference expressed in the parameter ``association_preference`` of the
``application.properties`` configuration file.

For example, let's consider the following example of data source:

.. code-block:: python
   :linenos:

   match_kwd = ['instrume', 'ins.mode']
   calibration = (data_source("CALIBRATION")
                  .with_classification_rule(calibration_class)
                  .with_match_keywords(match_kwd, time_range=SAME_NIGHT, level=-1)
                  .with_match_keywords(match_kwd, time_range=TWO_DAYS, level=0)
                  .with_match_keywords(match_kwd, time_range=ONE_DAY, level=-1)
                  .with_match_keywords(match_kwd, time_range=UNLIMITED, level=3))

The definition of time ranges is given in :ref:`validity-ranges`.

If the ``application.properties`` configuration file has:

``association_preference = RAW``
   First, the system will check if there are raw calibrations matching the first
   association rule. If found, they are associated with quality level flag =
   -1. If not found, raw calibrations matching the second association level
   level are searched (level = 0). If not found, the next level is searched
   until the last. If no raw calibrations are found for none of the levels, then
   master calibrations matching the first rule. If none are found, the second
   level is searched, and so forth. If no calibrations are found, the association
   is not done.

``association_preference = MASTER``
   Same as ``RAW``, but first master calibrations are looked for all the
   association levels. Then, if master calibrations are not found, the system
   looks for raw calibrations.

``association_preference = RAW_PER_LEVEL``
   First, the system will check if there are raw calibrations matching the first
   association rule. If not found, MASTER calibrations matching the first rule
   are searched. If not found, RAW calibrations matching the second rule are
   searched, if not found MASTER calibrations matching the second rule are
   searched. The sequence goes on until the last rule.

``association_preference = MASTER_PER_LEVEL``
   First, the system will check if there are MASTER calibrations matching the
   first association rule. If not found, RAW calibrations matching the first
   association rule are searched. If not found, MASTER calibrations matching the
   second rule are searched, if not found RAW calibrations matching the second
   rule are searched. The sequence goes on until the last rule.

.. note::

   The setting names accepted by EDPS 1.7.1 are the lower-case forms ``raw``,
   ``master``, ``raw_per_quality_level`` and ``master_per_quality_level``. The
   workflow-design manual uses the shorter names ``RAW_PER_LEVEL`` /
   ``MASTER_PER_LEVEL``; these describe the same four strategies. See
   :doc:`../user_guide/configuration` for the user-facing description.


.. _validity-ranges:

Definition of validity ranges for associations
----------------------------------------------

Time ranges are defined with the ``RelativeTimeRange(-M, N)`` function. The
function considers a time range included between :math:`-N` days and :math:`+M`
days around the file that needs the association. :math:`M` and :math:`N` are
real numbers.

The following time ranges are pre-defined in EDPS:

.. code-block:: python
   :linenos:

   ONE_AND_HALF_HOURS = RelativeTimeRange(-0.0625, 0.0625)
   SAME_NIGHT   = RelativeTimeRange(-0.4, 0.4)
   NEXT_DAY     = RelativeTimeRange(0, 1)
   ONE_DAY      = RelativeTimeRange(-1, 1)
   TWO_DAYS     = RelativeTimeRange(-2, 2)
   THREE_DAYS   = RelativeTimeRange(-3, 3)
   FOUR_DAYS    = RelativeTimeRange(-4, 4)
   FIVE_DAYS    = RelativeTimeRange(-5, 5)
   ONE_WEEK     = RelativeTimeRange(-7, 7)
   TWO_WEEKS    = RelativeTimeRange(-14, 14)
   THREE_WEEKS  = RelativeTimeRange(-21, 21)
   ONE_MONTH    = RelativeTimeRange(-30, 30)
   QUARTERLY    = RelativeTimeRange(-90, 90)
   IN_THE_PAST  = RelativeTimeRange(NEGATIVE_INF, 0)
   UNLIMITED    = RelativeTimeRange(NEGATIVE_INF, INF)

The above values must be imported in the ``instrument_datasource.py`` file, e.g.:

.. code-block:: python

   from edps.generator.time_range import *

.. admonition:: Verified against EDPS 1.7.1
   :class: tip

   All fifteen ranges above exist with exactly these bounds in EDPS 1.7.1, and
   are also importable directly from the top-level ``edps`` package.


.. _rules-file:

The rules file: complex classifications and associations
--------------------------------------------------------

This file contains the functions used for "complex" classification and
association rules. The convention is to start with the classification rules,
followed by the association rules.

An example of "complex" classification rule is:

.. code-block:: python
   :caption: example_classification.py
   :linenos:

   from . import kmos_rules as rules
   reduced_class = classification_rule("SINGLE_CUBES", rules.is_single_cubes)

.. code-block:: python
   :caption: example_rules.py
   :linenos:

   def is_kmos(f):
       return f[kwd.instrume] == "KMOS"

   def is_sci_reconstructed(f):
       return is_kmos(f) and (f[kwd.pro_catg] == "SCI_RECONSTRUCTED" or
                              f[kwd.pro_catg] == "SINGLE_CUBES")

   def is_single_cubes(f):
       return is_sci_reconstructed(f) and f[kwd.tpl_id] != "KMOS_spec_acq"

It is recommended to use **nested functions**.

An example of "complex" association rule is:

.. code-block:: python
   :linenos:

   # Data source in the data source file:
   raw_standard = (data_source('RAW_STANDARD')
                   .with_classification_rule(standard_class)
                   .with_grouping_keywords(['tpl.start'])
                   .with_match_function(match_standard_science)
                   .build())

   # Association rule in the instrument_rules.py file
   def match_standard_science(ref, f):
       return f['det.id'] == ref['det.id'] and \
           abs(f['airmass'] - ref['airmass']) <= 0.1

In the above example, the standard star is associated if it has the same
``det.id`` and airmass difference not more than 0.1 than the main input of the
task requiring the standard star.

.. admonition:: The argument convention matters
   :class: important

   The first input of the function, ``ref``, is the **trigger**, i.e. the file
   requesting the calibration. The second input, ``f``, is the **file to
   associate**, i.e. the calibration.

   It is advisable to write the following comment into the rules file, right
   before the start of association functions:

   .. code-block:: python

      # ASSOCIATION RULES
      #  - first input, e.g. ref=trigger (e.g. science)
      #  - second input, e.g. f=file to associate (e.g. calibration)
