The integrated test suite: JSON tests
=====================================

``json_tests.py`` contains generic logic which executes all test cases defined
under the ``tests/json_configuration`` directory. Adding a new test requires
putting a new scenario description in one of the existing ``.json`` files or
creating a new file. New files will be picked up automatically on the next test
run.


Test suite JSON file
--------------------

Each ``.json`` file contains a document with one field ``scenarios``, which
contains a list of scenario definitions. Those will be run in-order,
sequentially, exactly as they are defined in the file.


Scenario definition
-------------------

Each scenario has 3 major sections: test-case metadata, input file definitions,
and result expectations.

Test-case metadata
~~~~~~~~~~~~~~~~~~

The first section contains:

``description``
   Description of the test, which will be used as *test name* in the execution
   result.

``workflow``
   The workflow to be used for data organization.

``workflow_parameters``
   Optional dictionary to pass with the request to EDPS.

``workflow_parameter_set``
   Optional name of a *named parameter set* for EDPS to use.

``targets``
   List of target tasks to consider when generating jobs. EDPS will generate jobs
   for the targets and also for anything those targets depend on.

``meta_targets``
   List of labelled meta-targets which will be expanded by EDPS into a list of
   tasks to be used as targets.

Example:

.. code-block:: json

   {
     "description": "fors bias flat",
     "workflow": "fors.fors_imaging_wkf",
     "workflow_parameters": {
       "a": "b"
     },
     "workflow_parameter_set": "qc0_parameters",
     "targets": [
       "bias",
       "flat"
     ],
     "meta_targets": [],
     "skip": false
   }

Input file definitions
~~~~~~~~~~~~~~~~~~~~~~

Each test scenario will run EDPS using **generated FITS files**. The list
``input_files`` holds definitions of file templates. A template consists of:

``name_prefix``
   Will be prepended to generated files (each file will have a random UUID
   suffix).

``count``
   Number of files to generate, defaults to 1.

``keywords``
   Dictionary with keywords to place in the primary header of the FITS file.
   Keywords defined like that will be put in the file as-is.

Example:

.. code-block:: json

   {
     "input_files": [
       {
         "name_prefix": "bias",
         "count": 4,
         "keywords": {
           "instrume": "FORS1",
           "dpr.catg": "CALIB",
           "dpr.type": "BIAS"
         }
       },
       {
         "name_prefix": "flat",
         "keywords": {
           "instrume": "FORS1",
           "dpr.catg": "CALIB",
           "dpr.type": "FLAT,SKY",
           "dpr.tech": "IMAGE"
         }
       }
     ]
   }

Result expectations
~~~~~~~~~~~~~~~~~~~

Each test scenario will be validated against the defined expected results list.
The list ``results`` contains definitions of the jobs that are expected to be
created by EDPS. Each job is defined by:

``recipe``
   Name of the recipe which is supposed to be used.

``inputs_prefixes``
   List of allowed filename prefixes for the input files.

Example:

.. code-block:: json

   {
     "results": [
       {
         "recipe": "fors_bias",
         "inputs_prefixes": [
           "bias"
         ]
       },
       {
         "recipe": "fors_img_sky_flat",
         "inputs_prefixes": [
           "flat"
         ]
       }
     ]
   }

Full example
~~~~~~~~~~~~

.. code-block:: json

   {
     "description": "fors bias flat",
     "workflow": "fors.fors_imaging_wkf",
     "workflow_parameters": {
       "a": "b"
     },
     "workflow_parameter_set": "qc0_parameters",
     "targets": [
       "bias",
       "flat"
     ],
     "meta_targets": [],
     "input_files": [
       {
         "name_prefix": "bias",
         "count": 4,
         "keywords": {
           "instrume": "FORS1",
           "dpr.catg": "CALIB",
           "dpr.type": "BIAS"
         }
       },
       {
         "name_prefix": "flat",
         "keywords": {
           "instrume": "FORS1",
           "dpr.catg": "CALIB",
           "dpr.type": "FLAT,SKY",
           "dpr.tech": "IMAGE"
         }
       }
     ],
     "results": [
       {
         "recipe": "fors_bias",
         "inputs_prefixes": [
           "bias"
         ]
       },
       {
         "recipe": "fors_img_sky_flat",
         "inputs_prefixes": [
           "flat"
         ]
       }
     ]
   }


