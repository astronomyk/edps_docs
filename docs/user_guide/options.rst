Most useful options
===================

To get the EDPS full list of options, type on the terminal where the EDPS
environment is active:

.. code-block:: console

   $ edps -h

The complete, annotated list is in :doc:`../reference/cli`. In the following
sections we describe the most useful options.


.. _workflow-graph:

Graphic representation of a workflow
------------------------------------

One convenient way to understand a workflow is to look at a graphical
representation. EDPS supports **2 levels** of graphic display:

* ``-g`` — the *general graph*: shows datasets, tasks, and subworkflows.
* ``-g2`` — the *detailed graph*: shows tasks, subworkflows, the input
  categories and the recipes.

The graphs are produced in the `dot <https://graphviz.org/>`_ format. This
format can be converted into a large range of formats by the ``dot`` program.
This program needs to be installed separately and is available in all commonly
used Linux and macOS versions.

For example, to produce a workflow graph for the ESPRESSO workflow in PDF
format, type from a terminal where the ``edps`` environment is active:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -g | dot -Tpdf > espresso.pdf

For ``.ps`` or ``.png`` format, use ``-Tps`` or ``-Tpng`` respectively.

The program ``dot`` has many options that can be used to produce presentations
of the workflow depending on the preferences of the user. For example, to
produce a detailed workflow graph for the ESPRESSO workflow, type (single-line
command):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -g2 | dot -Tpdf -O

This generally produces several output files, one with the workflow and the
other ones with details of each sub-workflow. [#f1]_ A convenient way to merge
the various created files into a single PDF file is:

.. code-block:: console

   $ gs -sDEVICE=pdfwrite -sOutputFile=espresso.pdf -dNOPAUSE -dBATCH noname*pdf
   $ rm noname*pdf

.. rubric:: Footnotes

.. [#f1] If a workflow does not contain any sub-workflows, then only one file
   is generated, i.e. ``noname.gv.pdf``. In this case, the file can simply be
   renamed without the need to merge multiple PDF files.


Classification of input data
----------------------------

To show only the classification of the input data, type from a terminal where
the ``edps`` environment is active:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -c

EDPS inspects the ``<input_directory>`` recursively, and prints a list of the
FITS files and their classifications. In general, a file can have more than one
classification.

This is the cheapest possible sanity check on a new dataset: it touches no
recipes and takes seconds.


.. _target-task:

Reducing data until a certain step
----------------------------------

EDPS can perform the reduction up to a certain processing step, which we call
the **target task**. Only input data related to that task (and needed
calibrations) will be processed.

To reduce data until the task ``flat``, i.e. reduction of flat field raw
calibrations (single-line command):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -t flat -o <output_directory>

To see the list of processing tasks, type on the terminal where the EDPS
environment is active:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -lt

A list of tasks grouped by the so-called **metatargets** is shown.

To process data of the tasks that belong to the same metatarget (single-line
command):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -m <METATARGET> -o <output_directory>

For example:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -m qc1calib -o <output_directory>

executes only calibration tasks.

.. note::

   By default, if no target tasks or metatargets are specified, EDPS assumes the
   default option ``-m science``, i.e. all science tasks are considered targets
   of the reduction.

.. note::

   When the output directory is specified with the ``-o`` option, only the
   products of the (meta)target tasks are saved into the final directory. All
   other products, including logs and book-keeping, are stored in the general
   EDPS data directory, as specified during the configuration (see
   :doc:`installation`).

.. seealso::

   The predefined metatargets and what each is for are listed in
   :ref:`metatargets`.


.. _inspect-cascade:

Inspecting the cascade without reducing
---------------------------------------

By default, if a workflow and the input data directories are specified, EDPS
organises the data into datasets and processes them, according to the
(meta)target tasks.

It is possible to **stop at the data organisation**, and visualise the content
of the datasets, with the option ``-f``. The data organisation is done up to the
(meta) target tasks (default is ``-m science``, i.e. all the science tasks).

To perform the data organisation only, up to a certain task type (for example,
up to the flat fielding):

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -t flat -f

One can direct the output (JSON format) to a file and open it with a browser:

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i <input_directory> -t flat -f > flat_field_datasets.json
   $ firefox flat_field_datasets.json

Notes:

* With the option ``-f``, the datasets are organised in a **tree-like
  structure**. If one replaces ``-f`` with ``-od``, then each job is displayed
  independently with more information, but the associations between the various
  calibrations are not highlighted.

* If the ``-od`` and ``-f`` options are omitted in the previous example, EDPS
  **processes** all the flat fields (and needed calibrations) in the input
  directory. The steps after the reduction of flat fields are not executed.

.. tip::

   ``-a`` (``--assocmap``) prints the association map in Markdown format. It is
   not mentioned in the source manual but is often the fastest way to see, at a
   glance, which calibration got attached to which science frame and why a job
   is incomplete.
