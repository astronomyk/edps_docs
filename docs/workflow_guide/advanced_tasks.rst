Tasks: advanced features
========================

.. _conditional-association:

Conditional association
-----------------------

It is possible to specify a condition under which a file (or a task) is
associated to another task. Conditions can be based on **workflow parameters**
(static) or can depend on the properties of the main input data — **data-driven
conditions** (dynamic).

Based on a static parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example: associate the bias task to the science task only if it is the desired
reduction strategy. The behaviour is regulated by a parameter (named, for
example, ``use_bias``) defined in the ``parameter.yaml`` file.

.. code-block:: yaml
   :caption: example_parameters.yaml
   :linenos:

   qc1_parameters:
     tags: [ qc1calib ]
     is_default: yes
     workflow_parameters:
       use_bias: "NO"

.. code-block:: python
   :caption: example_task_functions.py
   :linenos:

   def use_bias(params: JobParameters) -> bool:
       return get_parameter(params, "use_bias") == "YES"

.. code-block:: python
   :caption: example_wkf.py
   :linenos:

   from edps import task
   from .demo_datasources import *
   from .demo_task_functions import *
   [...]
   science_task = (task("science")
                   .with_main_input(raw_science)
                   .with_associated_input(bias, [MASTERBIAS], condition=use_bias)
                   .with_recipe('run_science')
                   .build())

In the above example, we omit the definition of bias task, datasources, and
classification rules.

* If the workflow parameter ``use_bias`` is set to ``NO``, then the condition
  (evaluated by the function ``use_bias``) is False, and the bias is not
  associated. **The job is considered complete.**
* If the workflow parameter ``use_bias`` is set to ``YES``, then the condition is
  True. If appropriate biases are found, then they are associated and the job is
  complete. If appropriate biases are not found, then no bias is associated and
  the job is incomplete.

Based on a dynamic parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The condition can be evaluated on the basis of the properties of the main input.
In the following example, we associate the bias only if the ``INS.MODE`` header
keyword of the main input is set to ``IMG``.

.. code-block:: python
   :caption: example_task_functions.py
   :linenos:

   def which_ins_mode(files: List[ClassifiedFitsFile]):
       ins_mode = files[0].get_keyword_value("ins.mode", None)
       return ins_mode

   def is_img(params: JobParameters) -> bool:
       return params.get_workflow_param('ins_mode') == 'IMG'

.. code-block:: python
   :caption: example_wkf.py
   :linenos:

   from edps import task
   from .demo_datasources import *
   from .demo_task_functions import *
   [...]
   science_task = (task('SCIENCE')
                   .with_main_input(raw_science)
                   .with_dynamic_parameter("ins_mode", which_ins_mode)
                   .with_associated_input(bias, [MASTERBIAS], condition=is_img)
                   .with_recipe('run_science')
                   .build())

In this example, the main input of the task (that can change for every job) is
inspected by the ``which_ins_mode`` function. The task defines a parameter (named
``ins_mode``) whose value is computed by the function ``which_ins_mode``. Because
the inputs to the task can vary, the parameter is called **dynamic**. The
condition is evaluated by the function ``is_img``, which returns True if the
``ins_mode`` parameter is equal to ``IMG``; otherwise it returns False.

As for the case of static parameters, the job is not checked for completeness if
the association condition is False.

.. note::

   The source manual captions the first block above ``example_parameters.yaml``,
   but its content is Python, and it belongs in the task-functions file. It is
   captioned correctly here.


Execute a task under certain conditions
---------------------------------------

The execution of a task can be subordinated to certain conditions, expressed via
a workflow parameter. This is useful, for example, when specifying the reduction
cascade (activate certain tasks instead of others). The conditions that trigger
the task are as in the static-parameter case above.

.. code-block:: yaml
   :caption: example_parameters.yaml
   :linenos:

   qc1_parameters:
     tags: [ qc1calib ]
     is_default: yes
     workflow_parameters:
       use_sky_flats: "NO"

.. code-block:: python
   :caption: example_task_functions.py
   :linenos:

   def use_sky_flats(params: JobParameters) -> bool:
       return get_parameter(params, "use_sky_flats") == 'YES'

.. code-block:: python
   :caption: example_wkf.py
   :linenos:

   [...]
   sky_flat = (task('SKYFLAT')
               .with_condition(use_sky_flat)
               .with_main_input(raw_sky_flats)
               .with_recipe("run_sky_flats")
               .build())

In the example, the task ``SKYFLAT`` is executed only if the workflow parameter
``use_sky_flats`` is set to ``"YES"``. In the example, we omit import statements
and the definition of datasources and classification rules.
:doc:`../examples/simple` presents a similar example within a complete workflow.


How to specify alternative inputs
---------------------------------

Alternative inputs can be specified with the object
``alternative_associated_input``. The object lists a series of alternatives; if
the first is not found it goes to the second and so forth. If the first is found,
it is returned and the others are not associated.

