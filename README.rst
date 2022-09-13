=======================================
 repolite: git repo dependency manager
=======================================

A lightweight tool to manage a small set of repository dependencies without a
manifest.xml file or git submodules. You get to write (local) project config
files in yaml instead.

|ci| |wheels| |release| |badge| |bandit|

|pre| |pylint|

|tag| |license| |python|



.. note:: This project uses versioningit_ to generate and maintain the
          version file, which only gets included in the sdist/wheel
          packages. In a fresh clone, running any of the tox_ commands
          should generate the current version file.

.. _versioningit: https://github.com/jwodder/versioningit
.. _tox: https://github.com/tox-dev/tox


Quick Start
===========

Repolite is mainly configuration-driven via YAML config files; the included
example can be displayed and copied via command-line options (see the Usage_
section below).  To create your own configuration, you need your repository
metadata and some ancillary info (see `Configuration settings`_ for more
details).

Once installed, running ``repolite`` without any local configuration file
will use the (internal) example configuration, ie, running it without any
arguments will clone the example repos to a subdirectory ``ext/`` in the
current directory.

By default (with no options) ``repolite`` will clone all the repositories
in the configuration file and checkout each configured branch.  From there
you can build and test, add more tests/features, until you need to update
your dependencies or switch branches.  At that point (or any time), run
``repolite`` with the ``--update`` option to pull in upstream changes
and/or switch branches.

To create your own default config file in the working directory, the local
copy must be named ``.repolite.yml``.  To get a copy of the example
configuration file, do::

  $ cd path/to/work/dir/
  $ repolite --save-config
  $ $EDITOR .repolite.yml
  $ repolite --dump-config  # you should see your config settings

If needed, you can also create additional project-level config files to
override your default project configuration. These alternate config files
can have arbitrary names (ending in '.yml' or '.yaml') but we recommend
using something like ``repo-dev-myproject.yml`` or similar. Since only one
configuration can be "active", the non-default config file must be set
via the environment variable ``REPO_CFG``, eg::

  $ repolite --dump-config > repo-develop.yml
  $ $EDITOR repo-develop.yml  # set alternate branches, other options
  $ REPO_CFG="repo-develop.yml" repolite --update

Install with pip
----------------

This package is *not* yet published on PyPI, thus use one of the
following to install the latest repolite on any platform::

  $ pip install -U -f https://github.com/sarnold/repolite/releases/ repolite

or use this command to install a specific version from source::

  $ pip install git+https://github.com/sarnold/repolite.git@0.1.0

If you have a ``requirements.txt`` file, you can add something like this::

  -f https://github.com/sarnold/repolite/releases/
  repolite>=0.1.0


The full package provides the ``repolite`` executable as well as
an example configuration file that provides defaults for all values.

If you'd rather work from the source repository, it supports the common
idiom to install it on your system in a virtual env after cloning::

  $ python3 -m venv env
  $ source env/bin/activate
  $ pip install .
  $ repolite --version
  $ repolite --dump-config
  $ deactivate

The alternative to python venv is the ``tox`` test driver.  If you have it
installed already, see the example tox commands below.

Usage
=====

The current version supports minimal command options and there are no
required arguments::

  (dev) user@host repolite (main) $ repolite -h
  Usage: repolite [options]

  Manage local (git) dependencies (default: clone and checkout).

  Options:
    --version          show program's version number and exit
    -h, --help         show this help message and exit
    -u, --update       update existing repositories
    -S, --show         display current repository state and exit
    -q, --quiet        suppress output from git command
    -v, --verbose      display more logging info
    -d, --dump-config  dump active configuration file or example to stdout and
                       exit
    -l, --lock-config  lock active configuration in new config file and checkout
                       hashes
    -s, --save-config  save example config to default filename (.repolite.yml)
                       and exit

Configuration settings
----------------------

Configuration keys for repository data:

:top_dir: path to repository parent directory (global option)
:repo_name: full repository name
:repo_alias: alias (short name) for ``repo_name``
:repo_url: full repository url, eg, Github ssh or https URL
:repo_remote: remote name (usually origin)
:repo_opts: reserved/not implemented
:repo_branch: git branch (used with checkout)
:repo_hash: git commit hash (used by ``lock-config`` option)
:repo_enable: if False, ignore repository

Configuration keys for optional ``git`` features/behavior:

:pull_with_rebase: global option, useful when upstream history gets rewritten
                   and fast-forward pull fails (see repo-level option)
:repo_use_rebase: same as above, but per-repository instead of global
:repo_has_lfs_files: if True, runs ``git-lfs install`` after cloning
                     (requires ``git-lfs`` to be installed first)
:repo_init_submodules: if True, initialize/update git submodules in that repository

Notes:

* use ``--lock-config`` to create a new config file with git hashes, then
  run that config later to reproduce a build using those hashes (this uses
  the current active config as baseline)
