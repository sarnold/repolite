Changelog
=========


0.4.1 (2023-02-13)
------------------

New
~~~
- Add a changelog file and include it in docs build. [Stephen L Arnold]

Changes
~~~~~~~
- Be more explicit about OS packages in the readme. [Stephen L Arnold]
- Use defaults on gh-pages deploy action, bump to v4. [Stephen L Arnold]

Fix
~~~
- Stop using later constructs and pkg_resources. [Stephen L Arnold]

  * do not use pkg_resources or global version in repolite module
  * python setup.py <foo> commands should work as expected back to bionic
    launchpad builder env (ie, early py3.6)

Other
~~~~~
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

Fix
~~~
- Cleanup/improve docstring for module func. [Stephen L Arnold]

Other
~~~~~
- Merge pull request #12 from sarnold/older-python. [Steve Arnold]

  new features and older python


0.3.3 (2022-09-29)
------------------

Fix
~~~
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

Fix
~~~
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

Fix
~~~
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

Fix
~~~
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

Fix
~~~
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
- Add sphinx/api doc sources and ci workflow, more cleanup. [Stephen L
  Arnold]

  * update readme, add missing license file

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
