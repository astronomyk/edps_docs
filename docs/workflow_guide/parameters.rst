The parameters file
===================

"General" and "workflow" parameter files
----------------------------------------

Static parameters (see :doc:`advanced_tasks`) in the workflow and recipe
parameters are stored in the so-called **parameter file** (in YAML format). The
name of the parameter file should be ``<instrument>_parameters.yaml``, and it
should be located in the same directory where the workflow files are.

The structure of a workflow parameter file is (mind the spaces):

.. code-block:: yaml
   :linenos:

   parameters_set1:        # name of the 1st parameter set
     is_default: yes/no    # tells if this set is default
     workflow_parameters:  # list of static parameters
       param1: value1
       param2: value2
       ...
     recipe_parameters:    # list of task/recipe parameters
       task1:
         recipe1.param1: value1
         recipe1.param2: value2
       task2:
         recipe2.param1: value3
         recipe2.param2: value4
       ...
   parameters_set2:        # name of the 2nd parameter set
     is_default: yes/no    # tells if this set is default
     workflow_parameters:  # list of static parameters

Notes:

* Different tasks can run the same recipe.
* If a recipe parameter is not listed, its default value is used.
* **Only 1 default is admitted.**
* It is not mandatory to specify multiple parameter sets. Technically, the file
  can be empty or not provided in ``parameters.yaml`` at all.
* Tasks are allowed a special parameter ``OMP_NUM_THREADS: <value>``, that
  defines the number of threads to be used by the recipe of that task,
  overriding (for that task only) the default specified in
  ``application.properties``.
* Workflow parameters or recipe parameters specified in the request call have
  **precedence** over those specified in the parameter file.
* Parameters that are strings or boolean must be written in quotation marks (see
  example below).


Example
-------

Example extracted from the MUSE EDPS workflow. Two parameter sets are defined:
``qc1_parameters`` (the default) and ``test_parameters``.

.. code-block:: yaml
   :caption: muse_parameters.yaml
   :linenos:

   qc1_parameters:
     is_default: yes
     workflow_parameters:
       lsfmode: "arc"
       skysubtraction: "auto"
       recompute_geometry: "no"
       recompute_astrometry: "no"
       wavelength_min: 4000.
       wavelength_max: 10000.
       telluric_correction: "TRUE"
       combine_science: "obs.id"
       max_diameter: 2
       max_separation: 0.25
       use_darks: "no"
     recipe_parameters:
       bias:
         muse.muse_bias.nifu: -1
         muse.muse_bias.merge: "TRUE"
       dark:
         muse.muse_dark.nifu: -1
         muse.muse_dark.merge: "TRUE"
       flat_lamp:
         muse.muse_flat.nifu: -1
         muse.muse_flat.merge: "TRUE"
       linearity_and_gain:
         muse.muse_lingain.nifu: -1
       wavelength:
         muse.muse_wavecal.nifu: -1
         muse.muse_wavecal.merge: "TRUE"
       line_spread_function:
         muse.muse_lsf.nifu: -1
         muse.muse_lsf.merge: "TRUE"
       line_spread_function_2:
         muse.muse_lsf.nifu: -1
         muse.muse_lsf.merge: "TRUE"
       throughput:
         muse.muse_ampl.nifu: -1
         muse.muse_ampl.savemaster: "TRUE"
         muse.muse_ampl.savetable: "TRUE"
         muse.muse_ampl.merge: "TRUE"
       preprocess_standard:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_science:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_astrometry:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_sky:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       science:
         muse.muse_scipost.save: "cube,individual"
         muse.muse_scipost.format: "sdpCube"
         muse.muse_scipost.skymodel_fraction: 0.4
       science_sky:
         muse.muse_scipost.save: "cube,individual"
         muse.muse_scipost.format: "sdpCube"
         muse.muse_scipost.skymodel_fraction: 0.4
       science_combination:
         muse.muse_exp_combine.format: "sdpCube"
       mask:
         OMP_NUM_THREADS: 12

   test_parameters:
     is_default: no
     workflow_parameters:
       lsfmode: "lsf"
       skysubtraction: "auto"
       recompute_geometry: "no"
       recompute_astrometry: "yes"
     recipe_parameters:
       bias:
         muse.muse_bias.nifu: -1
         muse.muse_bias.merge: "TRUE"
       dark:
         muse.muse_dark.nifu: -1
         muse.muse_dark.merge: "TRUE"
       flat_lamp:
         muse.muse_flat.nifu: -1
         muse.muse_flat.merge: "TRUE"
       linearity_and_gain:
         muse.muse_lingain.nifu: -1
       wavelength:
         muse.muse_wavecal.nifu: -1
         muse.muse_wavecal.merge: "TRUE"
       line_spread_function:
         muse.muse_lsf.nifu: -1
         muse.muse_lsf.merge: "TRUE"
       line_spread_function_2:
         muse.muse_lsf.nifu: -1
         muse.muse_lsf.merge: "TRUE"
       throughput:
         muse.muse_ampl.nifu: -1
         muse.muse_ampl.savemaster: "TRUE"
         muse.muse_ampl.savetable: "TRUE"
         muse.muse_ampl.merge: "TRUE"
       preprocess_standard:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_science:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_astrometry:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       preprocess_sky:
         muse.muse_scibasic.nifu: -1
         muse.muse_scibasic.merge: "TRUE"
       science:
         muse.muse_scipost.save: "cube,individual"
         muse.muse_scipost.format: "sdpCube"
         muse.muse_scipost.skymodel_fraction: 0.4
       science_sky:
         muse.muse_scipost.save: "cube,individual"
         muse.muse_scipost.format: "sdpCube"
         muse.muse_scipost.skymodel_fraction: 0.4
       science_combination:
         muse.muse_exp_combine.format: "sdpCube"

Note how the two sets differ only in a handful of workflow parameters
(``lsfmode``, ``recompute_astrometry``) while repeating the recipe parameters.
Users select a set from the command line with ``-wps`` and ``-rps``; see
:ref:`display-parameters`.

.. note::

   Some workflows additionally attach a ``tags:`` list to a parameter set, e.g.
   ``tags: [ qc1calib ]``. This appears in the examples in
   :doc:`advanced_tasks` and :doc:`../examples/index`.
