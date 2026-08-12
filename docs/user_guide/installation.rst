Installation
============

Prerequisites
-------------

EDPS requires **Python 3.9** (recommended) or higher. Linux and macOS are
supported. Check your Python version with:

.. code-block:: console

   $ python --version

EDPS is pre-configured to run workflows for ESO data reduction pipelines. Only
pipelines that include an EDPS workflow can be used by EDPS. As of the source
manual, the ESPRESSO, UVES and KMOS pipelines include such a workflow; the
up-to-date list is maintained at
https://www.eso.org/sci/software/pipelines/, which is also where you install
the instrument pipeline from.

The pipeline recipe executer ``esorex``, which is installed automatically with
the pipeline, must be on your ``PATH`` so that EDPS can find the pipelines:

.. code-block:: console

   $ which esorex

This should return the full path to the installed ``esorex`` binary.

.. important::

   EDPS will see **only** the workflows of the pipelines associated with that
   ``esorex`` binary. If you have several pipeline installations, the one on
   your ``PATH`` decides which workflows exist. This is the single most common
   cause of a "workflow not found" error.


Installation procedure
----------------------

There are two main ways to install EDPS: with Homebrew (recommended), or into a
Python virtual environment. A conda recipe is given at the end of this page.

.. tab-set::

   .. tab-item:: Homebrew (recommended)

      1. **Install Homebrew.** Refer to the `official documentation
         <https://brew.sh>`_; the installation is as simple as running the
         following in your macOS Terminal or Linux shell prompt:

         .. code-block:: console

            $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

         Then follow the instructions on the terminal about how to add
         Homebrew to your path.

      2. **Set up the ESO repository.** This adds a custom Homebrew repository
         (a *Tap*) containing the pipeline packages:

         .. code-block:: console

            $ brew tap eso/pipelines

      3. **Install EDPS:**

         .. code-block:: console

            $ brew install edps

      4. **Install a pipeline** (ESPRESSO, in this example):

         .. code-block:: console

            $ brew install esopipe-espdr

      To uninstall EDPS later:

      .. code-block:: console

         $ brew uninstall edps

   .. tab-item:: Python virtual environment

      From a bash shell:

      1. **Define a new environment** named ``edps``, where
         ``<path_to_environment>`` is a directory where the environment is to
         be saved:

         .. code-block:: console

            $ python3 -m venv <path_to_environment>/edps

      2. **Activate the environment:**

         .. code-block:: console

            $ . <path_to_environment>/edps/bin/activate

         .. note::

            For csh or tcsh shells use
            ``source <path_to_environment>/edps/bin/activate.csh``, and for
            the fish shell use
            ``source <path_to_environment>/edps/bin/activate.fish``.

      3. **Upgrade pip:**

         .. code-block:: console

            $ pip install --upgrade pip

      4. **Install EDPS** (single-line command):

         .. code-block:: console

            $ pip install --extra-index-url https://ftp.eso.org/pub/dfs/pipelines/repositories/stable/src edps adari_core

   .. tab-item:: conda

      Assuming that conda is installed and activated:

      1. **Define a new conda environment** named ``edps``:

         .. code-block:: console

            $ conda create -n edps python=3.10

      2. **Activate it:**

         .. code-block:: console

            $ conda activate edps

      3. **Upgrade pip:**

         .. code-block:: console

            $ python -m pip install --upgrade pip

      4. **Install EDPS** (single-line command):

         .. code-block:: console

            $ python -m pip install --extra-index-url https://ftp.eso.org/pub/dfs/pipelines/libraries edps adari_core

      To remove the environment at any time:

      .. code-block:: console

         $ conda env remove --name edps

.. warning::

   If this is a re-installation, make sure that the EDPS server is not running
   in the background. To close the EDPS server, type ``edps -shutdown``.
   Alternatively it can be killed with the usual Linux commands.


First run: EDPS configuration
-----------------------------

Once EDPS has been installed, it can be run with:

1. If EDPS was **not** installed via Homebrew, activate the ``edps``
   environment first:

   .. code-block:: console

      $ . <path_to_environment>/edps/bin/activate

2. Run EDPS:

   .. code-block:: console

      $ edps

The first time EDPS is executed, it will ask for a location where intermediate
data products, bookkeeping information and logs will be stored. This should be
a location with **sufficient disk space** to store the output data for several
executions of the pipeline, and it needs full write permission.

.. code-block:: text

   ### EDPS has not been initialised on this system. Creating initial configuration
   Enter EDPS bookkeeping directory where intermediate products are stored [~/EDPS_data]:

This location is stored in ``~/.edps/application.properties`` and used for
further calls of EDPS. **EDPS will exit after this initial setup** — run the
``edps`` command again to start reducing data.

To reconfigure later, edit ``~/.edps/application.properties`` (see
:doc:`configuration`), or delete the ``~/.edps`` directory and repeat the
configuration step.


Updating EDPS
-------------

Once EDPS is installed, it can be updated as follows.

.. tab-set::

   .. tab-item:: Homebrew

      .. code-block:: console

         $ brew update && brew upgrade edps

   .. tab-item:: Python virtual environment

      Activate the previously defined ``edps`` environment:

      .. code-block:: console

         $ . <path_to_environment>/edps/bin/activate

      Then (single-line command):

      .. code-block:: console

         $ pip install --upgrade --extra-index-url https://ftp.eso.org/pub/dfs/pipelines/repositories/stable/src edps adari_core

.. warning::

   As for a re-installation, make sure the EDPS server is not running in the
   background before updating: ``edps -shutdown``.


Verifying the installation
--------------------------

Two quick checks confirm that EDPS and the pipelines can see each other:

.. code-block:: console

   $ edps -lw

lists the workflows EDPS has found. If your instrument is missing, EDPS is
looking at the wrong ``esorex``; see :doc:`faq`.

.. code-block:: console

   $ esorex --recipes

lists the recipes that ``esorex`` can see. If your instrument's recipes are not
there, the pipeline installation itself is the problem.
