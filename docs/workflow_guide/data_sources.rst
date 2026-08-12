Data sources
============

Data sources are the inputs of a task. They specify:

* the files that have to be grouped together on the basis of some classification
  rules;
* the criteria by which they have to be associated to the main input of a task.

An example of a datasource is:

.. code-block:: python
   :linenos:

   raw_science = (data_source("OBJECT")
                  .with_classification_rule(science_extended_class)
                  .with_classification_rule(science_pointlike_class)
                  .with_grouping_keywords(["tpl.start", "obs.targname"])
                  .with_match_keywords(['instrume', 'ins.filt.name'])
                  .with_match_function(rules.associate_science)
                  .build())

The data source ``raw_science`` encompasses two different groups of files: those
that obey the ``science_extended_class`` classification rule, and those that obey
the ``science_pointlike_class`` classification rule. These two groups will be
processed separately.

Files are grouped according to the list of header keywords specified by
``.with_grouping_keywords()``; this applies to both classification rules, but
files from two different classifications are **not** grouped together.

``.with_match_keywords()`` and ``.with_match_function()`` specify the association
rules that this data source must obey to be associated to tasks (either a list of
keywords to match, or a more complicated function). See :doc:`classification`.

.. important::

   Datasources that are **main inputs** to a task must also have the
   ``.with_setup_keywords()`` method declared. This list of keywords is used by
   QCFlow for the scoring.

The order of the datasources defined in the datasource file should follow the
calibration cascade. Datasources based on static calibrations should be done at
the end.


Using keyword variables
-----------------------

In the example above, we directly declared the header keywords to be used as
strings (e.g. ``'tpl.start'``, ``'obs.targname'``). However, it is convenient to
define these keywords in an appropriate file and use variables instead. The file
has to be imported, i.e. via:

.. code-block:: python

   from . import instrume_keywords as kwd

**Convention:** it might be convenient to create lists of keywords that are used
by many data sources. The list should include keywords of similar type and
should be named in a way that "suggests" the type of keywords there are in. For
example, one can put in the same list the keywords that refer to the detector
(if they are used together, obviously) and in another list the keywords that
refer to the spectrograph. For example:

.. code-block:: python

   detector = [kwd.instrume, kwd.det_binx, kwd.det_biny, kwd.readoutnoise]
   spectr   = [kwd.opti_ins1, kwd.ipti_slit1_width]

and the match can be done via:

.. code-block:: python

   .with_match_keywords(detector + spectr)

``kwd.instrume`` and the other keywords are defined in the keywords file. It is
up to the developer to come up with a strategy for naming and which keywords to
include in a list; every instrument might require a different solution.


Grouping and clustering of files
--------------------------------

A data source can represent different groups of files. Each group is defined by
a classification rule. The files within the same classification rule are grouped
together following the list of keywords in the method
``.with_grouping_keywords(<list>)``. The list of keywords applies to both
classification rules, but files from two different classifications are not
grouped together.

* To process files **individually**, one has to use a unique grouping keyword
  (e.g. ``arcfile`` or ``mjd.obs``).
* To process the files **all together** (of the same classification) do not
  specify the grouping method.
* If a keyword starts with the symbol ``$``, it means that it has to be read
  from a **workflow parameter**. This is useful, for example, if the files can be
  reduced following different data reduction strategies (e.g. grouping files of
  the same night, or files from the same ``tpl.start``, or individually).

Together with the grouping method, there is also the ``.with_cluster()`` method,
that allows files to be clustered together by closeness of a parameter. One can
specify the minimum and maximum threshold of the cluster method. This method is
particularly useful to collect exposures of a specific time range (e.g. a night,
regardless of their ``tpl.start``) or group files on sky coordinates.

Grouping and clustering can be both specified in the data source. Their order
reflects the order over which files are grouped or clustered.

To group data by ``tpl.start`` and ``ins.filt.name``:

.. code-block:: python
   :linenos:

   science = (data_source('OBJECT')
              .with_classification_rule(science_class)
              .with_grouping_keywords([kwd.instrume, kwd.ins_filt_name])
              .build())

To group data by ``tpl.start`` and ``ins.filt.name``, and cluster them by
position on the sky:

.. code-block:: python
   :linenos:

   science = (data_source('OBJECT')
              .with_classification_rule(science_class)
              .with_grouping_keywords([kwd.tpl_start, kwd.ins_filt_name])
              .with_cluster('SKY.POSITION', 0.001, 0.05)
              .build())

A file belongs to a cluster if the minimum distance from the elements of the
cluster is below 0.001 degrees (threshold) and if the maximum from the elements
in the cluster is below 0.05 degrees (maximum cluster size).

