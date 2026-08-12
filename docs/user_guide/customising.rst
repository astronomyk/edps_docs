Customising the data reduction
==============================

Each step of the reduction cascade is organised in the so-called **tasks**. In
other words, a task represents a step in the data reduction. Each task is
defined by input files and the recipe to execute.

It is possible to define the reduction cascade up to a certain step, by
selecting the *target task*, or a *meta-target* (i.e. a defined group of
tasks), so that the data reduction stops at a certain point.

To display the tasks for a certain workflow type:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -lt

The output list shows the tasks grouped by meta-target. While a task can run
only one recipe, a recipe can be associated to many tasks.

In order to execute the reduction up to a certain step, indicate the target
task:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -t <TASK>

or a meta-target (this will select multiple target tasks, i.e. those that are
within the same meta-target group):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -m <meta-target>

More information in :ref:`inspect-cascade`.


Recipe parameters
-----------------

To process data with a specific value for a parameter, which is executed by a
recipe of a given task, type on a terminal where the ``edps`` Python
environment is active (single-line command):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directories> -rp <TASK> <PARAMETER> <VALUE> -o <output_directory>

where:

``TASK``
   the task name that runs the recipe we want to change the parameter for;

``PARAMETER``
   the parameter name. This **must give the full name**, which includes the
   instrument name and the recipe name — see :ref:`display-parameters` on how
   to display the available recipe parameters;

``VALUE``
   the value we want to use.

For example, the command (single line):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directories> \
       -rp object espdr.espdr_sci_red.cosmic_detection_sw 1 \
       -o <output_directory>

instructs the task ``object`` to activate the Laplacian Cosmic Ray detection
algorithm when running the recipe ``espdr_sci_red``.

To change more than one parameter, just add other ``-rp`` lines to the example
above. If many parameters have to be configured, it might be convenient to load
them from a configuration file (see :ref:`parameter-config-file`).

For a given instrument workflow, the full list of options is described in the
corresponding pipeline manuals and data reduction tutorials.

.. admonition:: Precedence
   :class: important

   Recipe parameters defined through the command line as above **override**:

   * default recipe values;
   * configuration files with specified values;
   * values that are hard-coded or configured automatically by the workflow
     (e.g. that depend on input data).


Workflow parameters
-------------------

Some instrument workflows can reduce the data in different ways, depending on
the science needs. Certain steps of the reduction can be avoided or executed
instead of others, or some calibrations can be ignored despite being present in
the input data directory.

Some of the data reduction strategies are **hard-coded** in the workflow, in the
sense that the data reduction cascade depends on the properties of the data we
want to process. On the other hand, some other strategies can be controlled by
so-called **workflow parameters**. In other words, workflow parameters are not
directly associated to the recipes but they define the strategy of the data
reduction and the reduction chain.

In the case of ESPRESSO, there is only one reduction strategy and no workflow
parameters are available. In the case of the KMOS workflow, the following
workflow parameters are available:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Values
   * - ``molecfit``
     - ``'standard'`` (default), ``'science'``, ``'false'``
   * - ``use_sky_flats``
     - ``'false'`` (default), ``'true'``
   * - ``qc0``
     - ``'false'`` (default), ``'true'``

For example, to use the sky flats for illumination correction instead of using
the lamp flats as default strategy, type (single-line command):

.. code-block:: console

   $ edps -w kmos.kmos_wkf -i <input_directories> -wp use_sky_flats 'true' -o <output_directory>

To specify more workflow parameters, add as many ``-wp`` lines as needed. If a
large number of workflow parameters have to be specified, it might be convenient
to load them from a configuration file (see :ref:`parameter-config-file`).

.. admonition:: Precedence
   :class: important

   Workflow parameters defined through the command line as above **override**:

   * values defined in configuration files;
   * values that are hard-coded or configured automatically by the workflow
     (e.g. that depend on input data).


.. _display-parameters:

Displaying default parameter values
-----------------------------------

To display what the recipe parameter full names and their values are, for the
task ``object`` used in the default parameter set (note: the ESPRESSO pipeline
must be installed):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -p object

In the case there are several parameter sets, add the name of the set for which
you would like to see the parameters. In the ESPRESSO workflow there is only one
parameter set. But in the case of KMOS, one can show the information for the
parameter set ``qc0_parameters``, which is not the default one:

.. code-block:: console

   $ edps -w kmos.kmos_wkf -p object qc0_parameters

In general, to display simultaneously the information for all the parameter
sets, type:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -ps


Using a specific parameter set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each workflow can have different sets of parameters. There are two types of
parameters: workflow parameters and recipe parameters. In the case of KMOS,
there is a non-default parameter set named ``qc0_parameters``.

To use the **workflow** parameters from that set:

.. code-block:: console

   $ edps -w kmos.kmos_wkf -wps qc0_parameters

To use the **recipe** parameters from that set:

.. code-block:: console

   $ edps -w kmos.kmos_wkf -rps qc0_parameters

To use **both** the workflow and recipe parameters from that set:

.. code-block:: console

   $ edps -w kmos.kmos_wkf -wps qc0_parameters -rps qc0_parameters


.. _parameter-config-file:

Configuration file for recipe and workflow parameters
-----------------------------------------------------

Each workflow comes with a configuration file that contains recipe and workflow
parameters. The recipe parameters are organised by task (indeed, several tasks
can run the same recipe and might require different parameter values). If a
recipe parameter is not listed, then the pipeline default is used. Each
parameter file can contain more than one parameter set, therefore the users can
define the set with the parameters that are most suited for their reduction.

The configuration file is in YAML format, therefore it must follow some
conventions. Please use the default configuration file as starting point to
create new ones. General rules to keep in mind are:

* Booleans have to be indicated as strings (e.g. ``"FALSE"``, ``"TRUE"``).

* Values have to be specified via colon, not via equality. E.g.:

  .. code-block:: yaml

     espresso.espdr_sci_red.cosmic_detection_sw: 2

* Recipe parameters have to be specified by their full name, which follows the
  convention ``<instrument>.<recipe>.<alias>``.

Note that the direct specification of a parameter value in the ``edps`` command
overrides the values defined in the parameter file.

.. seealso::

   The full structure of a parameter file, including how parameter sets and
   defaults are declared, is described in
   :doc:`../workflow_guide/parameters`.
