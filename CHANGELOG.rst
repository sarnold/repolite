Changelog
=========


0.6.3 (2025-03-16)
------------------

Changes
~~~~~~~
- Improve readme descriptions, add example repo links. [Stephen L
  Arnold]
- Rename symlink bacl to LICENSE, update readme badge uri. [Stephen L
  Arnold]
- Update .pre-commit-config.yaml, fix clean targets. [Stephen L Arnold]
- Add readme section on SBOM and licensing info. [Stephen L Arnold]
- Add REUSE.toml config and become reuse spec 3.3 compliant. [Stephen L
  Arnold]

  * repolite-sdist-sbom.txt was generated using ``reuse spdx`` cmd
  * COPYING is now a symlink pointing to LICENSES/LGPL-2.1-or-later.txt
- Update all workflow actions and python versions. [Stephen L Arnold]
- Move description text and add version. [Stephen L Arnold]

Fixes
~~~~~
- Change license badge to static instead. [Stephen L Arnold]

  * github decided to cry about license symlink so use static badge text
- Sort out git quiet and add info log line. [Stephen L Arnold]

  * closes issue #25
- Make sure release workflow has the right job permissions. [Stephen L
  Arnold]

  * fix readme uri, add more clean to tox cmd

Other
~~~~~
- Merge pull request #30 from sarnold/doc-examples. [Steve Arnold]

  readme improvements
- Merge pull request #29 from sarnold/license-fiddling. [Steve Arnold]

  static licesnse badge
- Merge pull request #28 from sarnold/license-fiddling. [Steve Arnold]

  license link not detected
- Merge pull request #27 from sarnold/issue-readme. [Steve Arnold]

  workflow fixes
- Merge pull request #26 from sarnold/metadata-cleanup. [Steve Arnold]

  metadata cleanup


0.6.2 (2024-06-02)
------------------

New
~~~
- Add changelog feature for release workflows. [Stephen L Arnold]

  * uses ``gitchangelog`` to generate either full changelog.rst or
    changelog diff from given base tag

Changes
~~~~~~~
- Add config option to set changelog file extension. [Stephen L Arnold]

  * allowed options are 'rst' or 'md' depending on the gitchangelog
    configuration setting for ``output_engine``

Fixes
~~~~~
- Update docs cmds in release workflow. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #24 from sarnold/changelogs. [Steve Arnold]

  Add changelog support
- Update our own changelog for next release, combine tox doc envs.
  [Stephen L Arnold]


0.6.1 (2024-05-22)
------------------

New
~~~
- Support per-repo tag in config file for tag creation. [Steve Arnold]

  * add new config key repo_create_tag_new
  * repo tag takes precedence over command-line tag

Changes
~~~~~~~
- Update readme, cleanup action versions in wheels workflow. [Steve
  Arnold]

Other
~~~~~
- Merge pull request #23 from sarnold/per-repo-tags. [Steve Arnold]

  feat: add per-repo tag support


0.6.0 (2024-05-08)
------------------

New
~~~
- Add tagging feature, currently only one tag via args. [Steve Arnold]

Changes
~~~~~~~
- Update changelog for new release. [Stephen L Arnold]
- Start with the simplest tag push, update debug logging. [Steve Arnold]
- Wire up tag function to cmdline arg and update readme. [Steve Arnold]
- Set global git user params in CI before running (tag) tests. [Steve
  Arnold]

Other
~~~~~
- Merge pull request #22 from sarnold/feat-tagging. [Steve Arnold]

  New tagging feature


0.5.2 (2024-03-27)
------------------

Changes
~~~~~~~
- Add a gitchangelog cfg and tox cmd to (re)generate changes. [Steve
  Arnold]
- Update python and GH workflow action versions. [Steve Arnold]

Fixes
~~~~~
- Refactor test fixtures for pytest 8 and temp_path. [Steve Arnold]

  * session.name is now an empty string, use getbasetemp().name instead
  * use tmp_path_factory instead of tmpdir
- Re-init git_action to get proper clone args for each repository.
  [Steve Arnold]

  * fixes issue #20

Other
~~~~~
- Bump changelog for release. [Steve Arnold]
- Merge pull request #21 from sarnold/issue-20. [Steve Arnold]

  Fixes for Issue #20 and pytest fixtures


0.5.1 (2024-01-12)
------------------

Changes
~~~~~~~
- Switch to upstream git_dummy instead of fork. [Stephen L Arnold]

  * requires new arg for nested repos, but it does work

