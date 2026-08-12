Your first data reduction
=========================

This section guides you through the reduction of science data with an EDPS
workflow. As an example we refer mostly to the ESPRESSO workflow.

We assume that EDPS, the ESPRESSO pipeline with ``esorex`` and the workflow have
been successfully installed and configured on your system (see
:doc:`installation`), and that ``esorex`` is on your ``PATH``. If the
installation was done via a Python virtual environment, it needs to be
activated:

.. code-block:: console

   $ . <path_to_environment>/edps/bin/activate


The one-line reduction
----------------------

A simple reduction of all of the ESPRESSO data in a directory
``input_directory`` can be achieved with a single command:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -o <output_directory>

That is the whole thing. For example, the default location of the ESPRESSO demo
data when installing the ESPRESSO pipeline with RPMs is
``/usr/share/esopipes/datademo/espdr``.

It is recommended to try this command on the demo data provided with the
pipeline before running it on your own data.


What just happened
------------------

EDPS scans the input directory **recursively** — the directory and all of its
subdirectories are scanned for data. In addition, the static calibration
directory delivered with the pipeline is used.

From there:

1. Any FITS file found is **classified**.
2. The science files are **identified**.
3. The best calibrations to be used are **associated**.
4. All science exposures with a complete set of calibrations are **processed**.
5. The final data products are **copied** into the ``output_directory``, if one
   was specified.

Intermediate files, calibration results, logs and book-keeping information are
saved in the general EDPS directory specified during installation (see
:doc:`installation`), *not* in the output directory.

.. tip::

   Before committing to a full reduction, it is worth running the same command
   with ``-c`` (classify only) or ``-t <task> -f`` (organise only) to see what
   EDPS makes of your data. See :doc:`options`.


Closing EDPS
------------

After the completion of the first ``edps`` command, subsequent calls will start
processing with reduced overhead. The reason for this is that EDPS starts a
**server component** that is persistent and remains running in the background
even when the processing is completed. Subsequent ``edps`` commands connect to
this server. This mechanism improves the efficiency of the processing.

Once no further processing is desired, this server can be closed with:

.. code-block:: console

   $ edps --shutdown

One can also pass the option ``-shutdown`` at every command, to close the
server after the command execution.

.. important::

   The running server also caches configuration. If you edit
   ``~/.edps/application.properties``, the changes have **no effect** until you
   shut the server down and let the next ``edps`` call start a fresh one. This
   catches almost everyone once.


Workflows for different pipelines
---------------------------------

Depending on the instrument, the workflow reduces science data in different
ways. The workflows are similar to the ones documented in detail in the
EsoReflex tutorials for each pipeline, available at
http://eso.org/pipelines/. See :ref:`workflow-graph` for how to visualise the
individual steps of the actually implemented EDPS workflows.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Instrument
     - How science data are combined
   * - ESPRESSO, UVES
     - Individual science observations are processed but **not** combined.
   * - KMOS
     - The workflow first reduces and combines together all the science data
       belonging to the same Observing Block, then combines the results that
       refer to the same target name and instrument setup.
   * - MUSE
     - The workflow first reduces exposures separately, then combines them
       according to a preference expressed by the user: data from the same
       Observing Block, data of the same target name, or data that fall within
       a certain distance on the sky (default).

EDPS processes the data following a default reduction strategy and using
certain values for the recipe parameters (whose defaults can vary depending on
the type of input data). It is possible to customise the reduction strategy by
changing the values of the recipe parameters, and eventually by activating or
de-activating some reduction steps according to the science needs. All these
options are instrument-dependent; see :doc:`customising`.
