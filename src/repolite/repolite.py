#!/usr/bin/env python

# Copyright 2022 Stephen L Arnold
#
# This is free software, licensed under the LGPL-2.1 license
# available in the accompanying LICENSE file.

"""
Manage a small set of repository dependencies without manifest.xml or git
submodules. You get to write (local) project config files in yaml instead.
"""

import logging
import os
import subprocess as sp
import sys
from optparse import OptionParser  # pylint: disable=W0402
from pathlib import Path
from shlex import split
from shutil import which

import pkg_resources
from munch import Munch

# from logging_tree import printout  # debug logger environment


class DirectoryTypeError(Exception):
    """Raise when there is a directory mismatch between cfg and actual"""

    __module__ = Exception.__module__


class FileTypeError(Exception):
    """Raise when the file extension is not '.yml' or '.yaml'"""

    __module__ = Exception.__module__


def check_for_git():
    """
    Make sure we can find the ``git`` and ``git-lfs`` binaries in the
    user environment and return a tuple of path strings.

    :return git_path, lfs_path: program path strings
    :rtype tuple: path to program if found, else None
    """
    git_path = which('git')
    lfs_path = which('git-lfs')
    if not git_path:
        logging.error('Cannot continue, no path found for git')
        sys.exit(1)
    elif not lfs_path:
        logging.debug('Cannot initialize large files, git-lfs not found')
    return git_path, lfs_path


def check_repo_state(ucfg):
    """
    Check if repo configuration is consistent, ie, does current repo state
    match repo configuration items.  Return ``True`` if current directories
    match the configuration, else ``False``.

    :param ucfg: Munch configuration object extracted from config file
    :type ucfg: Munch cfgobj
    :return is_state_valid: Boolean
    """
    _, top_dir = resolve_top_dir(ucfg.top_dir)
    logging.debug('Using top-level repo dir: %s', str(top_dir))
    try:
        os.chdir(top_dir)
    except OSError as exc:
        logging.exception("Could not change to repo directory: %s", exc)

    sorted_dir_list = sorted([x for x in top_dir.iterdir() if x.is_dir()])
    repo_name_list = []
    sorted_name_list = []
    for item in sorted_dir_list:
        sorted_name_list.append(item.stem)
    for item in [x for x in ucfg.repos if x.repo_enable]:
        dir_name = item.repo_alias if item.repo_alias else item.repo_name
        repo_name_list.append(dir_name)
    is_state_valid = sorted(repo_name_list) == sorted_name_list
    if not is_state_valid:
        logging.warning(
            'Invalid state: %s not equal to %s', repo_name_list, sorted_name_list
        )
    return is_state_valid


def install_with_pip(pip_name, quiet=False):
    """
    Install a python repository via pip; this should be done in a local
    virtual environment.

    :param pip_name: directory name of python repo to install
    :type pip_name: str
    :param quiet: filter most of the install cmd output
    :type verbose: boolean
    """
    pip_cmd_str = '-m pip install' + f' {pip_name}'
    pip_cmd = [sys.executable] + pip_cmd_str.split()
    logging.debug('Running install cmd: %s', pip_cmd)
    runner = sp.check_output
    if not quiet:
        runner = sp.check_call
    runner(pip_cmd)
    if not quiet:
        pkg_reqs = sp.check_output([sys.executable, '-m', 'pip', 'freeze'])
        pkg_deps = [r.decode().split('@')[0] for r in pkg_reqs.split()]
        logging.debug('Installed %s dependencies: %s', pip_name, pkg_deps)


def load_config(file_encoding='utf-8'):
    """
    Load yaml configuration file and munchify the data. If ENV path or local
    file is not found in current directory, the default will be loaded.

    :param file_encoding: file encoding of config file
    :type file_encoding: str
    :return tuple: Munch cfg obj and cfg file as Path obj
    :raises FileTypeError: if the input file is not yml
    """
    cfgfile = Path(REPO_CFG) if REPO_CFG else Path('.repolite.yml')
    if not cfgfile.name.lower().endswith(('.yml', '.yaml')):
        raise FileTypeError("FileTypeError: unknown config file extension")
    if not cfgfile.exists():
        cfgfile = Path(pkg_resources.resource_filename(__name__, 'data/example.yml'))
    logging.debug('Using config: %s', str(cfgfile.resolve()))
    cfgobj = Munch.fromYAML(cfgfile.read_text(encoding=file_encoding))

    return cfgobj, cfgfile