Default behaviour
-----------------

MJD-OBS
~~~~~~~

For each scenario a random *base mjd-obs* is generated. Unless ``MJD-OBS`` is
explicitly defined for a given template, the *base* value will be used. If there
is more than 1 file in the template, each consecutive file has the MJD-OBS
slightly further in the future compared to the previous one →
``base_mjd_obs + i * 0.02``. If the keyword is explicitly defined for a template
it will be used as-is, without the increment. Each consecutive template starts
with mjd-obs further back in time, based on the order in which inputs are defined
in the file.

TPL.START
~~~~~~~~~

If not explicitly defined, ``tpl.start`` is set to a randomly generated value,
the same for each file of the template. Input files template definition supports
only a single set of keywords, so in case different files should be marked as
part of the same template it might be necessary to explicitly set ``tpl.start``.

Example:

.. code-block:: json

   {
     "input_files": [
       {
         "name_prefix": "orderdef_a",
         "count": 1,
         "keywords": {
           "instrume": "ESPRESSO",
           "dpr.catg": "CALIB",
           "dpr.type": "ORDERDEF,LAMP,OFF",
           "tpl.start": "1"
         }
       },
       {
         "name_prefix": "orderdef_b",
         "count": 1,
         "keywords": {
           "instrume": "ESPRESSO",
           "dpr.catg": "CALIB",
           "dpr.type": "ORDERDEF,OFF,LAMP",
           "tpl.start": "1"
         }
       }
     ]
   }

With such definition both generated files will have the same ``tpl.start``.

Default keywords
~~~~~~~~~~~~~~~~

Certain keywords are inserted automatically, even if not explicitly defined:

* ``arcfile`` set to the same as file name: ``{prefix}_{i + 1}_{uuid.uuid4()}.fits``
* ``tpl.nexp`` set to number of template files
* ``tpl.expno`` set to numbers ``1..n`` for each template file


Known limitations
-----------------

* It's not possible to re-run one selected test, because they are generated
  dynamically. If you want to work on a single test only, set the ``skip`` flag
  for other tests.

* Synthetic data generation has no knowledge about the type of the data or any
  real-world relative order in which such data are taken. Unless you explicitly
  specify the ``MJD-OBS`` keyword you should not make any assumptions about the
  MJD-OBS value and therefore about chronological ordering of the generated
  files.

* Each template definition can have only one set of keywords to use.

* Tests are doing only the **data organization** part and are designed to verify
  the workflow against expectations about what jobs should be created for a given
  set of inputs. No recipes are run, so it's still possible that the workflow is
  not really correct (e.g. min/max-ret is set incorrectly or some task is not
  declaring an association necessary for the recipe).

* Result verification does not check if all defined prefixes are included in the
  list of input files for the recipe (e.g. if there is at least one file with
  each prefix); it checks only that there are no input files other than those
  with the right prefix (e.g. if the only expected prefix is ``bias`` and there
  is a file ``flat_...`` as input, the test will fail).

* Result verification is **strict** and it requires that the number of resulting
  jobs matches the number of defined expectations, and that there is at least one
  job matching each of the expectations.

* Tests are able to check only happy-paths; they always assert that the request
  succeeded, so they are not suitable for checking error conditions.


Sharing common definitions
--------------------------

Different tasks often share common inputs; moreover association rules may share
common header keywords. In particular this occurs when the full reduction chain
is tested.

For this reason the EDPS library offers special ways to share common
information:

