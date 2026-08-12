Frequently asked questions
==========================

.. dropdown:: I get "workflow not found", and/or nothing happens after I submitted the ``edps`` command with my workflow. How do I fix it?
   :open:

   This should not happen if the recommended installation procedures for EDPS
   and pipelines have been followed. If the installation was done in a
   non-standard way, the "workflow not found" message could indicate that:

   * the ``esorex`` command is not associated to the instrument pipeline you
     want to use;
   * the installed pipeline does not have an EDPS workflow yet;
   * the workflow name is misspelled.

   Type the command:

   .. code-block:: console

      $ esorex --recipes

   to check which pipeline is seen by ``esorex``. If there are no recipes for
   your instrument, it means that the path in ``application.properties`` points
   to the wrong ``esorex`` installation. Fix it and restart the EDPS server.

   Type the command:

   .. code-block:: console

      $ edps -lw

   to list the installed workflows. If the workflow is not present, please
   check the spelling or the workflow directory in the
   ``application.properties`` file. See :doc:`configuration`.

.. dropdown:: The association reveals that my datasets are not complete, but I think I have all the needed data. How do I fix it?

   It could be that EDPS could not find the location of static calibrations for
   that instrument pipeline (this could happen, for example, if the instrument
   pipeline was not installed following the recommended procedures). Try to add
   the static calibration directory to the list of input data via the ``-i``
   option.

.. dropdown:: I do not remember the name of the workflow I want to run. How do I know the exact workflow names?

   EDPS workflows are installed together with the instrument pipeline
   installation. To see which are the workflows installed in your system and
   their names, type:

   .. code-block:: console

      $ edps -lw

.. dropdown:: I edited the configuration file ``application.properties``, but this seems to have no effect. Why?

   In order for the changes to take effect, first close the EDPS server by
   typing the command ``edps -shutdown``, and then relaunch the request.

   The server is persistent and caches its configuration at startup, so a
   running server will happily keep using the old settings.

.. dropdown:: How do I know which recipe parameters were or will be used?

   The book-keeping directory has the file ``parameters.rc``, which indicates
   only the values of the recipe parameters that are **different from the recipe
   default**. The products have record of the recipe parameters values in their
   header.

   For inspecting the parameter values that are going to be used in the
   reduction *before* the reduction starts, consult
   :ref:`display-parameters`.

.. dropdown:: How do I stop EDPS re-using products from a previous run?

   EDPS deliberately reuses products from the bookkeeping directory rather than
   re-executing a recipe ("smart re-run"). To force a full re-execution, set
   ``truncate=True`` in ``application.properties`` and restart the server. See
   :doc:`configuration`.

.. dropdown:: Where are my quality-control plots?

   In the EDPS data directory (default ``~/EDPS_data``), inside the job
   directory for the relevant task execution — one level below the products
   themselves. They are **not** copied into the ``-o`` output directory, which
   receives FITS products only. See :doc:`outputs`.
