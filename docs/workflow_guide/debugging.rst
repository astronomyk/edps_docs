Tips for debugging
==================

Debugging a workflow is as complicated as the data reduction cascades,
classification and association rules the workflow itself has to support. Here, we
collect some tips that could help during development and debugging. A tutorial on
how to install and run EDPS is available at
https://www.eso.org/sci/software/edps.html, and rendered here as the
:doc:`../user_guide/index`.

**Start simple!**
   First get a clear design of the various steps, i.e. the sequence of tasks and
   their inputs. A simple structure like the one shown in :doc:`overview` is the
   starting point.

**Plot it.**
   Create a plot of the workflow design and compare it to the requirements of the
   data reduction cascade(s). See :ref:`workflow-graph`.

**Add rules only after the design is ready.**
   Add classification and association rules only after the general design is
   ready.

**Advanced features last.**
   Advanced features such as conditional associations can be added after the
   overall design and classification are ready.

**Use a known pool of data.**
   Prepare a pool of data (FITS files) where the file association is known. Do the
   data classification and organisation with EDPS on those data and check if they
   match the expectation. **Header-only FITS files are sufficient for this
   purpose.** Use the option ``-f`` to do a tree-like organisation of files
   without starting the reduction (see :ref:`inspect-cascade`).

**Test from the front of the cascade.**
   Test the workflow by starting from the first task in the reduction cascade,
   not by running the full reduction chain.

**Bisect incomplete jobs.**
   If a job is found to be incomplete and there is no clear indication about what
   is missing, edit the task and add one associated input at a time. This will
   help to identify what's missing.


A practical debugging loop
--------------------------

Putting the above together, the fastest iteration cycle during development is:

.. code-block:: console

   # 1. Does EDPS see the workflow at all?
   $ edps -lw

   # 2. Does the structure look right?
   $ edps -w demo.demo_wkf -g | dot -Tpng > demo.png

   # 3. Are the files classified as expected?
   $ edps -w demo.demo_wkf -i ./test_data -c

   # 4. Are they grouped and associated as expected, without reducing anything?
   $ edps -w demo.demo_wkf -i ./test_data -t bias -f

   # 5. Only now, actually run the first task.
   $ edps -w demo.demo_wkf -i ./test_data -t bias

   # 6. After editing any workflow file or application.properties:
   $ edps -shutdown

.. warning::

   Step 6 is not optional. The EDPS server caches the loaded workflow. If you
   edit a workflow file and re-run without shutting the server down, you are
   testing the **old** workflow — and the resulting confusion can cost hours.

.. tip::

   ``-a`` (``--assocmap``) prints the association map in Markdown, which is
   usually the quickest way to see exactly which calibration was attached to
   which trigger and at what quality level. It is not documented in the source
   manual. See :doc:`../reference/cli`.

Once the workflow behaves as intended by hand, encode those expectations as
regression tests — see :doc:`testing`.