def resolve_top_dir(upath):
    """
    Resolve top_dir, ie, containing directory for git repositories. The
    suggested path is inside the project working directory, but we should
    support any writable path. Also set the working dir path and return
    both as Path objs.

    :return workpath, userpath: tuple of Path objs
    """
    workpath = Path('.').resolve()
    userpath = Path(upath).resolve()
    return workpath, userpath


def parse_config(ucfg):
    """
    Parse config file options and build list of repo objects. Return list
    of global options and list of Munch repo objects.

    :param ucfg: Munch configuration object extracted from config file
    :type ucfg: Munch cfgobj
    :return tuple: list of flags, list of repository objs
    """
    urepos = []
    udir = ucfg.top_dir
    urebase = ucfg.pull_with_rebase
    for item in [x for x in ucfg.repos if x.repo_enable]:
        urepos.append(item)
    return [udir, urebase], urepos


def create_locked_cfg(ucfg, ufile, quiet):
    """
    Create a 'locked' cfg file, ie, read the active config file and
    populate the ``repo_hash`` values with HEAD from each branch, then
    write a new config file with '-locked' appended to the name.

    :param ucfg: Munch configuration object extracted from config file
    :type ucfg: Munch cfgobj
    :param ufile: active config file
    :type ufile: Path obj
    :param quiet: Suppress some git output
    :type quiet: Boolean
    :raises DirectoryTypeError: if repo state is invalid
    """

    def write_locked_cfg(ucfg, ufile):
        """
        Write a new config file with '-locked' appended to the name.
        """
        locked_cfg_name = f'{ufile.stem}-locked{ufile.suffix}'
        Path(locked_cfg_name).write_text(Munch.toYAML(ucfg), encoding='utf-8')

    work_dir, top_dir = resolve_top_dir(ucfg.top_dir)
    logging.debug('Using top-level repo dir: %s', str(top_dir))

    valid_repo_state = check_repo_state(ucfg)
    if not valid_repo_state:
        raise DirectoryTypeError('Cannot lock cfg with mismatched directories')

    git_action = 'git rev-parse --verify HEAD'
    logging.debug('Get hash cmd: %s', git_action)
    checkout_cmd = 'git checkout -q ' if quiet else 'git checkout '
    for item in [x for x in ucfg.repos if x.repo_enable]:
        git_dir = item.repo_alias if item.repo_alias else item.repo_name
        os.chdir(git_dir)
        item.repo_hash = sp.check_output(split(git_action), text=True).strip()
        logging.debug('Repository %s HEAD is %s', str(git_dir), item.repo_hash)
        git_checkout = checkout_cmd + f'{item.repo_hash}'
        logging.debug('Checkout cmd: %s', git_checkout)
        sp.check_call(split(git_checkout))

        os.chdir(top_dir)
    os.chdir(work_dir)
    write_locked_cfg(ucfg, ufile)


