Workflow builder API
====================

The methods available on the ``task`` and ``data_source`` builders, and the
constants importable from ``edps``, as of EDPS 1.7.1.

.. note::

   The EDPS source code carries almost no docstrings, so the descriptions below
   are drawn from the workflow design manual and from observed usage in the ESO
   workflows. Method *names and existence* are verified against the installed
   package; the descriptions are not authoritative where the manual is silent.


``task(name)`` builder methods
------------------------------

Core
~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``.with_main_input(source)``
     - The single main input — a datasource or another task. Required.
   * - ``.with_associated_input(source, [rules], min_ret=1, max_ret=1, condition=..., match_rules=...)``
     - Attach a calibration or other secondary input. Repeatable.
   * - ``.with_recipe(name)``
     - The pipeline recipe this task runs.
   * - ``.with_function(fn)``
     - Run a Python function instead of a recipe. See :doc:`../workflow_guide/functions`.
   * - ``.with_shell_command(...)``
     - Run a shell command. *Undocumented in the manuals.*
   * - ``.build()``
     - Finalise. Every task definition ends with this.

Structure and grouping
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``.with_alternatives(alt)``
     - Attach an ``alternative_associated_inputs`` object.
   * - ``.with_alternative_associated_inputs(alt)``
     - Same, longer spelling; both appear in ESO workflows.
   * - ``.with_meta_targets([...])``
     - Attach metatargets. See :ref:`metatargets`.
   * - ``.with_condition(fn)``
     - Execute the task only if ``fn(params)`` is True.
   * - ``.with_dynamic_parameter(name, fn)``
     - Compute a parameter from the job's main input files.
   * - ``.with_job_processing(fn)``
     - Modify job properties at run time.
   * - ``.with_min_group_size(n)``
     - Minimum files in a group.
   * - ``.with_grouping_keywords([...])``
     - Group the main input by these header keywords.
   * - ``.with_grouping_function(fn)`` / ``.with_custom_grouping(...)``
     - Custom grouping. *Undocumented in the manuals.*
   * - ``.with_cluster(key, min, max)``
     - Cluster files by closeness of a parameter.
   * - ``.with_subworkflow_name(name)``
     - Assign the task to a named subworkflow.

Filtering and tagging
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``.with_input_filter(rules, mode="SELECT"|"REJECT")``
     - Filter what gets written into the recipe sof.
   * - ``.with_output_filter(rules, mode="SELECT"|"REJECT")``
     - Filter what gets passed to downstream tasks.
   * - ``.with_input_map({OLD: NEW})``
     - Rename input category tags in the sof.
   * - ``.with_report(...)``
     - Attach an ADARI report. *Undocumented in the manuals.*
   * - ``.with_description(text)``
     - Human-readable description. *Undocumented in the manuals.*


``data_source(name)`` builder methods
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``.with_classification_rule(rule)``
     - Which files belong to this datasource. Repeatable — several rules mean
       several groups, never mixed.
   * - ``.with_grouping_keywords([...])``
     - Header keywords by which files are grouped into jobs.
   * - ``.with_cluster(key, min, max)``
     - Cluster by closeness of a parameter, e.g. ``'SKY.POSITION'``.
   * - ``.with_grouping_function(fn)`` / ``.with_custom_grouping(...)``
     - Custom grouping. *Undocumented in the manuals.*
   * - ``.with_min_group_size(n)``
     - Minimum number of files for the group to be considered. Only effective
       when the datasource is a **main** input.
   * - ``.with_setup_keywords([...])``
     - Keywords describing the instrument setup; used by QCFlow for scoring.
       Required for datasources that are main inputs.
   * - ``.with_match_keywords([...], time_range=..., level=...)``
     - Simple association rule. Repeatable, one per quality level.
   * - ``.with_match_function(fn, time_range=..., level=...)``
     - Complex association rule, ``fn(ref, f)``.
   * - ``.with_match_rules(rules)``
     - Attach a prebuilt ``match_rules`` object.
   * - ``.with_subworkflow_name(name)``
     - Assign to a named subworkflow.
   * - ``.build()``
     - Finalise.

