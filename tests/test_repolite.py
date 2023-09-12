import os
from pathlib import Path

import pytest
from munch import Munch

from repolite import *
from repolite.repolite import *

repo_cfg = """\
prog_name: repolite
top_dir: ext  # local directory path for enabled repositories
pull_with_rebase: false  # use --ff-only if false
# add new repo_name sections as needed
repos:
  - repo_name: daffy
    repo_alias: null
    repo_url: testdata/daffy/
    repo_depth: 0
    repo_remote: origin
    repo_opts: []
    repo_branch: main
    repo_hash: null
    repo_use_rebase: false
    repo_has_lfs_files: false
    repo_init_submodules: false
    repo_install: false
    repo_enable: true
  - repo_name: porky
    repo_alias: bugs  # optional short name for repo directory
    repo_url: testdata/porky/
    repo_depth: 0
    repo_remote: origin
    repo_opts: []
    repo_branch: branch1
    repo_hash: null
    repo_use_rebase: false
    repo_has_lfs_files: false
    repo_init_submodules: false
    repo_install: false  # only for pip-installable packages
    repo_enable: true
"""

cfg = Munch.fromYAML(repo_cfg)


def test_repolite_sync(script_loc, tmpdir_session):
    """
    Sync the repos in the test config.
    """
    print(tmpdir_session)
    cfg.top_dir = str(tmpdir_session / 'ext')

    for repo in cfg.repos:
        repo.repo_url = script_loc / repo.repo_url

    flag_list, repo_list = parse_config(cfg)
    git_cmd, lfs_cmd = check_for_git()
    flag_list.append(lfs_cmd)
    ulock = False
    flag_list.append(ulock)

    update = False
    quiet = True
    process_git_repos(flag_list, repo_list, update, quiet)


def test_repolite_show(script_loc, tmpdir_session):
    """
    Sync the repos in the test config.
    """
    cfg.top_dir = str(tmpdir_session / 'ext')

    for repo in cfg.repos:
        repo.repo_url = script_loc / repo.repo_url

    show_repo_state(cfg)


def test_repolite_update(tmp_path, script_loc, tmpdir_session):
    """
    Update the repos in the test config.
    """
    cfg.top_dir = str(tmpdir_session / 'ext')

    for repo in cfg.repos:
        repo.repo_url = script_loc / repo.repo_url

    flag_list, repo_list = parse_config(cfg)
    git_cmd, lfs_cmd = check_for_git()
    flag_list.append(lfs_cmd)
    ulock = False
    flag_list.append(ulock)

    for repo in cfg.repos:
        if repo.repo_name == 'daffy':
            repo.repo_branch = 'branch2'

    update = True
    quiet = True
    process_git_repos(flag_list, repo_list, update, quiet)