.. code-block:: json

   {
     "keywords": {
       "keys_instrume_setup": {
         "instrume": "HAWKI",
         "det.ncorrs.name": "A",
         "ins.filt1.name": "B",
         "ins.filt2.name": "C"
       },
       "keys_detector": {
         "det.dit": 1,
         "det.ndit": 1,
         "det.rspeed": 1
       }
     },
     "inputs": [
       {
         "name_prefix": "dark",
         "count": 5,
         "common_keywords": [
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "dpr.catg": "CALIB",
           "dpr.type": "DARK",
           "dpr.tech": "IMAGE",
           "tpl.id": "HAWKI_img_cal_Darks",
           "tpl.nexp": 3,
           "tpl.start": 1,
           "obs.start": "2010-11-22T05:16:50",
           "arcfile": "HAWKI.010-11-22T05:16:50.fits"
         }
       },
       {
         "name_prefix": "reference_dark",
         "count": 1,
         "common_keywords": [
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "dpr.catg": "CALIB",
           "dpr.type": "DARK",
           "dpr.tech": "IMAGE",
           "pro.catg": "REFERENCE_DARK",
           "tpl.id": "HAWKI_img_cal_Darks",
           "tpl.nexp": 3,
           "tpl.start": 1,
           "obs.start": "2010-11-22T05:16:50"
         }
       },
       {
         "name_prefix": "flat_twilight",
         "count": 10,
         "common_keywords": [
           "keys_instrume_setup",
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "dpr.catg": "CALIB",
           "dpr.type": "FLAT",
           "dpr.tech": "IMAGE",
           "tpl.id": "HAWKI_img_cal_TwFlats",
           "tpl.start": "2010-11-22T05:15:50"
         }
       },
       {
         "name_prefix": "master_bpm",
         "common_keywords": [
           "keys_instrume_setup",
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "pro.catg": "MASTER_BPM"
         }
       },
       {
         "name_prefix": "master_conf",
         "common_keywords": [
           "keys_instrume_setup",
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "pro.catg": "MASTER_CONF"
         }
       },
       {
         "name_prefix": "master_dark",
         "common_keywords": [
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "pro.catg": "MASTER_DARK"
         }
       },
       {
         "name_prefix": "reference_twilight_flat",
         "common_keywords": [
           "keys_instrume_setup",
           "keys_detector"
         ],
         "keywords": {
           "instrume": "HAWKI",
           "pro.catg": "REFERENCE_TWILIGHT_FLAT"
         }
       }
     ],
     "scenarios": [
       {
         "skip": false,
         "description": "HAWKI master dark test",
         "workflow": "hawki.hawki_wkf",
         "targets": [
           "dark"
         ],
         "meta_targets": [],
         "common_inputs": [
           "dark",
           "reference_dark",
           "master_bpm",
           "master_conf"
         ],
         "results": [
           {
             "recipe": "hawki_dark_combine",
             "inputs_prefixes": [
               "dark"
             ],
             "assoc_prefixes": [
               "reference_dark",
               "master_bpm",
               "master_conf"
             ]
           }
         ]
       },
       {
         "skip": false,
         "description": "HAWKI master flat twilight test",
         "workflow": "hawki.hawki_wkf",
         "targets": [
           "flat"
         ],
         "meta_targets": [],
         "common_inputs": [
           "flat_twilight",
           "reference_twilight_flat",
           "master_dark",
           "master_bpm",
           "master_conf"
         ],
         "results": [
           {
             "recipe": "hawki_twilight_flat_combine",
             "inputs_prefixes": [
               "flat_twilight"
             ],
             "assoc_prefixes": [
               "reference_twilight_flat",
               "master_dark",
               "master_bpm",
               "master_conf"
             ]
           }
         ]
       }
     ]
   }

As one can note, in the previous example the set of FITS keywords defined by
``keys_instrume_setup`` is common to ``flat_twilight``,
``reference_twilight_flat``, ``master_bpm``, ``master_conf``, and the set of
keywords defined by ``keys_detector`` is common to these and ``dark``,
``reference_dark`` and ``master_dark``. Those can be shared using a syntax like
the following:

.. code-block:: json

   "common_keywords": [
     "keys_name1",
     "keys_name2"
   ]

Moreover inputs like ``master_bpm``, ``master_conf`` are common for the two shown
examples and can be shared with a syntax like:

.. code-block:: json

   "common_inputs": [
     "input_name1",
     "input_name2"
   ]

In this way, once a given common input (or a set of common FITS keywords) has
been validated, it is easy to extend the list of unit tests. The inputs and FITS
keywords involved in the association rules that are peculiar will have to be
explicitly written.
