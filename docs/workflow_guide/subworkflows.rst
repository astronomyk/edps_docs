Subworkflows
============

General concepts
----------------

EDPS allows the inclusion of **subworkflows** within a workflow. Subworkflows are
the equivalent of sub-routines in a program, and therefore they can be a useful
way to "isolate" a portion of the reduction cascade with precise input/output.

Also, a subworkflow:

* can be **reused** in the same or in other workflows;
* can be used to **hide** part of the reduction chain, which might contain a
  number of steps but only the final task(s) are needed in the rest of the
  reduction cascade;
* can be used to **simplify** the overall workflow structure, as the subworkflow
  appears as a single block.

.. important::

   All the tasks in a workflow, including those in the subworkflow, must have
   **unique names**. Therefore, if the same subworkflow is used several times
   within a workflow, it must be inserted so that task names are unique.

   In practice this means parameterising the task name — see the
   ``bias_arm(raw_bias, tag)`` pattern in :doc:`../examples/compact`, where the
   task is named ``'bias_' + tag``.


Example
-------

Example extracted from the MUSE workflow. A subworkflow is declared with the
``@subworkflow`` decorator on a function that builds and returns the task(s) the
rest of the cascade needs.

.. code-block:: python
   :caption: muse_wkf.py
   :linenos:

   from .muse_response import process_standard
   [...]
   # --- Subworkflow to generate response curve and telluric correction
   response = process_standard(bias, dark, lamp_flat, wavelength, geometry_calibrations,
                               sky_flat)

.. code-block:: python
   :caption: muse_response.py
   :linenos:

   from edps import subworkflow, task

   # This subworkflow reduces standard star observations and produces
   # response curve and telluric correction

   @subworkflow("response", "")
   def process_standard(bias, dark, lamp_flat, wavelength, geometry_calibrations, sky_flat):

       # --- Pre-process standard star raw calibrations
       standard = (task("preprocess_standard")
                   .with_recipe("muse_scibasic")
                   .with_main_input(raw_std)
                   .with_associated_input(badpix_table, min_ret=0)
                   .with_associated_input(bias, [MASTER_BIAS])
                   .with_associated_input(lamp_flat, [TRACE_TABLE, MASTER_FLAT])
                   .with_associated_input(wavelength, [WAVECAL_TABLE])
                   .with_alternatives(geometry_calibrations)
                   .with_associated_input(sky_flat, [TWILIGHT_CUBE], min_ret=0)
                   .with_associated_input(raw_flat_illum, min_ret=0)
                   .build())

       # --- Generation of response curve and telluric correction
       response = (task("response")
                   .with_recipe("muse_standard")
                   .with_main_input(preprocess_standard)
                   .with_associated_input(extinct_table)
                   .with_associated_input(std_flux_table)
                   .with_associated_input(telluric_regions, min_ret=0)
                   .with_associated_input(filter_list, min_ret=0)
                   .with_meta_targets([QC0, CALCHECKER, QC1_CALIB])
                   .build())

       return response

The subworkflow takes the upstream tasks it depends on as **function arguments**
and returns only the task the caller needs (``response``). The intermediate
``preprocess_standard`` task still runs, and still appears in the detailed graph
(``-g2``), but it does not clutter the top-level workflow.

.. note::

   In the graphical representation (``-g``), a subworkflow appears as a single
   orange block. See the ``demo2`` figure description in
   :doc:`../examples/compact`.