Fixes
~~~~~
- Use branch arg for clone with non-zero depth. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #19 from sarnold/shallow-args. [Steve Arnold]

  fix shallow clone error
- Merge pull request #17 from sarnold/fixture-update. [Steve Arnold]

  update test fixture and release workflow


0.5.0 (2023-09-16)
------------------

New
~~~
- Introduce check_repo_url() to sanitize windows paths. [Stephen L
  Arnold]

  * inspired by SO and GitPython url polishing
- Use clone_from() on all platforms, cleanup test output. [Stephen L
  Arnold]
- Use GitPython wrapper to clone on win32. [Stephen L Arnold]

  * test passing some multi_options to clone_from()
- Add some misc tests, minor refactor for testability. [Stephen L
  Arnold]

  * swap out optparse and swap in argparse, maintain original interface
  * add another tox command to setup dummy test repositories

Changes
~~~~~~~
- Readme and ci cleanup, add coverage workflow. [Stephen L Arnold]
- Use joinpath for pytest urls, cleanup paths, add windows to ci.
  [Stephen L Arnold]

  * refactor default url paths so we can do a proper join of path elements
  * resolve all test paths, add some introspection to CI test output
  * stringify repo_url and add more logging calls in process_git_repos()
  * switch check_output call to run with capture_output
  * test alternate GitPython wrapper for cloning on win32
  * Munch is actually tested on Windows, but we should check it anyway
- Add test for locked_cfg, fix testability bit. [Stephen L Arnold]
- Remove windows from pytest CI matrix, Path obj not iterable. [Stephen
  L Arnold]
- Add pytest fixtures so we can add more tests. [Stephen L Arnold]

  * uses (forked) git_dummy to create git repos for testing
  * update project/test configs, add testdata paths to .gitignore

Fixes
~~~~~
- Improve testability, cleanup CI env names. [Stephen L Arnold]

  * make sure we use importlib backport in older environments
  * try pytest on windows-latest

Other
~~~~~
- Merge pull request #16 from sarnold/fm-tests2. [Steve Arnold]

  refactored version of fm-tests
- Really fix coverage workflow, attempt to combine py37,py311 coverage
  data. [Stephen L Arnold]


0.4.2 (2023-09-02)
------------------

New
~~~
- Add tox self-test workflow example to go with example cfg. [Stephen L
  Arnold]
- Vendor tox plugin file, use for workflow self-test cmds. [Stephen L
  Arnold]

Changes
~~~~~~~
- Fix bandit workflow (needs to run on just push) [Stephen L Arnold]
- Update pre-commit hooks, adjust config. [Stephen L Arnold]
- Refactor upstream imports, remove generated version module. [Stephen L
  Arnold]

  * use setuptools_scm instead of versioningit, do not use write_to_file
  * use importlib resources/metadata instead of pkg_resources/version mod
  * cleanup tox file, manifest, and docs config

Other
~~~~~
- Merge pull request #14 from sarnold/import-ref. [Steve Arnold]

  Import refactor, remove generated version module


0.4.1 (2023-02-13)
------------------

New
~~~
- Add a changelog file and include it in docs build. [Stephen L Arnold]

Changes
~~~~~~~
- Be more explicit about OS packages in the readme. [Stephen L Arnold]
- Cleanup ci artifacts. [Stephen L Arnold]
- Use defaults on gh-pages deploy action, bump to v4. [Stephen L Arnold]

Fixes
~~~~~
- Stop using later constructs and pkg_resources. [Stephen L Arnold]

  * do not use pkg_resources or global version in repolite module
  * python setup.py <foo> commands should work as expected back to bionic
    launchpad builder env (ie, early py3.6)

Other
~~~~~
- Update changelog file for new patch release. [Stephen L Arnold]
- Merge pull request #13 from sarnold/changelog-docs. [Steve Arnold]

  cleanup imports, add changelog in docs


0.4.0 (2022-12-23)
------------------

New
~~~
- Add new config options, update readme and default yaml. [Stephen L
  Arnold]

  * add option for clone depth with default 0 (ala gh workflows)
  * add option to install a repo into the current env using pip

Changes
~~~~~~~
- Update all workflows, mainly action versions. [Stephen L Arnold]

Fixes
~~~~~
- Cleanup/improve docstring for module func. [Stephen L Arnold]
- Make setup.py compatible with older python, eg, py36 bionic. [Stephen
  L Arnold]

  * required for python envs still using distutils that do not
    like projects with src/ layout
  * update tox file to generate egg_info for mypy

