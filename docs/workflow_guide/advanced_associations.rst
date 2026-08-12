Associations: advanced features
===============================

.. _same-datasource-different-rules:

Same datasource, different association rules
--------------------------------------------

There could be the case where the same datasource (e.g. calibration) is required
by two different tasks using two different rules. In this case, the association
rule (or matching keywords) does not need to be specified in the datasource, but
it can be specified with a ``match_rule`` object, that is passed to the task.

.. code-block:: python
   :linenos:

   from edps import classification_rule, data_source, task, match_rule

   calibration_class = classification_rule("CALIB", {"dpr.type": CALIB})
   science_class     = classification_rule("SCIENCE", {"dpr.tpye": SCIENCE})

   raw_calibration = (data_source("CALIBRATION")
                      .with_classification_rules(calibration_class)
                      .with_grouping_keywords("arcfile")
                      .with_match_keywords(["instrume", "ins.grating", "ins.filter"],
                                           time_range=ONE_DAY)
                      .build())

   raw_science = (data_source("SCIENCE")
                  .with_classification_rule(science_class)
                  .with_grouping_keywords(["arcfile"])
                  .build())

   task1 = (task("reduction1")
            .with_recipe("recipe1")
            .with_main_input(science)
            .with_associated_input(calibration)
            .build())

   new_rule = (match_rules()
               .with_match_keywords(["instrume", "ins.filter"], time_range="ONE_MONTH"))

   task2 = (task("reduction2")
            .with_recipe("recipe2")
            .with_main_input(science)
            .with_associated_input(calibration, match_rules=new_rule)
            .build())

In the example above, the task ``reduction1`` uses the rules attached to the
calibration ``data_source`` to find a calibration for the science input. The task
``reduction2`` uses the rules defined by ``new_rule``, **overriding** those
defined in the ``data_source``.

.. note::

   The example is transcribed from the source manual and contains a few typos
   that would prevent it running as printed: ``dpr.tpye`` for ``dpr.type``,
   ``.with_classification_rules`` (singular in EDPS 1.7.1), ``time_range=
   "ONE_MONTH"`` as a string rather than the imported ``ONE_MONTH`` constant,
   and the import of ``match_rule`` where the object used is ``match_rules``.
   Read it for the pattern, not as copy-paste source.


.. _optional-mandatory-products:

Optional and mandatory products of a task
-----------------------------------------

A task (e.g. ``calibration``) can generate several products (e.g. ``MASTER1``
and ``MASTER2``), some of them might be required and other optional by one task.
They **cannot** be specified together inside the same
``.with_associated_input`` because it accepts only one ``min_ret``/``max_ret``
input. They must be associated using **alternatives**.

In the below example, the task ``science`` requires the products from the
``calibration`` task; however ``MASTER1`` is mandatory, whereas ``MASTER2`` is
optional.

.. code-block:: python
   :linenos:

   from edps import classification_rule, data_source, task, alternative_associations

   calibration_class = classification_rule("CALIB", ({"dpr.type": "CALIB"}))
   science_class     = classification_rule("SCIENCE", ({"dpr.tpye": "SCIENCE"}))

   raw_calibration = (data_source("CALIBRATION")
                      .with_classification_rules(calibration_class)
                      .with_grouping_keywords("arcfile")
                      .with_match_keywords(["instrume", "ins.filter"])
                      .build())

   raw_science = (data_source("SCIENCE")
                  .with_classification_rule(science_class)
                  .with_grouping_keywords(["arcfile"])
                  .build())

   calibration = (task("CALIBRATION")
                  .with_recipe("calibration_recipe")
                  .with_main_input(raw_calibration)
                  .build())

   # First line all calibrations. Second line only mandatory calibrations
   calibration_files = (alternative_associatiated_inputs()
                        .with_associated_input(calibration, [MASTER1, MASTER2])
                        .with_associated_input(calibration, [MASTER1]))

   science = (task("SCIENCE")
              .with_recipe("science_recipe")
              .with_main_input(science)
              .with_alternatives(calibration_files)
              .build())

In the example above we assume the association preferences to be set to
``master``:

* If both ``MASTER1`` (mandatory) and ``MASTER2`` (optional) are found, then both
  are associated.
* If only ``MASTER1`` is found, then only that one is associated and the task is
  still complete.
* If none, or if only ``MASTER2`` is found, then the task is incomplete.

If the association preference were set to ``raw``, then the raw calibrations are
processed and both products (``MASTER1`` and ``MASTER2``) are sent to the task
``SCIENCE``.

.. admonition:: Why this works
   :class: tip

   Alternatives are tried in order and stop at the first match. Listing the
   *richest* combination first and the *minimum viable* combination second means
   EDPS takes everything when everything is there, and degrades gracefully to the
   mandatory subset when it is not.

.. note::

   As above, the transcribed code contains typos —
   ``alternative_associatiated_inputs`` should be
   ``alternative_associated_inputs``, and the import line names
   ``alternative_associations``.
