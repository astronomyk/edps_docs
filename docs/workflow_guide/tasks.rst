Tasks
=====

Tasks are the **processing units** of the reduction process. Each task, if
complete, generates a number of **jobs**, each of them running the same pipeline
recipe (or Python function) on different groups of data.

To be defined, a task needs just the main input. Other things such as associated
inputs (e.g. calibrations), recipe to be executed, alternative inputs, and
conditions can be added depending on the data reduction requirements.

The **main input** is passed with the method ``.with_main_input()``. A task
accepts only one main input, that can be either a datasource or another task.

Inputs other than the main input are passed with the method
``.with_associated_input()``. Several associated inputs can be specified. An
associated input can be either a datasource or a task.

An example of a task is:

.. code-block:: python
   :linenos:

   science_task = (task("science")
                   .with_recipe("run_science")
                   .with_main_input(raw_science)
                   .with_associated_input(bias_task, [MASTERBIAS_class])
                   .build())

In the example above, the task gets its main inputs from the ``raw_science``
data source, and attaches bias calibrations (either the result of the ``bias``
task that processed raw bias calibrations, or master calibrations already
present on disk). The task creates as many jobs as groups of files to be
processed and reduces them with the ``run_science`` recipe.

Calibrations (i.e. bias frames in this example) are associated to the
``raw_science`` following association rules attached to the main input of the
bias task. See :doc:`classification`.

The task above generates as many jobs as science files. **Incomplete jobs**
(e.g. science files that are missing the corresponding bias frames) are marked
as incomplete and not executed.


Optional inputs
---------------

One can specify the minimum and maximum number of associated inputs of a certain
type, using ``min_ret`` (default = 1) and ``max_ret`` (default = 1). Optional
inputs of the task are specified by setting ``min_ret=0``:

.. code-block:: python
   :linenos:

   science_task = (task("object")
                   .with_main_input(raw_science)
                   .with_associated_input(bias_task, [MASTERBIAS_class], min_ret=0)
                   ....)

The ``min_ret`` and ``max_ret`` specified in the task refer to the **associated
input**: number of jobs to associate, or number of master calibrations to
associate — *not* the number of raw files used in the associated job. Those are
specified in the data source (see :ref:`min-group-size`).

``min_ret`` and ``max_ret`` apply to all master calibrations and jobs specified
in the associated input. For example:

.. code-block:: python

   .with_associated_input(bias_task, [MASTERBIAS, BADPIXEL_MASK], min_ret=2)

asks for at least 2 bias jobs, or for at least 2 ``MASTERBIAS`` and 2
``BADPIXEL_MASK`` frames.

.. note::

   It is not possible to specify a different ``min_ret``/``max_ret`` for jobs and
   master calibrations. If you need a mandatory and an optional product from the
   same task, use alternatives — see :ref:`optional-mandatory-products`.

.. note::

   Associated inputs can be associated on the basis of a **condition** (a.k.a.
   conditional associations), which might depend on the properties of the data
   themselves or some parameters defined in the workflow. See
   :ref:`conditional-association`.


.. _metatargets:

Targets and metatargets
-----------------------

One of the core features of EDPS is the concept of processing **target(s)**,
which can be used to restrict the processing to a subset of the workflow tasks.
In this context "target" is synonym for "task" and can be referred to using the
task name defined in the workflow.

It is also possible to attach one or more **metatargets** to a task. A
metatarget is a label that can be used to refer to a group of related tasks (for
example all calibration tasks or all science tasks) instead of specifying them
individually.

EDPS has the following pre-defined metatargets:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Metatarget
     - Meaning
   * - ``qc1calib``
     - Tasks used to create master calibrations or instrument monitoring.
   * - ``qc0``
     - Tasks that are meant to be run as a quick look at the telescope (QC0
       process).
   * - ``science``
     - Tasks responsible for scientific reduction.
   * - ``calchecker``
     - Tasks that require monitoring of the needed calibrations (typically
       instrument monitoring, processing scientific and standard star
       exposures).

Example:

.. code-block:: python
   :linenos:

   bias = (task("bias")
           .with_recipe("run_bias")
           .with_main_input(raw_bias)
           .with_meta_targets([qc1_calib, qc0])
           .build())