.. note::

   In the example above, we used variables instead of explicitly stating the
   header keywords as strings. These variables are defined in the
   ``instrument_keywords.py`` file this way:

   .. code-block:: python

      tpl_start     = "tpl.start"
      ins_filt_name = "ins.filt.name"
      instrume      = "instrume"

   that is imported with the following statement at the beginning of the
   datasource file:

   .. code-block:: python

      import instrument_keywords as kwd

.. admonition:: Correction
   :class: warning

   The source manual writes ``.with_group_keywords()`` in several examples. That
   method does not exist. The correct name, verified against EDPS 1.7.1, is
   ``.with_grouping_keywords()``. Examples on this page have been corrected;
   the raw transcription in :doc:`../examples/index` preserves the original
   text where it is quoted verbatim.


.. _min-group-size:

Minimum number of files in a group
----------------------------------

The method ``.with_min_group_size()`` specifies the minimum number of files that
has to be present in a group to be considered by the workflow. Example:

.. code-block:: python
   :linenos:

   raw_bias = (data_source("BIAS")
               .with_classification_rule(bias_class)
               .with_grouping_keywords(["tpl.start"])
               .with_min_group_size(3)
               [...]
               .build())

A few important notes:

* The method ``.with_min_group_size()`` has effect **only** for datasources that
  are main inputs of tasks. If the datasource is an associated input to a task,
  then use the keywords ``min_ret`` and ``max_ret`` in the
  ``.with_associated_input()`` method in the task itself. ``min_ret``'s and
  ``max_ret``'s default value is 1.

* There is **not** a ``.with_max_group_size()`` equivalent method. By default,
  all data fulfilling the grouping conditions are included in the group. To
  process files individually, use unique header keywords such as ``mjd.obs`` or
  ``arcfile``.


Naming a data source
--------------------

Datasources have two types of names: a **variable name** used within the workflow
and a **label name** used in the graphic representation and instrument monitor.
If the label name is not provided, EDPS automatically uses the label defined by
the classification rule attached to the data source. Because a datasource can
have more than one classification rule, it is recommended to assign a label name
if multiple classification rules are used.

Example:

.. code-block:: python
   :linenos:

   variable_name = (data_source("LABEL_NAME")
                    .with_classification_rule(rule1)
                    .with_classification_rule(rule2)
                    [...]
                    .build())

It is recommended to use consistent variable and label names: **lower case for
variables, upper case for labels**.

In the case of data sources coming from raw calibration files, the convention is
to start the variable name with the prefix ``raw_`` (e.g. ``raw_bias``).

Names of datasources should be chosen to reach a compromise between:

* understanding what the file is about;
* match of the ``DPR.TYPE`` keyword that defines the file;
* match of the ``TAG`` expected by the recipe aimed at processing it.

It is advisable to follow the naming convention of the pipeline ``DRS.TYPE`` as
close as possible, and at the same time, to use common sense to find a balance
with a self-explanatory name. For example, the datasource that corresponds to
data with ``DPR.TYPE = LMP_FMT_CHECK`` can be simply ``format_check``.

It is also recommended to use the **same label name for data sources of different
workflows** that refer to the same type of files (for example, use consistently
names such as ``BIAS``, ``SKYFLAT``, ``LAMP_FLAT``, ``ARC``, ``STANDARD_STAR``,
``OBJECT`` across different workflows). In this way, the instrument monitor will
display consistent nomenclature across instruments.


Writing the data source file
----------------------------

Import statements
~~~~~~~~~~~~~~~~~

Create a file named ``instrument_datasources.py`` (e.g. ``muse_datasources.py``),
with the following import statements:

.. code-block:: python
   :linenos:

   from edps import data_source, match_rules
   from edps.generator.time_range import *
   from .muse_classification import *
   from . import muse_keywords as kwd

Files in the workflow package that need the data source file must have the
following import statement:

.. code-block:: python

   from .muse_datasource import *

.. note::

   If one feels uncomfortable in using ``*`` for importing, an alias can be used
   (as done, for example, for the keyword and rules files).

Convention on its content
~~~~~~~~~~~~~~~~~~~~~~~~~

Each data source should have a comment explaining what it is for. Commented
symbols should separate data sources from raw data, from static calibrations, and
of other types (e.g. user-provided calibrations).

The ``datasource.py`` file should contain the datasources and the **alternative
matching rules** (if applicable) that will override those embedded in the data
source itself. The alternative matching rule(s) should be written right after the
data source it refers to.

Examples are given in :ref:`same-datasource-different-rules`.