* use ``--verbose`` to see more about what the tool is doing, eg, git
  cmd strings
* use ``--quiet`` to suppress most of the git output
* we don't create new branches; configured branches must already exist in
  the remote repositories
* use the appropriate clone URL for upstream projects; if you have commit
  access, the ssh format is probably what you want
* using a correctly configured ``ssh-agent`` can help save extra typing
* you may want to add your ``top_dir`` path or default local config file
  patterns to your ``.gitignore`` file


Dev tools
=========

Local tool dependencies to aid in development; install both tools for
maximum enjoyment.

Tox
---

As long as you have git and at least Python 3.6, then you can install
and use `tox`_.  After cloning the repository, you can run the repo
checks with the ``tox`` command.  It will build a virtual python
environment for each installed version of python with all the python
dependencies and run the specified commands, eg:

::

  $ git clone https://github.com/sarnold/repolite
  $ cd repolite/
  $ tox -e py

The above will run the default test commands (if we had tests) using the
(local) default Python version.  To specify the Python version and host
OS type, run something like::

  $ tox -e py39-linux

To build and check the Python package, run::

  $ tox -e build,check

Full list of additional ``tox`` commands:

* ``tox -e dev`` will build a python venv and install in editable mode
* ``tox -e build`` will build the python packages and run package checks
* ``tox -e check`` will install the wheel package from above
* ``tox -e lint`` will run ``pylint`` (somewhat less permissive than PEP8/flake8 checks)
* ``tox -e mypy`` will run mypy import and type checking
* ``tox -e style`` will run flake8 style checks

To build/lint the api docs, use the following tox commands:

* ``tox -e docs`` will build the documentation using sphinx and the api-doc plugin
* ``tox -e docs-lint`` will run the sphinx doc-link checking

To install the latest release, eg with your own ``tox.ini`` file in
another project, use something like this::

  $ pip install -U -f https://github.com/sarnold/repolite/releases/ repolite


Pre-commit
----------

This repo is also pre-commit_ enabled for python/rst source and file-type
linting. The checks run automatically on commit and will fail the commit
(if not clean) and perform simple file corrections.  For example, if the
mypy check fails on commit, you must first fix any fatal errors for the
commit to succeed. That said, pre-commit does nothing if you don't install
it first (both the program itself and the hooks in your local repository
copy).

You will need to install pre-commit before contributing any changes;
installing it using your system's package manager is recommended,
otherwise install with pip into your usual virtual environment using
something like::

  $ sudo emerge pre-commit  --or--
  $ pip install pre-commit

then install it into the repo you just cloned::

  $ git clone https://github.com/sarnold/repolite
  $ cd repolite/
  $ pre-commit install

It's usually a good idea to update the hooks to the latest version::

    $ pre-commit autoupdate

Most (but not all) of the pre-commit checks will make corrections for you,
however, some will only report errors, so these you will need to correct
manually.

Automatic-fix checks include black, isort, autoflake, and miscellaneous
file fixers. If any of these fail, you can review the changes with
``git diff`` and just add them to your commit and continue.

If any of the mypy, bandit, or rst source checks fail, you will get a report,
and you must fix any errors before you can continue adding/committing.

To see a "replay" of any ``rst`` check errors, run::

  $ pre-commit run rst-backticks -a
  $ pre-commit run rst-directive-colons -a
  $ pre-commit run rst-inline-touching-normal -a

To run all ``pre-commit`` checks manually, try::

  $ pre-commit run -a


.. _pre-commit: https://pre-commit.com/index.html

.. |ci| image:: https://github.com/sarnold/repolite/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/ci.yml
    :alt: CI Status

.. |wheels| image:: https://github.com/sarnold/repolite/actions/workflows/wheels.yml/badge.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/wheels.yml
    :alt: Wheel Status

.. |badge| image:: https://github.com/sarnold/repolite/actions/workflows/pylint.yml/badge.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/pylint.yml
    :alt: Pylint Status

.. |release| image:: https://github.com/sarnold/repolite/actions/workflows/release.yml/badge.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/release.yml
    :alt: Release Status

.. |bandit| image:: https://github.com/sarnold/repolite/actions/workflows/bandit.yml/badge.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/bandit.yml
    :alt: Security check - Bandit

.. |pylint| image:: https://raw.githubusercontent.com/sarnold/repolite/badges/master/pylint-score.svg
    :target: https://github.com/sarnold/repolite/actions/workflows/pylint.yml
    :alt: Pylint Score

.. |license| image:: https://img.shields.io/github/license/sarnold/repolite
    :target: https://github.com/sarnold/repolite/blob/master/LICENSE
    :alt: License

.. |tag| image:: https://img.shields.io/github/v/tag/sarnold/repolite?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/sarnold/repolite/releases
    :alt: GitHub tag

.. |python| image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://www.python.org/downloads/
    :alt: Python

.. |pre| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