.. warning::

   There is **no** ``.with_group_keywords()`` and **no**
   ``.with_max_group_size()``, despite both appearing in the source manual. Use
   ``.with_grouping_keywords()``; for an upper bound, group on a unique keyword
   such as ``arcfile`` or ``mjd-obs``.


Predefined validity ranges
--------------------------

Importable from ``edps`` directly or from ``edps.generator.time_range``.

.. list-table::
   :header-rows: 1
   :widths: 30 24 46

   * - Constant
     - Range (days)
     - Equivalent
   * - ``ONE_AND_HALF_HOURS``
     - −0.0625, +0.0625
     - ``RelativeTimeRange(-0.0625, 0.0625)``
   * - ``SAME_NIGHT``
     - −0.4, +0.4
     - ``RelativeTimeRange(-0.4, 0.4)``
   * - ``NEXT_DAY``
     - 0, +1
     - ``RelativeTimeRange(0, 1)``
   * - ``ONE_DAY``
     - −1, +1
     - ``RelativeTimeRange(-1, 1)``
   * - ``TWO_DAYS``
     - −2, +2
     - ``RelativeTimeRange(-2, 2)``
   * - ``THREE_DAYS``
     - −3, +3
     - ``RelativeTimeRange(-3, 3)``
   * - ``FOUR_DAYS``
     - −4, +4
     - ``RelativeTimeRange(-4, 4)``
   * - ``FIVE_DAYS``
     - −5, +5
     - ``RelativeTimeRange(-5, 5)``
   * - ``ONE_WEEK``
     - −7, +7
     - ``RelativeTimeRange(-7, 7)``
   * - ``TWO_WEEKS``
     - −14, +14
     - ``RelativeTimeRange(-14, 14)``
   * - ``THREE_WEEKS``
     - −21, +21
     - ``RelativeTimeRange(-21, 21)``
   * - ``ONE_MONTH``
     - −30, +30
     - ``RelativeTimeRange(-30, 30)``
   * - ``QUARTERLY``
     - −90, +90
     - ``RelativeTimeRange(-90, 90)``
   * - ``IN_THE_PAST``
     - −∞, 0
     - ``RelativeTimeRange(NEGATIVE_INF, 0)``
   * - ``UNLIMITED``
     - −∞, +∞
     - ``RelativeTimeRange(NEGATIVE_INF, INF)``

For anything else, construct one directly: ``RelativeTimeRange(-365, 365)``.


Metatargets
-----------

.. list-table::
   :header-rows: 1
   :widths: 22 20 58

   * - Lower-case
     - Upper-case
     - Meaning
   * - ``qc1calib``
     - ``QC1_CALIB``
     - Tasks creating master calibrations or instrument monitoring.
   * - ``qc1science``
     - ``QC1_SCIENCE``
     - Science-side QC1 tasks. *Not in the source manual.*
   * - ``qc0``
     - ``QC0``
     - Quick-look tasks run at the telescope.
   * - ``science``
     - ``SCIENCE``
     - Scientific reduction. The default target if none is given.
   * - ``calchecker``
     - ``CALCHECKER``
     - Tasks requiring monitoring of the needed calibrations.
   * - ``idp``
     - ``IDP``
     - Internal Data Product tasks. *Not in the source manual.*
   * - ``phase3``
     - —
     - Phase 3 delivery tasks. *Not in the source manual.*
   * - —
     - ``ALL``
     - All tasks. *Not in the source manual.*


Other importable names
----------------------

Frequently used in workflow files:

``classification_rule``, ``data_source``, ``task``, ``subworkflow``,
``match_rules``, ``alternative_associated_inputs``,
``alternative_association``, ``associated_input``, ``get_parameter``,
``RelativeTimeRange``

Type annotations used in task functions:

``Job``, ``JobParameters``, ``ClassifiedFitsFile``, ``File``, ``FitsFile``,
``List``, ``RecipeInputs``, ``RecipeInvocationArguments``,
``RecipeInvocationResult``, ``InvokerProvider``, ``ProductRenamer``