def process_git_repos(flags, repos, pull, quiet):
    """
    Process list of git repository objs and populate/update ``top_dir``.

    :param flags: List of options (from yaml cfg)
    :type flags: list
    :param repos: List of repository objs (from yaml cfg)
    :type repos: list
    :param pull: Pull with rebase if True, else use --ff-only
    :type pull: Boolean
    :param quiet: Suppress some git output
    :type quiet: Boolean
    :raises FileExistsError: if cloning on top of existing directories
    """
    udir, urebase, has_lfs, ulock = flags
    work_dir, top_dir = resolve_top_dir(udir)
    logging.debug('Running with top-level repo dir: %s', str(top_dir))
    try:
        top_dir.mkdir(parents=True, exist_ok=True)
    except (FileExistsError, PermissionError) as exc:
        logging.exception('Could not create top repo directory: %s', exc)

    # find any existing directories and check for name clash
    if not pull:
        path_list = sorted([x for x in top_dir.iterdir() if x.is_dir()])
        top_dir_list = []
        for path in path_list:
            top_dir_list.append(path.stem)
        repo_name_list = []
        for item in repos:
            dir_name = item.repo_alias if item.repo_alias else item.repo_name
            repo_name_list.append(dir_name)
        logging.debug('Current dirs in config: %s', repo_name_list)
        logging.debug('Current dirs in top_dir: %s', top_dir_list)
        invalid_repo_state = sorted(repo_name_list) == top_dir_list
        dir_name_repo_intersect = set(top_dir_list).intersection(repo_name_list)
        logging.debug('Top_dir / repo intersect: %s', dir_name_repo_intersect)
        if invalid_repo_state:
            raise FileExistsError(
                'Git cannot clone when config matches existing directories'
            )

    os.chdir(top_dir)
    git_action = 'git clone -q ' if quiet else 'git clone '
    checkout_cmd = 'git checkout -q ' if quiet else 'git checkout '
    submodule_cmd = 'git submodule update --init --recursive'
    git_lfs_install = 'git lfs install'

    if pull:  # baseline git pull action, overrides repo-level option
        git_action = 'git pull --rebase=merges ' if urebase else 'git pull --ff-only '

    for item in repos:
        git_fetch = f'git fetch --tags {item.repo_remote}'
        git_checkout = checkout_cmd + f'{item.repo_branch}'
        git_dir = item.repo_alias if item.repo_alias else item.repo_name
        logging.debug('Operating in git_dir: %s', git_dir)
        if not pull:
            logging.debug('Checkout cmd: %s', git_checkout)
            if git_dir in list(dir_name_repo_intersect):
                logging.debug('Skipping existing repo: %s', git_dir)
            else:
                if item.repo_depth > 0:
                    git_action = git_action + f'--depth {item.repo_depth} '
                git_clone = git_action + f'{item.repo_url} '
                if item.repo_alias:
                    git_clone += item.repo_alias
                logging.debug('Clone cmd: %s', git_clone)
                sp.check_call(split(git_clone))
                os.chdir(git_dir)
                sp.check_call(split(git_checkout))
                if item.repo_init_submodules:
                    sp.check_call(split(submodule_cmd))
                if item.repo_has_lfs_files and has_lfs is not None:
                    sp.check_call(split(git_lfs_install))
        else:
            if item.repo_use_rebase and not urebase:
                git_action = 'git pull --rebase=merges '
            if item.repo_init_submodules:
                submodule_cmd = 'git submodule update --recursive'
            git_pull = git_action + f'{item.repo_remote} {item.repo_branch}'
            if ulock:
                checkout_lock = checkout_cmd + f'{item.repo_hash}'
            try:
                os.chdir(git_dir)
            except OSError as exc:
                logging.exception("Could not change to repo directory: %s", exc)

            if ulock:
                logging.debug('Checkout cmd: %s', git_checkout)
                sp.check_call(split(checkout_lock))
            else:
                logging.debug('Fetch cmd: %s', git_fetch)
                sp.check_call(split(git_fetch))
                sp.check_call(split(git_checkout))
                logging.debug('Pull cmd: %s', git_pull)
                sp.check_call(split(git_pull))
                if item.repo_init_submodules:
                    sp.check_call(split(submodule_cmd))

        os.chdir(top_dir)
    os.chdir(work_dir)


def process_repo_install(ucfg, quiet):
    """
    Install any repos with the ``repo_install`` flag set. Note we do not
    check repo state here, we just process each valid repo entry.

    :param ucfg: Munch configuration object extracted from config file
    :type ucfg: Munch cfgobj
    :param quiet: pass the ``quiet`` cmd line flag to install cmd
    """
    _, top_dir = resolve_top_dir(ucfg.top_dir)
    logging.debug('Using top-level repo dir: %s', str(top_dir))

    for item in [x for x in ucfg.repos if x.repo_enable and x.repo_install]:
        git_dir = item.repo_alias if item.repo_alias else item.repo_name
        tgt_dir = top_dir / str(git_dir)  # fun with Path objects
        install_with_pip(tgt_dir, quiet)


