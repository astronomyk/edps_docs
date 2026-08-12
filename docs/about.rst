About this documentation
========================

This site is an unofficial, community-maintained HTML rendering of ESO's EDPS
manuals. ESO distributes the EDPS documentation as PDF only; this project
converts that material into a searchable, linkable, version-controlled site.


Source material
---------------

The content is derived from two ESO documents, both classified *Public*:

.. list-table::
   :header-rows: 1
   :widths: 40 12 18 30

   * - Document
     - Version
     - Released
     - Rendered here as
   * - *ESO Data Processing System (EDPS) Tutorial*
     - 0.9.7
     - 2024-12-20
     - :doc:`user_guide/index`
   * - *EDPS workflow design tutorial* (draft)
     - 0.8
     - 2023-12-01
     - :doc:`workflow_guide/index`, :doc:`examples/index`

Both are by **L. Coccato, W. Freudling and S. Zampieri** (ESO, Science Data
Quality Group). Copyright in the original text remains with the European
Southern Observatory.

The official landing page for EDPS is https://www.eso.org/sci/software/edps.html.


What has been added
-------------------

The :doc:`reference/index` section is **not** a transcription. It was generated
by introspecting an actual EDPS installation, and it is marked throughout with
the version it was taken from:

.. admonition:: Verified against
   :class: note

   EDPS **1.7.1**, installed from
   ``https://ftp.eso.org/pub/dfs/pipelines/repositories/stable/src``.

This matters because the manuals lag the software. The tutorial PDF was written
against EDPS 1.3.3, and a number of things have changed since — the
``application.properties`` file is now split into INI-style sections, the
default execution ordering is ``bfs`` rather than ``dfs``, and there are
command-line options (``-a``, ``-rj``, ``-x``, ``-rt``) that the manuals do not
mention at all. Where the reference and the tutorial disagree, the reference
reflects what the software actually does.

A handful of transcription-level corrections have also been made to the
narrative chapters, each flagged inline with a note. These are cases where the
PDF example would not run as printed — for example ``.with_group_keywords()``,
which does not exist; the method is ``.with_grouping_keywords()``.


Corrections and contributions
-----------------------------

Errors in this rendering are the responsibility of this project, not of ESO.
Please open an issue or pull request against the repository.

For questions about EDPS itself — bugs, unexpected reduction results, missing
workflows — contact ESO directly rather than this project; see
:doc:`user_guide/support`.


Licence
-------

The original ESO manuals are public documents. This rendering is provided in
the same spirit: freely usable, with attribution to ESO and to the original
authors.
