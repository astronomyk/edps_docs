Anatomy of a workflow
=====================

An EDPS workflow contains all the components that allow files to be classified
and grouped together for processing, ensuring the correct sequence of recipes
with appropriate input/output relations.

We adopt the convention to store these different components into **separate
files**, entwined by import statements. Therefore, a workflow "package" consists
of several Python files.


The files of a workflow package
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - File
     - Contents
   * - ``instrument_wkf.py``
     - **The list of tasks** (a.k.a. main workflow). The ``_wkf`` suffix is
       mandatory. An instrument can have more than one workflow; their names
       must start with the instrument name and end with the ``_wkf`` suffix
       (e.g. ``fors_wkf.py``, ``fors_spec_wkf.py``, ``fors_imaging_wkf.py``).
   * - ``instrument_datasources.py``
     - **The data sources**, that are the inputs of the various tasks. The list
       of datasources and the list of tasks entirely define the workflow. See
       :doc:`data_sources`.
   * - ``instrument_classification.py``
     - **The classification statements**, used to define a datasource. It
       contains the ``classification_rules`` objects. Files are classified by
       these classification statements, which obey some rules. The rules are
       either defined explicitly within the ``classification_rules`` object
       (for simple rules), or defined in the rules file (for more complex
       rules). See :doc:`classification`.
   * - ``instrument_rules.py``
     - **The rules**: functions that allow the classification and association of
       files. See :ref:`rules-file`.
   * - ``instrument_keywords.py``
     - **The definition of header keywords.** Classification and association
       rules use header keywords to classify and associate files. Typically,
       rules use strings or lists of strings containing header keywords. It is
       convenient to define variables equal to those strings. In this way, the
       variable is defined once and it is easier to spot syntax issues when
       using a Python development environment (e.g. PyCharm).
   * - ``instrument_task_functions.py``
     - **Auxiliary functions** that are required by tasks (job-editing
       functions, functions for association conditions, dynamic parameters), if
       any. See :doc:`advanced_tasks`.
   * - ``instrument_parameters.yaml``
     - **Workflow and task parameters**, in YAML format. See
       :doc:`parameters`.
   * - subworkflow file(s)
     - The file(s) with subworkflows, if any. See :doc:`subworkflows`.

.. note::

   The names above are conventions, not hard requirements — with two
   exceptions. The main workflow file **must** end in ``_wkf.py``, and it must
   live in a directory named after the instrument, because that is how EDPS
   derives the workflow name ``instrument.instrument_wkf``.


Example of a basic workflow
---------------------------

A workflow is entirely defined by its **data sources** (i.e. inputs) and
**tasks** (i.e. processing steps). The following is an example of a basic
workflow, composed only by the tasks and data sources which are specified in
two separate files.

.. code-block:: python
   :caption: demo0_datasources.py
   :linenos:

   from edps import data_source

   # --- Raw types datasources ---------------------------------------------
   raw_bias = (data_source('BIAS')
               .build())

   raw_flat = (data_source('FLAT')
               .build())

   raw_science = (data_source('OBJECT')
                  .build())

   raw_sky = (data_source('SKY')
              .build())

   # Catalogue of standard stars
   static_catalog = (data_source("catalog")
                     .build())

.. code-block:: python
   :caption: demo0_wkf.py
   :linenos:

   from edps import task
   from .demo0_datasources import *

   # --- Processing tasks --------------------------------------------------

   # - Task for processing raw biases
   bias_task = (task('bias')
                .with_main_input(raw_bias)
                .build())

   # - Task for processing raw flats
   flat_task = (task('flat')
                .with_main_input(raw_flat)
                .with_associated_input(bias_task)
                .build())

   # - Task for processing science exposures
   science_task = (task('object')
                   .with_main_input(raw_science)
                   .with_associated_input(raw_sky, min_ret=0)  # sky is an optional input
                   .with_associated_input(bias_task)
                   .with_associated_input(flat_task)
                   .with_associated_input(static_catalog)
                   .build())

So far, the workflow contains only the link between the processing steps and the
inputs. It does not contain any instruction on how to classify the files, nor
how to associate them, nor which file belongs to which data source, nor the
recipe to be executed.

It is, however, a **self-contained entity** that defines the data reduction flow
shown below. To obtain the graphical representation of a workflow (e.g.
``demo0``), type from a terminal where the EDPS environment is active:

.. code-block:: console

   $ edps -w demo.demo0_wkf -g | dot -Tpng > demo0.png

.. code-block:: text
   :caption: The structure that ``demo0_wkf`` describes

    Raw Types
    ┌──────────────────────────┐
    │  OBJECT   FLAT    BIAS   │
    └────┬────────┬───────┬────┘
         │        │       │
         │        │       ▼
         │        │    ( bias )
         │        │     │    │
         │        ▼     ▼    │
         │      ( flat )     │      Static Calibrations
         │         │         │      ┌──────────────────┐
         │         │         │      │ catalog    SKY   │
         ▼         ▼         ▼      └────┬─────────┬───┘
        ────────( object )◄─────────────┴─────────┘

EDPS has other options for visualising a workflow which are described in detail
in :ref:`workflow-graph`.


Building up from here
---------------------

The rest of this guide adds, in order:

1. :doc:`tasks` — recipes, optional inputs, metatargets, input/output filters.
2. :doc:`data_sources` — grouping, clustering, naming.
3. :doc:`classification` — how files get their tags, and how calibrations get
   matched to the data that need them.
4. :doc:`parameters` — the YAML parameter file.

Then the advanced material: :doc:`advanced_tasks`, :doc:`functions`,
:doc:`advanced_associations` and :doc:`subworkflows`.

The complete, runnable versions of these examples are in
:doc:`../examples/index`.
