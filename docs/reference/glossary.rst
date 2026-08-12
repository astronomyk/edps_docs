Glossary
========

.. glossary::
   :sorted:

   association
      The process by which EDPS attaches the right calibrations to the data that
      need them, following :term:`association rules <association rule>`.

   association rule
      A criterion a file must satisfy to be attached to a task's main input.
      Either a list of header keywords that must match
      (``.with_match_keywords()``) or a function the files must obey
      (``.with_match_function()``).

   association preference
      The ``application.properties`` setting that decides whether EDPS prefers
      raw or master calibrations when both would match. One of ``raw``,
      ``master``, ``raw_per_quality_level`` (default) or
      ``master_per_quality_level``.

   base_dir
      The EDPS data directory (default ``~/EDPS_data``) where all recipe
      products, logs, quality-control plots and bookkeeping are stored. Distinct
      from the ``-o`` output directory. Must not be deleted.

   bookkeeping
      The record EDPS keeps of what has already been reduced, allowing it to
      reuse products instead of re-running recipes. Stored in a TinyDB database
      under :term:`base_dir`.

   classification
      Assigning a tag to a FITS file based on its header keywords, so that EDPS
      knows what kind of data it is.

   classification rule
      A tag plus either a dictionary of keyword/value pairs the file must have,
      or a function expressing more complex conditions.

   cluster
      A group of files collected by *closeness* of a parameter rather than exact
      match — e.g. all exposures within 0.05 degrees on the sky. Set with
      ``.with_cluster()``.

   data source
      A description of a class of input files: which files belong together
      (classification and grouping), and how they are matched to the data that
      need them (association rules).

   dataset
      A set of related data organised by EDPS for processing, named after the
      first FITS file that triggers the recipe.

   dynamic parameter
      A workflow parameter whose value is computed at run time from the
      properties of a job's main input, via
      ``.with_dynamic_parameter(name, fn)``. Used to drive conditional
      associations.

   EDPS
      ESO Data Processing System. The framework that runs ESO's data-reduction
      pipelines, successor to :term:`EsoReflex`.

   EsoReflex
      The previous ESO data-reduction environment, which EDPS is meant to
      eventually replace.

   esorex
      The pipeline recipe executer, installed with each pipeline. EDPS sees only
      the workflows of the pipelines associated with the ``esorex`` on the
      ``PATH``.

   grouping
      Collecting files of the same classification into a job, on the basis of
      matching header keywords. Set with ``.with_grouping_keywords()``.

   incomplete job
      A job missing one or more required associated inputs. Incomplete jobs are
      marked as such and **not executed**. The most common cause of "nothing
      happened".

   job
      One concrete execution of a :term:`task`, on one specific group of files. A
      task with five sets of biases to reduce produces five jobs.

   metatarget
      A label attached to a task that groups related tasks, so that they can be
      selected together with ``-m``. Predefined: ``qc1calib``, ``qc0``,
      ``science``, ``calchecker``, and (in EDPS 1.7.1) ``qc1science``, ``idp``,
      ``phase3``.

   min_ret / max_ret
      The minimum and maximum number of associated inputs of a given type a task
      requires. Both default to 1; ``min_ret=0`` makes the input optional.

   quality level
      A number attached to an association rule indicating the expected quality of
      the resulting products. By convention: ``< 0`` more restrictive than the
      calibration plan; ``0`` follows the calibration plan; ``1`` sufficient for
      QC1 certification; ``2`` probably still acceptable; ``3`` significant risk
      of bad results.

   recipe
      A standalone program that is part of an ESO pipeline, designed to process
      one type of input data. Executed by :term:`esorex`.

   recipe parameter
      A parameter passed to a pipeline recipe. Specified with the full name
      ``<instrument>.<recipe>.<alias>``, set via ``-rp``, the parameter file, a
      job function, or left at the recipe default.

   reduction cascade
      The ordered sequence of tasks that transforms raw data into final
      products.

   set of frames (sof)
      The list of input files, with their category tags, that is handed to a
      recipe.

   smart re-run
      EDPS's reuse of existing products from :term:`base_dir` instead of
      re-executing a recipe whose inputs and parameters have not changed.

   subworkflow
      A reusable block of tasks, declared with the ``@subworkflow`` decorator,
      that appears as a single element in the workflow graph. Task names within
      it must still be globally unique.

   target task
      The task at which the reduction should stop, selected with ``-t``. Only
      input data related to that task, and the calibrations it needs, are
      processed.

   task
      One step in the reduction cascade: a main input, some associated inputs,
      and a recipe (or Python function) to execute. Generates one or more
      :term:`jobs <job>`.

   validity range
      The time window, relative to the file needing the association, within
      which a calibration is considered valid. Defined with
      ``RelativeTimeRange(-M, N)`` or one of the predefined constants.

   workflow
      The complete description, for one pipeline, of how to organise data and
      execute the recipes. A Python package of several files, named
      ``<instrument>.<instrument>_wkf``.

   workflow parameter
      A parameter that controls the *strategy* of the reduction rather than a
      recipe's behaviour — which steps run, which calibrations are used. Set via
      ``-wp`` or the parameter file.
