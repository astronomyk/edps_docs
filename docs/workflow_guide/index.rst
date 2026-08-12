Workflow Developer Guide
========================

This guide provides instructions and examples on how to write EDPS workflows
for ESO pipelines.

.. important::

   This section is **not** intended for users who want to reduce data with the
   standard workflow for a supported pipeline. Supported pipelines are
   distributed with fully functional workflows — see the :doc:`../user_guide/index`
   instead.

This guide is mainly for developers of pipelines and for users who want to
modify existing EDPS workflows. It assumes that the reader is familiar with the
basic concepts behind EDPS workflows.

EDPS workflows are written in **Python**. The EDPS libraries must be used to
write a functional workflow. These libraries leave the developer with
significant choices for the design of workflows. The official workflows are
written using the same conventions for all instrument pipelines; those
conventions are described here.

.. note::

   The upstream source for this section is version 0.8 of the *EDPS workflow
   design tutorial*, which ESO marks as a draft. Method names and constants
   have been checked against EDPS 1.7.1 and corrections are flagged inline.

.. toctree::
   :maxdepth: 2

   setup
   overview
   tasks
   data_sources
   classification
   parameters
   advanced_tasks
   functions
   advanced_associations
   subworkflows
   debugging
   testing
