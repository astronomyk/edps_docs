Where your data ends up
=======================

EDPS saves the products into two directories. The first contains all recipe
products, logs and plots; the second, which is optional, contains only the
results of the last reduction steps.


The EDPS data directory
-----------------------

All recipe products, including all logs, book-keeping and intermediate files,
are saved into the directory specified during the first run (default:
``~/EDPS_data``).

.. warning::

   **This directory should not be deleted**, even after the execution of EDPS.
   It is used for bookkeeping purposes. EDPS will use the files stored there to
   run efficiently — among other things, EDPS will reuse products from that
   directory instead of re-executing a recipe whenever possible (a "smart
   re-run").

The location of this directory can be changed by changing the value of the
``base_dir`` parameter in the configuration file
``~/.edps/application.properties``, or by deleting the ``~/.edps`` directory and
repeating the configuration step.

Directory structure
~~~~~~~~~~~~~~~~~~~

The files in this directory are organised in a four-level tree:

.. code-block:: text

   EDPS_data/
   └── ESPRESSO/              1. instrument
       ├── bias/              2. reduction step (task)
       │   ├── <job-id-1>/    3. one execution of that task
       │   │   ├── master_bias.fits
       │   │   ├── parameters.rc
       │   │   ├── ... input list, recipe log, book-keeping
       │   │   └── <plots>/   4. quality control plots
       │   └── <job-id-2>/
       ├── flat/
       ├── dark/
       └── object/

1. The first level contains directories named after the **instrument** used
   (e.g. ``ESPRESSO``).
2. The second level contains directories named after the various **reduction
   steps** — e.g. ``dark``, ``flat``, ``bias``, ``object`` and so forth. The
   exact list depends on the instrument, the data present on disk, and the
   reduction strategy.
3. The third level includes each individual **execution** of a given task. For
   example, if the bias task was executed N times because there were N sets of
   bias to reduce, the bias directory will contain N subdirectories (a.k.a.
   *job directories*), each containing the products and the book-keeping files
   (such as list of inputs, list of parameters used, recipe log and so forth).
4. The fourth and final level contains **quality control plots** that can be
   used to inspect the recipe products. Each job directory can have one or more
   subdirectories containing the quality control plots for that specific recipe
   execution, depending on the workflow.

.. tip::

   The file ``parameters.rc`` in each job directory records only the recipe
   parameters that **differ from the recipe default**. The products themselves
   carry a record of the recipe parameter values in their headers. To inspect
   the parameter values that are going to be used *before* the reduction
   starts, see :ref:`display-parameters`.


The output directory
--------------------

If the output directory has been specified in the ``edps`` request via the
``-o`` option, then the products of the **last reduction steps** are copied
into the output directory.

In the case of ESPRESSO, the last reduction step corresponds to the reduction of
science target with the recipe ``espdr_sci_red``. For other instruments, like
MUSE and KMOS, also the combination of multiple exposures taken on different
nights are included among the final products. To specify different final
task(s) (also known as *target task*), see :ref:`target-task`.

.. note::

   Only the FITS files are stored in the output directory. All other
   information is still available in the general EDPS data directory described
   above.

Data are organised first by **dataset name**. The dataset name is defined as the
name of the first FITS file that triggers the recipe. Inside each dataset
directory there are the results of different EDPS executions, identified by the
**time stamp** of the EDPS request. If two reductions are identical (i.e. same
inputs, same parameters), EDPS does not create a different time stamp
directory.

The user can specify a different location and naming convention for some
products by setting the EDPS configuration file accordingly; see
:ref:`renaming-products`.
