Configuring EDPS: ``application.properties``
============================================

Several options in EDPS can be specified in a configuration file, named
``application.properties``. This file is located in the ``.edps/`` directory in
your ``HOME`` directory (see :doc:`installation`).

If a feature can be specified both in the command-line request and in the
configuration file, **the command-line request has priority**.

.. warning::

   To make the changes done in ``application.properties`` effective, you must
   first **restart the EDPS server**. To close the server, type (from a terminal
   with the EDPS environment active):

   .. code-block:: console

      $ edps -shutdown

.. admonition:: File format changed after the source manual
   :class: note

   In EDPS 1.7.1 the file is INI-style, split into ``[server]``,
   ``[application]``, ``[executor]``, ``[generator]``, ``[repository]``,
   ``[cleanup]`` and ``[packager]`` sections. The settings described below live
   in those sections. A complete annotated dump of the file, with every setting
   and its default, is in :doc:`../reference/application_properties`.


Association preference: RAW vs MASTER calibrations
--------------------------------------------------

If the input directory contains both ``MASTER`` (e.g. pre-reduced calibrations)
and ``RAW`` calibrations, it could happen that both of them fulfil the matching
criteria and quality level for a certain task. In this case, one can specify
which type of calibration to give priority to, by setting the variable
``association_preference`` in the ``application.properties`` configuration file.

Possible values of ``association_preference`` are:

``raw``
   First, EDPS checks if there are **raw** calibrations ensuring the first
   quality level of the products. If found, they are associated. If not found,
   raw calibrations ensuring the second quality level of the products are
   searched. If not found, the next level is searched until the last quality
   level permitted by the workflow parameter ``quality_threshold`` is reached.
   If no raw calibrations are found for none of the quality levels, then EDPS
   searches for **master** calibrations, starting from those ensuring the first
   quality level. If none are found, the second level is searched, and so
   forth. If no calibrations are found, the association is not done.

``master``
   Same as ``raw``, but first master calibrations are looked for all the
   products quality levels permitted by the workflow parameter
   ``quality_threshold``. Then, if master calibrations are not found, the
   system looks for raw calibrations.

``raw_per_quality_level`` (default)
   First, the system will check if there are **raw** calibrations ensuring the
   first quality level of the products. If not found, **MASTER** calibrations
   ensuring this level are searched for. If not found, RAW calibrations ensuring
   the second quality level are searched for; if not found, MASTER calibrations
   matching the second quality level are searched for. The sequence goes on
   until the last level permitted by the workflow parameter
   ``quality_threshold``.

``master_per_quality_level``
   Same as ``raw_per_quality_level``, but with inverted roles for MASTER and RAW
   calibrations.

If a combination of ``RAW`` and ``MASTER`` calibrations are present, the value of
``association_preference`` might have an impact on the performance and the
quality of the results. Typically:

* ``association_preference = raw_per_quality_level`` delivers the best quality
  products, at the price of speed.
* ``association_preference = master`` ensures faster performance, at cost of
  quality (e.g. a very old master calibration could be used instead of a more
  recent raw calibration).

If only ``RAW`` **or** ``MASTER`` calibrations are present in the input
directories, then the value of ``association_preference`` has no impact.

.. seealso::

   The quality levels themselves are defined by the workflow developer; see
   :ref:`association-levels`.


Running recipes in parallel
---------------------------

One of the advantages of EDPS is that it can exploit powerful hardware. The
following variables in the ``application.properties`` file determine the
parallelisation of the EDPS reduction.

``processes`` (default: 1)
   The maximum number of jobs to run in parallel (e.g. ``esorex`` parallel
   executions).

``cores`` (default: 1)
   The maximum number of computer cores to use, considering all the parallel
   jobs.

``default_omp_threads`` (default: 1)
   The number of cores to use for each job. This can be overridden by
   specifying a recipe parameter ``OMP_NUM_THREADS`` for a given task — e.g.
   ``-rp object OMP_NUM_THREAD 3`` to assign a desired number of threads to the
   ``object`` task, whereas all the others use the default value.

.. warning::

   Running concurrent data reductions increases performance if sufficient
   resources are available, but can also lead to pipeline crashes if not enough
   memory is available to execute parallel reductions. Raise ``processes``
   cautiously on memory-hungry pipelines such as MUSE.


Order of executions
-------------------

The variable ``ordering`` in the ``application.properties`` file specifies the
priority to give to the reduction jobs. All orderings follow topological order,
so parent tasks are always placed before their children. The most important
values are:

``dfs``
   Depth-first: gives preference to reaching the final reduction target
   quicker. In other words, it finishes the reduction of a dataset before moving
   to the next dataset. This choice is less efficient in time but it gives
   priority to the reduction of individual datasets.

