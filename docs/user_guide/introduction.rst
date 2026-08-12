Introduction
============

What is EDPS?
-------------

The ESO Data Processing System (EDPS) is a framework to run ESO's data
processing pipelines. It is meant to eventually replace the previous
`EsoReflex environment <https://www.eso.org/sci/software/esoreflex/>`_.

The general principles of EDPS have been described by Freudling, Zampieri,
Coccato et al. (`2024, A&A, 681, A93
<https://doi.org/10.1051/0004-6361/202347058>`_). Please refer to that paper if
you have used EDPS for research resulting in a scientific publication.

Each of ESO's data processing pipelines consists of a series of standalone
programs called **recipes**. Each recipe is designed to process certain type(s)
of input data. The processing of these input data typically requires a range of
auxiliary files such as calibration files. EDPS is designed to select
appropriate input data for the different recipes of a pipeline, and execute
them in sequence.

This is done by specifying, for each pipeline, a **workflow** for organising
data and executing the recipes. A workflow can be used to process a set of data
fully automatically.


The mental model
----------------

Three concepts carry most of the weight, and they recur throughout this guide:

**Data source**
   A description of a kind of input file — raw biases, raw flats, a static
   catalogue. It says which files belong together and how they should be
   matched to the data that need them.

**Task**
   One step in the reduction cascade. A task takes a main input, attaches the
   calibrations it needs, and runs one recipe. Tasks are the things you name
   when you want to stop the reduction early (``-t``) or set a recipe parameter
   (``-rp``).

**Job**
   One concrete execution of a task, on one specific group of files. A task
   that has five sets of biases to reduce produces five jobs.

A job that is missing a required calibration is marked **incomplete** and is not
executed. Most "nothing happened" problems come down to an incomplete job; see
:doc:`faq`.


Scope of this guide
-------------------

This guide covers *using* EDPS with the workflows that ship with ESO pipelines.
It does not cover writing or modifying workflows — for that, see the
:doc:`../workflow_guide/index`.
