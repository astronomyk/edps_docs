Running Python scripts and looping on recipes
=============================================

The task is primarily designed to run recipe pipelines specified with the
``.with_recipe("recipe_name")`` method. It is possible, however, to pass a
function that runs a script instead.

In the following example we show the task that performs the telluric correction
on FORS2 spectra. The task (named ``telluric_correction``) runs a function (also
named ``telluric_correction``) instead of a recipe.

The function performs the following steps:

* Runs a Python function that selects, among the input spectra to correct, the
  one with higher signal-to-noise (read from the file header). Let's call it
  *reference spectrum*.
* Runs the recipe ``fors_molecfit_model`` on the selected reference spectrum.
* Loops on all the input spectra to correct, running the following recipes:

  * Generates a telluric correction for the input spectrum, using the model
    results obtained from the reference spectrum (recipe
    ``fors_molecfit_calctrans``).
  * Corrects the input spectrum for telluric absorption (recipe
    ``fors_molecfit_correct``).


Declaring the task
------------------

.. code-block:: python
   :caption: fors_spec_wkf.py
   :linenos:

   [...]
   # --- Task for telluric correction (only for Long Slit data).
   telluric = (task('telluric_correction')
               .with_function(telluric_correction)
               .with_main_input(science)
               [...]
               .build())

Note ``.with_function()`` where a recipe-based task would use ``.with_recipe()``.


The function
------------

