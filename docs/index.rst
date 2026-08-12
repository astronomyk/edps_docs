EDPS — ESO Data Processing System
=================================

The **ESO Data Processing System (EDPS)** is the framework that runs ESO's
data-reduction pipelines. It classifies your raw FITS files, works out which
calibrations belong with which science exposures, and then executes the
pipeline recipes in the right order — automatically, from a single command.

.. code-block:: console

   $ edps -w espresso.espresso_wkf -i /path/to/raw_data -o /path/to/products

EDPS is the successor to the EsoReflex environment. The design principles
behind it are described in `Freudling, Zampieri, Coccato et al. (2024, A&A,
681, A93) <https://doi.org/10.1051/0004-6361/202347058>`_ — please cite that
paper if EDPS contributed to a publication.

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: :octicon:`rocket` I want to reduce data
      :link: user_guide/index
      :link-type: doc

      Install EDPS, run your first reduction, find your products, and tune the
      reduction to your science case.

   .. grid-item-card:: :octicon:`tools` I want to write a workflow
      :link: workflow_guide/index
      :link-type: doc

      Build EDPS workflows for a pipeline: tasks, data sources, classification
      and association rules, subworkflows, and testing.

   .. grid-item-card:: :octicon:`book` Worked examples
      :link: examples/index
      :link-type: doc

      Two complete workflows, built up from a plain reduction cascade to a
      compacted design with conditional associations.

   .. grid-item-card:: :octicon:`list-unordered` Reference
      :link: reference/index
      :link-type: doc

      Every command-line option, every ``application.properties`` setting, the
      builder API, validity ranges, and a glossary.


Where to start
--------------

If you have never used EDPS before, work through the
:doc:`user_guide/index` in order. It walks from installation to a complete
ESPRESSO reduction using the demo data shipped with the pipeline, and takes
about an hour.

If you already reduce data with EDPS and want to adapt or write a workflow for
a pipeline, go to the :doc:`workflow_guide/index`.


.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   user_guide/index
   workflow_guide/index
   examples/index
   reference/index
   about