Other
~~~~~
- Merge pull request #12 from sarnold/older-python. [Steve Arnold]

  new features and older python


0.3.3 (2022-09-29)
------------------

Fixes
~~~~~
- Add missing exit in cmd exception handler. [Stephen L Arnold]

  * inconsistent directory error should exit after log msg

Other
~~~~~
- Merge pull request #10 from sarnold/hotfix. [Steve Arnold]

  add missing exit in cmd exception handler


0.3.2 (2022-09-29)
------------------

New
~~~
- Flesh out show cmd with branch and describe data. [Stephen L Arnold]

Fixes
~~~~~
- Add missing refactor bits, update debug logging. [Stephen L Arnold]

  * remove secondary loop check, make sure repo context is available
  * add more useful output to show cmd, make sure we fetch tags
  * add more logging introspection

Other
~~~~~
- Merge pull request #9 from sarnold/more-show. [Steve Arnold]

  Show more repo metadata, finish refactor


0.3.1 (2022-09-13)
------------------

New
~~~
- Abstract code for valid_repo_state, add new show option. [Stephen L
  Arnold]

  * for display of current repo state, ie, git describe output

Changes
~~~~~~~
- Add new show option to usage output in readme. [Stephen L Arnold]

Fixes
~~~~~
- Still more docstring cleanup. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #8 from sarnold/repo-state. [Steve Arnold]

  Display repo state


0.3.0 (2022-09-04)
------------------

New
~~~
- Add support for submodule update and bandit workflow. [Stephen L
  Arnold]

  * add submodule handling to repo update cmd
  * add bandit security check workflow
  * update docs/docstrings and tool configs

Fixes
~~~~~
- Restore missing bits, un-disable some pylint checks. [Stephen L
  Arnold]

  * add missing recursive arg for submodule update
  * re-flow readme text, add missing updates
  * remove pylint-disable comments, update tox file

Other
~~~~~
- Merge pull request #7 from sarnold/more-cleanup. [Steve Arnold]

  submodule and doc updates
- Merge pull request #6 from sarnold/more-subs. [Steve Arnold]

  add support for submodule update


0.2.1 (2022-08-31)
------------------

Changes
~~~~~~~
- Main docs TOC meeds a better title. [Stephen L Arnold]

Fixes
~~~~~
- Add missing repo branch option. [Stephen L Arnold]
- Skip existing repos and allow clone if config updated. [Stephen L
  Arnold]

  * meaning the config file must have at least one repo configured that
    does not yet exist in the target directory, eg, a new ( or at least
    newly enabled) repository

Other
~~~~~
- Merge pull request #5 from sarnold/new-repo-fix. [Steve Arnold]

  improve existing directory check


0.2.0 (2022-08-20)
------------------

New
~~~
- Expand cfg options, wire up submodules, rebase, lfs, update readme.
  [Stephen L Arnold]

  * support initializing submodules and lfs when configured
  * check for git and git-lfs and log (or exit if both are missing)

Changes
~~~~~~~
- Flesh out table of configuration keys. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #3 from sarnold/still-more-docs. [Steve Arnold]

  expand cfg opts, update readme


0.1.0 (2022-08-17)
------------------

New
~~~
- Add lock-config option, update default config and readme. [Stephen L
  Arnold]
- Add docs build as the last job in release workflow. [Stephen L Arnold]

  * we should have matching doc version on new tag
- Add option to save example cfg to default filename. [Stephen L Arnold]

  * update readme with new help/examples
- Add sphinx/api doc sources and ci workflow, more cleanup. [Stephen L
  Arnold]

  * update readme, add missing license file
- Add tool configs for pep8speaks and pre-commit. [Stephen L Arnold]

Changes
~~~~~~~
- Update readme and doc strings, remove unused import,subclass. [Stephen
  L Arnold]

Fixes
~~~~~
- Implement directory-check TODO and update readme. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #2 from sarnold/more-docs. [Steve Arnold]

  doc updates and cleanup
- Merge pull request #1 from sarnold/docs-and-ci. [Steve Arnold]

  docs and CI workflows
- Create readme file, add base github CI workflows, more cleanup.
  [Stephen L Arnold]
- Finish initial git cmds, wire up logging, cleanup packaging. [Stephen
  L Arnold]
- Apply more flesh and lint cleanup, update cfg and tox files. [Stephen
  L Arnold]
- Add more (half)skeleton, update reqs, setup, tox files. [Stephen L
  Arnold]


0.0.0 (2022-08-14)
------------------
- Add initial project files and example config. [Stephen L Arnold]