``bfs``
   Breadth-first: gives preference to following the reduction cascade level by
   level. This is the default in EDPS 1.7.1.

``type``
   Same as ``bfs``, but makes sure to process the same type of data together
   (e.g. first all biases).

``dynamic``
   Immediately runs whichever job is ready (has all needed inputs); no stalling,
   but the order is unpredictable. This is the most time-efficient execution
   order.


.. _renaming-products:

Renaming product file names
---------------------------

If the user specified an output directory via the ``-o`` option in the EDPS
request (see :doc:`first_reduction`), the products of the target task(s) — i.e.
the final steps in the processing cascade — are saved in the specified
directory. Their names are given by the ``pattern`` variable in
``application.properties``.

The users can decide to copy or hard-link certain product categories into a
different location and with a different naming convention. This can be done by
setting the following variables in the ``application.properties`` configuration
file:

``mode`` (values: ``copy``/``link``)
   Specifies if the products have to be copied or (hard) linked into the output
   directory. Default: ``copy``. EDPS 1.7.1 also accepts ``symlink``.

``categories``
   List of categories (i.e. the ``HIERARCH ESO PRO CATG`` header keywords of the
   recipe products) that have to be copied or linked.

``pattern``
   Pattern to follow for the saving and naming convention. The default value is:

   .. code-block:: text

      pattern = $DATASET/$TIMESTAMP/$object$_$pro.catg$.$EXT

   The following predefined variables can be used:

   .. list-table::
      :header-rows: 1
      :widths: 22 78

      * - Variable
        - Meaning
      * - ``$TASK``
        - Name of the task generating the product.
      * - ``$DATASET``
        - Name of the dataset.
      * - ``$TIMESTAMP``
        - Time of the request to EDPS.
      * - ``$EXT``
        - File extension (``.fits``).
      * - ``$NIGHT``
        - Year-month-day of when the data were taken. *(EDPS 1.7.1; not in the
          source manual.)*
      * - ``$FILENAME``
        - Original name of the file. *(EDPS 1.7.1; not in the source manual.)*

   ``object`` and ``pro.catg`` in the default values represent the ``OBJECT``
   and ``HIERARCH ESO PRO CATG`` header keywords of the file. Values from header
   keywords and general text can be added, bracketed by ``$``.

For example, the following setup:

.. code-block:: ini

   package_base_dir=~/my_reduction/
   mode=link
   pattern=$TASK/$DATASET/$TIMESTAMP/\$object\$_\$pro.catg\$_reduced.$EXT
   categories=S1D_FINAL_A

will hard-link the category ``S1D_FINAL_A`` produced by the pipeline recipe
``espdr_sci_red`` into the directory ``~/my_reduction/``. Files are organised
into subdirectories that specify task name, the dataset name, and the creation
date. The names of the files contain the value of the ``OBJECT`` and
``HIERARCH ESO PRO CATG`` keywords, as specified in the product header.


Reprocessing a given set of datasets
------------------------------------

If you want to test which combination of options in
``${HOME}/.edps/application.properties`` works best for you, by processing a
given dataset several times with different values of one or more parameters in
the config file, you need to set the config parameter ``truncate`` to ``True``
and restart the server each time — or more precisely, shut down the server after
each invocation of ``edps``:

1. Edit ``${HOME}/.edps/application.properties``.

2. Run ``edps``, e.g.:

   .. code-block:: console

      $ edps -w espresso.espresso_wkf -i <input_directory> -o <output_directory>

3. Stop the EDPS server:

   .. code-block:: console

      $ edps --shutdown

4. Repeat from step 1 for each combination of config parameter values you want
   to test.

.. warning::

   ``truncate=True`` clears the EDPS bookkeeping database on startup. This
   causes all tasks to be re-executed even if they have been executed before on
   the same data — which is exactly what you want for a controlled comparison,
   and exactly what you do not want in normal operation. Remember to set it back
   to ``False``.


Changing the pipeline
---------------------

EDPS runs the workflows associated to the ``esorex`` command that is in the
system path. In order to change the workflow and/or the pipeline, edit the
following variables in the ``application.properties`` file so that they point to
the location of the workflow and ``esorex`` command associated to the desired
pipeline:

.. code-block:: ini

   workflow_dir=        # insert path to the new workflow directory
   esorex_path=esorex   # insert path of the new executable

In order for these changes to have effect, the EDPS server has to be shut down:

.. code-block:: console

   $ edps -shutdown

.. note::

   The source manual writes this second key as ``esorex_path=esorex``; in EDPS
   1.7.1 it lives in the ``[executor]`` section and is indeed named
   ``esorex_path``. ``workflow_dir`` is in the ``[application]`` section and
   accepts a comma-separated list of directories.
