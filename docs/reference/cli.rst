Command-line reference
======================

Full usage of the ``edps`` client, version 1.7.1:

.. code-block:: text

   usage: edps [-h] [-H HOST] [-P PORT] [-i [INPUTS ...]] [-t [TARGETS ...]]
               [-m [META_TARGETS ...]] [-w WORKFLOW] [-c] [-od] [-f] [-g] [-g2]
               [-a] [-r] [-x] [-d TASK] [-p [TASK [PARAMETER_SET ...]]] [-ps]
               [-wp PARAMETER VALUE] [-rp TASK PARAMETER VALUE]
               [-wps WORKFLOW_PARAMETER_SET] [-rps RECIPE_PARAMETER_SET] [-lt]
               [-lw] [-o OUTPUT_DIR] [-shutdown] [-rt {raw,reduced,all,none}]
               [-rj [REPORT_JOBS ...]]


Selecting what to run
---------------------

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - Option
     - Argument
     - Description
   * - ``-w``, ``--workflow``
     - ``WORKFLOW``
     - The workflow to use, e.g. ``"espresso.espresso_wkf"``. Required for
       almost everything.
   * - ``-i``, ``--inputs``
     - ``[INPUTS ...]``
     - Input files or directories. Directories are scanned recursively.
   * - ``-t``, ``--targets``
     - ``[TARGETS ...]``
     - Target task(s): reduce only up to these steps.
   * - ``-m``, ``--meta-targets``
     - ``[META_TARGETS ...]``
     - Meta-target(s), e.g. ``science``, ``qc1calib``. Defaults to
       ``science`` if neither ``-t`` nor ``-m`` is given.
   * - ``-o``, ``--output-dir``
     - ``OUTPUT_DIR``
     - Directory for the products of the target task(s).


Inspecting without reducing
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - Option
     - Argument
     - Description
   * - ``-c``, ``--classify``
     - —
     - Classify input files and print the result. Runs no recipes.
   * - ``-od``, ``--organize-data``
     - —
     - Run data organization only. Each job is shown independently, with more
       information but without highlighting the associations.
   * - ``-f``, ``--flat``
     - —
     - Produce flat organization output — datasets in a tree-like structure,
       showing the associations. JSON.
   * - ``-g``, ``--graph``
     - —
     - Print the workflow graph in DOT format. Pipe to ``dot``.
   * - ``-g2``, ``--detailed-graph``
     - —
     - Print the detailed workflow graph (tasks, subworkflows, input categories,
       recipes) in DOT format.
   * - ``-a``, ``--assocmap``
     - —
     - Print the association map in Markdown format. **Not in the source
       manual**; often the fastest way to diagnose an incomplete job.
   * - ``-x``, ``--expand-meta-targets``
     - —
     - Expand meta-targets into the list of tasks they cover. **Not in the
       source manual.**


Listing and introspection
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - Option
     - Argument
     - Description
   * - ``-lw``, ``--list-workflows``
     - —
     - Print the available workflows. The first thing to run when a workflow is
       "not found".
   * - ``-lt``, ``--list-targets``
     - —
     - Print the workflow targets and meta-targets.
   * - ``-p``, ``--recipe-parameters``
     - ``TASK [SET ...]``
     - Get the recipe parameters for a task, optionally for a named parameter
       set.
   * - ``-ps``, ``--parameter-sets``
     - —
     - Get all parameter sets.
   * - ``-d``, ``--default-parameters``
     - ``TASK``
     - Get the default parameters for a task. **Not in the source manual.**


Setting parameters
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 24 46

   * - Option
     - Argument
     - Description
   * - ``-rp``, ``--recipe-param``
     - ``TASK PARAMETER VALUE``
     - Set one recipe parameter. Repeatable. ``PARAMETER`` must be the full
       ``<instrument>.<recipe>.<alias>`` name.
   * - ``-wp``, ``--workflow-param``
     - ``PARAMETER VALUE``
     - Set one workflow parameter. Repeatable.
   * - ``-rps``, ``--recipe-parameter-set``
     - ``SET``
     - Use the recipe parameters from a named set.
   * - ``-wps``, ``--workflow-parameter-set``
     - ``SET``
     - Use the workflow parameters from a named set.

Command-line parameters take precedence over the parameter file, which in turn
takes precedence over values hard-coded in the workflow, which take precedence
over recipe defaults.


Reports
-------

.. list-table::
   :header-rows: 1
   :widths: 30 24 46

   * - Option
     - Argument
     - Description
   * - ``-rt``, ``--report-type``
     - ``raw``/``reduced``/``all``/``none``
     - Data type for graphical reports. Default: ``reduced``. **Not in the
       source manual.**
   * - ``-rj``, ``--report-jobs``
     - ``[JOB_IDS ...]``
     - Create graphical reports for the given job IDs. **Not in the source
       manual.**


Server control
--------------

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - Option
     - Argument
     - Description
   * - ``-shutdown``, ``--shutdown``
     - —
     - Shut down the EDPS server. Required after editing
       ``application.properties`` or any workflow file.
   * - ``-r``, ``--reset``
     - —
     - Reset the given workflow. **Not in the source manual.**
   * - ``-H``, ``--host``
     - ``HOST``
     - Server host. Default: ``localhost``.
   * - ``-P``, ``--port``
     - ``PORT``
     - Server port. Default: ``5000``.
   * - ``-h``, ``--help``
     - —
     - Show the help message and exit.


Recipes for common tasks
------------------------

.. code-block:: console

   # Full reduction, products into ./products
   $ edps -w espresso.espresso_wkf -i ./raw -o ./products

   # What does EDPS think my files are?
   $ edps -w espresso.espresso_wkf -i ./raw -c

   # How would it group and associate them? (no reduction)
   $ edps -w espresso.espresso_wkf -i ./raw -f > datasets.json

   # Which calibration got attached to what, and why?
   $ edps -w espresso.espresso_wkf -i ./raw -a > assoc.md

   # Calibrations only
   $ edps -w espresso.espresso_wkf -i ./raw -m qc1calib -o ./calibs

   # Stop after flat fielding
   $ edps -w espresso.espresso_wkf -i ./raw -t flat -o ./flats

   # Draw the workflow
   $ edps -w espresso.espresso_wkf -g | dot -Tpng > wkf.png

   # Change one recipe parameter
   $ edps -w espresso.espresso_wkf -i ./raw \
       -rp object espdr.espdr_sci_red.cosmic_detection_sw 1 -o ./products

   # Stop the server (do this after editing config or workflows)
   $ edps -shutdown