def show_repo_state(ucfg):
    """
    Display the current state of each repository using git describe/rev-parse.

    :param ucfg: Munch configuration object extracted from config file
    :type ucfg: Munch cfgobj
    :raises DirectoryTypeError: if repo state is invalid
    """
    work_dir, top_dir = resolve_top_dir(ucfg.top_dir)
    logging.debug('Using top-level repo dir: %s', str(top_dir))

    valid_repo_state = check_repo_state(ucfg)
    if not valid_repo_state:
        raise DirectoryTypeError(
            'Inconsistent directories; try running ``--update`` first?'
        )

    git_action1 = 'git describe --tags --dirty --always'
    git_action2 = 'git rev-parse --abbrev-ref HEAD'
    logging.debug('Git describe cmd: %s', git_action1)
    logging.debug('Git rev-parse cmd: %s', git_action2)
    for item in [x for x in ucfg.repos if x.repo_enable]:
        git_dir = item.repo_alias if item.repo_alias else item.repo_name
        os.chdir(git_dir)
        item1_data = sp.check_output(split(git_action1), text=True).strip()
        item2_data = sp.check_output(split(git_action2), text=True).strip()
        logging.info(
            'Repository %s: branch is %s, commit is %s',
            str(git_dir),
            item2_data,
            item1_data,
        )
        os.chdir(top_dir)
    os.chdir(work_dir)


def main(argv=None):
    """
    Manage git repository-based project dependencies.
    """
    if argv is None:
        argv = sys.argv

    parser = OptionParser(usage="usage: %prog [options]", version=f"%prog {VERSION}")
    parser.description = 'Manage local (git) dependencies (default: clone and checkout).'
    parser.add_option(
        "-i",
        "--install",
        action="store_true",
        dest="install",
        help="install existing repositories (python only)",
    )
    parser.add_option(
        "-u",
        "--update",
        action="store_true",
        dest="update",
        help="update existing repositories",
    )
    parser.add_option(
        "-S",
        "--show",
        action="store_true",
        dest="show",
        help="display current repository state",
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        help="suppress output from git command",
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="display more logging info",
    )
    parser.add_option(
        '-d',
        '--dump-config',
        action='store_true',
        dest="dump",
        help='dump active configuration file or example to stdout and exit',
    )
    parser.add_option(
        '-l',
        '--lock-config',
        action='store_true',
        dest="lock",
        help='lock active configuration in new config file and checkout hashes',
    )
    parser.add_option(
        '-s',
        '--save-config',
        action='store_true',
        dest="save",
        help='save example config to default filename (.repolite.yml) and exit',
    )

    (opts, _) = parser.parse_args()

    # basic logging setup must come before any other logging calls
    log_level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)
    # printout()  # logging_tree

    cfg, pfile = load_config()
    flag_list, repo_list = parse_config(cfg)

    git_cmd, lfs_cmd = check_for_git()
    logging.debug('Found at least one git binary: %s and %s', git_cmd, lfs_cmd)
    flag_list.append(lfs_cmd)

    if opts.save:
        cfg_data = pfile.read_bytes()
        def_config = Path('.repolite.yml')
        def_config.write_bytes(cfg_data)
        sys.exit(0)
    if opts.dump:
        sys.stdout.write(pfile.read_text(encoding='utf-8'))
        sys.stdout.flush()
        sys.exit(0)

    try:
        if opts.install:
            process_repo_install(cfg, opts.quiet)
            sys.exit(0)
        if opts.show:
            show_repo_state(cfg)
            sys.exit(0)
        if opts.lock:
            create_locked_cfg(cfg, pfile, opts.quiet)
            sys.exit(0)
    except DirectoryTypeError as exc:
        logging.error('Top dir: %s', exc)
        sys.exit(1)

    ulock = 'locked' in pfile.name
    flag_list.append(ulock)

    try:
        process_git_repos(flag_list, repo_list, opts.update, opts.quiet)
    except FileExistsError as exc:
        logging.error('Top dir: %s', exc)


VERSION = pkg_resources.get_distribution('repolite').version
REPO_CFG = os.getenv('REPO_CFG', default='')


if __name__ == '__main__':
    main()
