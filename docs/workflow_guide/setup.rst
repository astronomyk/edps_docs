Development setup
=================

A comprehensive tutorial on how to install and execute EDPS is available at
https://www.eso.org/sci/software/edps.html, and rendered here as the
:doc:`../user_guide/installation` page.

The default installation is designed to detect and execute workflows that come
with instrument pipelines. From a **workflow development** point of view it is
recommended to edit the EDPS configuration file ``application.properties``,
located in the ``$HOME/.edps`` directory, so that any workflow under development
(also those not associated to a pipeline) can be seen by EDPS.

The fields to modify are:

``workflow_dir``
   This should point to a directory containing all the workflow files. The
   directory should be structured so that it contains sub-directories named
   after the instrument, that contain the corresponding workflows. For example,
   a directory structure:

   .. code-block:: text

      /home/user/edps_workflow/
                  instr1/
                  instr2/

   shall contain the workflows ``instr1_wkf.py``, ``inst2_wkf.py`` in the
   corresponding directories (along with all the other relevant workflow files,
   see :doc:`overview`).

   The command [#f1]_

   .. code-block:: console

      $ edps -lw

   should prompt the following list:

   .. code-block:: python

      ["instr1.instr1_wkf", "instr2.instr2_wkf"]

``esorex_path``
   This should point to the ``esorex`` installation that is linked to the
   pipeline one has to prepare the workflow for.

.. rubric:: Footnotes

.. [#f1] The EDPS environment should be activated from the terminal where the
   command is launched; see :doc:`../user_guide/installation` for detailed
   instructions.

.. warning::

   Changes to ``application.properties`` only take effect after the EDPS server
   is restarted: ``edps -shutdown``. During workflow development you will be
   doing this constantly — it is worth defining a shell alias.