.. code-block:: python
   :linenos:

   from edps import task, alternative_associated_inputs

   calibrations = (alternative_associated_input()
                   .with_associated_input(bias, [MASTERBIAS])
                   .with_associated_input(dark, [MASTERDARK]))

   task = (task("reduction")
           .with_recipe("run_reduction")
           .with_main_input(raw_science)
           .with_alternatives(calibrations)
           .build())

In the example above, bias calibrations have the precedence: if found they are
associated to the task. Otherwise dark calibrations are associated. If none are
present, the task is incomplete. If the calibrations are optional, add
``min_ret=0`` to the last alternative in the list (dark, in this example).

The ``.with_associated_inputs()`` methods inside ``alternative_associated_inputs()``
have the same properties as if they were used in a task: ``min_ret``/``max_ret``,
``condition``, and ``match_rules``.

.. note::

   The source manual uses the names ``alternative_associated_input``,
   ``alternative_associated_inputs`` and ``alternative_association``
   interchangeably across examples. In EDPS 1.7.1 all three names are
   importable from ``edps``, alongside ``alternative_associated_inputs``.


Setting the recipe parameters
-----------------------------

The parameters of a recipe in a task can be set in several ways, listed here in
**order of precedence** (first has precedence):

1. Using the option ``-rp TASK PARAMETER VALUE`` in the ``edps-client`` request,
   e.g.:

   .. code-block:: console

      $ edps -w muse.muse_wkf -rp bias muse_bias muse.muse_bias.nifu 0

2. Via the ``instrument_parameters.yaml`` file (see :doc:`parameters`).

3. Via a job function (see below).

4. No particular specification: the recipe default is used.


Modifying the job properties
----------------------------

It is possible to modify at run-time the properties of a job (e.g. the values of
the recipe parameters) depending on the properties of the input data. In the
following example, taken from the UVES workflow, we modify the job created by the
task ``object`` to adjust the recipe parameter depending on the input data.

.. code-block:: python
   :caption: uves_task_functions.py
   :linenos:

   def object_type(job: Job):
       # Setting some recipe parameters in uves_obs_scired depending if the main
       # input is extended or point-like
       # Note: job.command is the recipe name.
       reduce_extract_method = f'{job.command}.reduce.extract.method'   # full name of recipe parameter
       reduce_backsub_method = f'{job.command}.reduce.backsub.mmethod'  # full name of recipe parameter
       dp_types = [f.get_keyword_value("dpr.type", None) for f in job.input_files]
       if "OBJECT,EXTENDED" in dp_types or "OBJECT,EXTENDED,EXTENDED" in dp_types:
           # Parameters to be set in the case of extended objects.
           job.parameters.recipe_parameters[reduce_extract_method] = "2d"
           job.parameters.recipe_parameters[reduce_backsub_method] = "minimum"
       elif "OBJECT,POINT" in dp_types or "OBJECT,POINT,POINT" in dp_types:
           # Parameters to be set in case of point-like objects.
           job.parameters.recipe_parameters[reduce_extract_method] = "optimal"
           job.parameters.recipe_parameters[reduce_backsub_method] = "median"

.. code-block:: python
   :caption: uves_wkf.py
   :linenos:

   from . import uves_task_functions
   # Task to reduce long slit observations
   science_slit = (task("object")
                   .with_recipe("uves_obs_scired")
                   .with_main_input(raw_science)
                   [...]
                   # set recipe params depending on target (extended or point-like)
                   .with_job_processing(object_type)
                   .build())

The following example, taken from the KMOS workflow, is designed to pass only the
last input file to the recipe:

.. code-block:: python
   :caption: kmos_fit_profiles.py
   :linenos:

   [...]
   # Process only the last acquisition
   def process_last_file(job: Job):
       job.input_files = [job.input_files[-1]]

   acquisition_reconstruct = (task('acquisition_reconstruct')
                              .with_recipe('kmos_reconstruct')
                              [...]
                              # Process only the last main input file.
                              .with_job_processing(process_last_file)
                              .build())


Modifying the input category tag
--------------------------------

For a certain recipe in the reduction chain, the input category of a file, as
specified in the *set of frames* (sof), can differ from the category the file is
classified in. In order to change the tag of the files that are going to be
written in the recipe sof, the ``.with_input_map()`` method in the task can be
used.

.. code-block:: python
   :linenos:

   reduction = (task("task")
                .with_recipe("recipe_name")
                .with_main_input(raw_input)
                .with_associated_input(calibration)
                .with_input_map({CATEGORY1: NEW_CATEGORY1,
                                 CATEGORY2: NEW_CATEGORY2})
                .build())

In the above example, the inputs that are tagged as ``CATEGORY1`` will be tagged
in the sof that will be given as input to the recipe ``recipe_name`` as
``NEW_CATEGORY1``. Similarly, the ``CATEGORY2`` inputs will be tagged as
``NEW_CATEGORY2``.

.. important::

   This renaming does **not** alter the header of the files.
