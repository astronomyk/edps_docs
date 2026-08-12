Workflow examples
=================

Two complete worked examples, both for a hypothetical instrument called
``DEMO``. They are best read in order: the first establishes the full set of
files a workflow needs, the second shows how to keep that structure from growing
out of hand as the pipeline gets more complicated.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Example
     - What it demonstrates
   * - :doc:`simple`
     - A complete workflow (``demo1``) with all seven files: tasks, data
       sources, classification, rules, keywords, task functions and parameters.
       Introduces conditional associations and a static catalogue that is
       attached only if the user asks for photometric calibration.
   * - :doc:`compact`
     - The same reduction cascade for a pipeline that distinguishes VIS and NIR
       arms. First the straightforward translation (``demo2``, one task per
       tag, with a subworkflow), then the compacted design (``demo3``) that
       merges tasks and classification rules using conditional associations and
       a dynamic parameter.

.. tip::

   The general rule is to keep a workflow **as simple as possible**, minimising
   the number of tasks and datasources wherever possible. ``demo3`` is the
   design to imitate.

.. toctree::
   :maxdepth: 2

   simple
   compact