.. note::

   Despite the metatarget not being mandatory to define a workflow, it **is** a
   mandatory element for the QCFlow and CalChecker applications.

.. admonition:: Verified against EDPS 1.7.1
   :class: tip

   The importable metatarget names in EDPS 1.7.1 are ``qc0``, ``qc1calib``,
   ``qc1science``, ``science``, ``calchecker``, ``idp`` and ``phase3``, with
   upper-case aliases ``QC0``, ``QC1_CALIB``, ``QC1_SCIENCE``, ``SCIENCE``,
   ``CALCHECKER``, ``IDP`` and ``ALL``. The source manual lists only the first
   four; ``qc1science``, ``idp`` and ``phase3`` were added later. Note that the
   example above uses ``qc1_calib`` — the importable lower-case name is
   ``qc1calib``.


Filtering inputs and outputs
----------------------------

Filtering the inputs of a task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default all products of an associated task are passed to the recipe of the
task.

It is possible to filter the inputs of a task using the method
``.with_input_filter()``. The filter accepts a list of classification rules. The
list can be a **white list** (only classification rules specified in the list
are written into the recipe input set of files) or a **black list** (all inputs
are written to the set of files, but those specified in the filter list). These
modes can be specified by adding ``mode="SELECT"`` (default) or
``mode="REJECT"`` to the statement.

.. note::

   The filter is applied at the moment of writing the recipe input set of files.
   The associations are still displayed in the job and they still determine
   whether a job is considered complete or not.

Example:

.. code-block:: python
   :linenos:

   bias_task    = (task("bias")
                   .with_recipe("run_bias")
                   .with_main_input(raw_bias)
                   .build())

   science_task = (task("object")
                   .with_recipe("run_science")
                   .with_main_input(raw_science)
                   .with_associated_input(bias_task, [MASTERBIAS_class])
                   .with_input_filter(MASTERBIAS_class, mode="SELECT")
                   .build())

In the example above, the task ``bias`` is associated to the task ``science``.
The task ``bias`` triggers the reduction of ``raw_bias`` frames with the recipe
``run_bias``. All the products of the bias recipe are passed to the science
task, but only those listed in ``.with_input_filter`` are written into the
recipe input set of files. In the above example, assuming the bias recipe
creates a masterbias and a badpixelmask, the masterbias is passed while the
badpixelmask is not.

Filtering the outputs of a task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similarly to the input filter, one can filter the outputs of a task. The method
is called ``.with_output_filter()`` and accepts as input a list of classification
rules. If one sets ``mode="SELECT"`` (default) then the listed products are
passed to all the tasks that have this task as input. If one sets
``mode="REJECT"``, then the listed products are never passed to subsequent tasks
(but they are saved on disk).

Example:

.. code-block:: python
   :linenos:

   bias    = (task("bias")
              .with_recipe("run_bias")
              .with_main_input(raw_bias)
              .with_output_filter(OVERSCAN_class, mode="REJECT")
              .build())

   flat    = (task("flat")
              .with_recipe("run_flat")
              .with_main_input(raw_flats)
              .with_associated_input(bias, [MASTERBIAS_class])
              .build())

   science = (task("object")
              .with_recipe("run_science")
              .with_main_input(raw_science)
              .with_associated_input(bias, [MASTERBIAS_class, BPMASK_class])
              .build())

In the example above, all the products of the task ``bias`` are passed to the
tasks ``flat`` and ``object``, except the one defined by the classification rule
``OVERSCAN_class``.

.. important::

   If the association preference is set to associate **master calibrations**
   rather than tasks (see :ref:`raw-or-master`), then the task ``flat`` will get
   only the ``MASTERBIAS``, and the task ``science`` will get ``MASTERBIAS`` and
   ``BPMASK`` calibrations.


Convention on the order of task methods
---------------------------------------

The adopted convention is to define the methods in the task with the following
order:

1. recipe
2. call for "ADARI" reports
3. main input
4. associated inputs (follow the calibration cascade)
5. execution condition
6. dynamic parameters
7. job functions
8. input and output filters
9. mapping categories
10. meta targets

Following this consistently across workflows makes them far easier to diff and
review.