.. code-block:: python
   :caption: fors_task_functions.py
   :linenos:

   from astropy.io import fits
   from edps import File, FitsFile
   from edps import List, ClassifiedFitsFile, JobParameters, get_parameter, Job
   from edps import RecipeInvocationArguments, RecipeInvocationResult, InvokerProvider, \
       RecipeInputs, ProductRenamer

   from . import fors_keywords as kwd


   # --- FUNCTIONS TO PERFORM THE TELLURIC CORRECTION -------------------------

   # --- This function checks the parameter telluric_correction in the
   # fors_parameters.yaml file and determines whether the telluric correction
   # has to be carried on or not.

   def perform_telluric_correction(params: JobParameters) -> bool:
       return get_parameter(params, "telluric_correction") == "TRUE"


   # --- This function finds the spectrum with higher signal-to-noise
   def find_reference_file(science_files: List[File]):
       max_snr = 0
       reference_file = None
       for file in science_files:
           with fits.open(file.file_path) as hdus:
               snr = hdus[0].header['SNR']
               wavelen_max = hdus[0].header['WAVELMAX']
           if snr > max_snr and wavelen_max > 680.:
               max_snr = snr
               reference_file = file
       if reference_file:
           return File(reference_file.file_path, reference_file.category, ""), max_snr
       else:
           return None, None


   # --- Generic function to run a recipe
   def run_recipe(input_file, associated_files, parameters, recipe_name, args, invoker,
                  renamer) -> (RecipeInvocationResult, List):

       # input_file: main input and category. Format: File(string_with_full_path,
       #                                                   string_with_category, "")
       # associated_files: calibrations. Format List[file], where files have the format:
       #                                   File(string_with_full_path, string_with_category, "")
       # parameters: non default recipe parameters. Format {'parameter_name1': value1,
       #                                                    'parameter_name2': value2}
       # recipe_name: recipe name  Format: string
       # args, invoker: extra stuff provided by the task that calls the function
       #                calling run_recipe()

       inputs = RecipeInputs(main_upstream_inputs=[input_file],
                             associated_upstream_inputs=associated_files)
       arguments = RecipeInvocationArguments(inputs=inputs, parameters=parameters,
                                             job_dir=args.job_dir, input_map={},
                                             logging_prefix=args.logging_prefix)

       results = invoker.invoke(recipe_name, arguments, renamer, create_subdir=True)
       output_files = [File(f.name, f.category, "") for f in results.output_files]
       return results, output_files


   # --- This function coordinates the telluric correction process.
   #  - It finds the spectrum with higher S/N
   #  - It runs fors_molecfit_model on the higher S/N spectrum and determines the
   #    properties of the atmosphere.
   #  - For each spectrum to correct, it
   #      - computes the full telluric correction spectrum (fors_molecfit_calctrans)
   #      - applies the correction to the science spectrum.
   #
   def telluric_correction(args: RecipeInvocationArguments,
                           invoker_provider: InvokerProvider,
                           renamer: ProductRenamer) -> RecipeInvocationResult:
       invoker = invoker_provider.recipe_invoker
       results = []
       ret_codes = []
       calibration_categories = ['MOLECULES', 'WAVE_INCLUDE', 'WAVE_EXCLUDE', 'PIX_EXCLUDE',
                                 'ATM_PROFILE_STANDARD', 'KERNEL_LIBRARY', 'GDAS']
       science_categories = ['REDUCED_IDP_SCI_LSS']

       calibration_files = [File(f.name, f.category, "") for f in args.inputs.combined
                            if f.category in calibration_categories]
       science_files = [File(f.name, f.category, "") for f in args.inputs.combined
                        if f.category in science_categories]

       # find the file with higher signal-to-noise
       reference_file, max_snr = find_reference_file(science_files)

       # run fors_molecfit_model on reference_file if available
       if reference_file:
           molefit_parameters = {'WAVE_INCLUDE': '0.61,0.64,0.68,0.71,0.711,0.740,0.75,0.78,'
                                                 '0.81,0.84,0.91,0.95,0.96,0.98',
                                 'LIST_MOLEC': 'H2O, O2'}

           result_reference, reference_files = run_recipe(reference_file, calibration_files,
                                                          molefit_parameters, 'fors_molecfit_model',
                                                          args, invoker, renamer)

           ret_codes.append(result_reference.return_code)
           reference_files = [File(f.name, f.category, "")
                              for f in result_reference.output_files]

           # LOOPING fors_molecfit_calctrans and fors_molecfit_correct, using results
           # from the reference file for all the inputs
           for science_file in science_files:
               # run fors_molecfit_calctrans and for_molecfit_correct
               results_calctrans, caltrans_output_files = run_recipe(
                   science_file, reference_files, {},
                   'fors_molecfit_calctrans', args, invoker, renamer)
               result_correct, correct_output_files = run_recipe(
                   science_file, caltrans_output_files, {},
                   'fors_molecfit_correct', args, invoker, renamer)

               ret_codes.extend([results_calctrans.return_code, result_correct.return_code])
               results.append(result_correct)

           # Construct final RecipeInvocationResult
           ret_code = min(ret_codes)
           output_files = [FitsFile(name=f[0].name, category=f[0].category)
                           for f in ([r.output_files for r in results])]
           corrected_files = RecipeInvocationResult(return_code=ret_code,
                                                    output_files=output_files)
       else:
           output_files = [FitsFile(name=f.name, category=f.category)
                           for f in args.inputs.combined]
           corrected_files = RecipeInvocationResult(return_code=0,
                                                    output_files=output_files)
       return corrected_files


Anatomy of a task function
--------------------------

The signature that EDPS expects is:

.. code-block:: python

   def my_function(args: RecipeInvocationArguments,
                   invoker_provider: InvokerProvider,
                   renamer: ProductRenamer) -> RecipeInvocationResult:

``args``
   Carries ``args.inputs.combined`` (all input files with their categories),
   ``args.job_dir`` and ``args.logging_prefix``.

``invoker_provider``
   ``invoker_provider.recipe_invoker`` is what actually runs a recipe; call
   ``invoker.invoke(recipe_name, arguments, renamer, create_subdir=True)``.

``renamer``
   Passed straight through to ``invoke``.

The function must return a ``RecipeInvocationResult`` carrying a return code and
the list of output files — that is what the rest of the cascade consumes.

.. tip::

   The ``run_recipe`` helper above is worth copying into any workflow that needs
   this pattern. It reduces "invoke one recipe" to a single call and keeps the
   coordinating function readable.
