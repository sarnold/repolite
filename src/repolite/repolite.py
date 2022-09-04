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
    :type quiet: bool
    """

    def write_locked_cfg(ucfg, ufile):
        """
        Write a new config file with '-locked' appended to the name.
        """
        locked_cfg_name = f'{ufile.stem}-locked{ufile.suffix}'
        Path(locked_cfg_name).write_text(Munch.toYAML(ucfg), encoding='utf-8')

    work_dir, top_dir = resolve_top_dir(ucfg.top_dir)
    logging.debug('Using top-level repo dir: %s', str(top_dir))
    try:
        os.chdir(top_dir)
    except OSError as exc:
        logging.exception("Could not find repo directory: %s", exc)

    sorted_dir_list = sorted([x for x in top_dir.iterdir() if x.is_dir()])
    repo_name_list = []
    sorted_name_list = []
    for item in sorted_dir_list:
        sorted_name_list.append(item.stem)
    for item in [x for x in ucfg.repos if x.repo_enable]:
        dir_name = item.repo_alias if item.repo_alias else item.repo_name
        repo_name_list.append(dir_name)
    valid_repo_state = sorted(repo_name_list) == sorted_name_list
    if not valid_repo_state:
        logging.error('%s not equal to %s', repo_name_list, sorted_name_list)
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
    :type pull: bool
    :param quiet: Suppress some git output
    :type quiet: bool
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
        if top_dir_list:
            repo_name_list = []
            for item in repos:
                dir_name = item.repo_alias if item.repo_alias else item.repo_name
                repo_name_list.append(dir_name)
            logging.debug('Current dirs in config: %s', repo_name_list)
            logging.debug('Current dirs in top_dir: %s', top_dir_list)
            invalid_repo_state = sorted(repo_name_list) == top_dir_list
            dir_name_repo_intersect = set(top_dir_list).intersection(repo_name_list)
            if invalid_repo_state:
                raise FileExistsError('Git cannot clone with existing directories')

    os.chdir(top_dir)
    git_action = 'git clone -q ' if quiet else 'git clone '
    checkout_cmd = 'git checkout -q ' if quiet else 'git checkout '
    submodule_cmd = 'git submodule update --init --recursive'
    git_lfs_install = 'git lfs install'

    if pull:  # baseline git pull action, overrides repo-level option
        git_action = 'git pull --rebase=merges ' if urebase else 'git pull --ff-only '

    for item in repos:
        git_fetch = f'git fetch {item.repo_remote}'
        git_checkout = checkout_cmd + f'{item.repo_branch}'
        logging.debug('Checkout cmd: %s', git_checkout)
        git_dir = item.repo_alias if item.repo_alias else item.repo_name
        if not pull:
            if git_dir in list(dir_name_repo_intersect):
                logging.debug('Skipping existing repo: %s', git_dir)
            else:
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


def main(argv=None):
    """
    Manage git repository-based project dependencies.
    """
    if argv is None:
        argv = sys.argv

    parser = OptionParser(usage="usage: %prog [options]", version=f"%prog {VERSION}")
    parser.description = 'Manage local (git) dependencies (default: clone and checkout).'
    parser.add_option(
        "-u",
        "--update",
        action="store_true",
        dest="update",
        help="update existing repositories",
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
    elif opts.dump:
        sys.stdout.write(pfile.read_text(encoding='utf-8'))
        sys.stdout.flush()
        sys.exit(0)
    elif opts.lock:
        try:
            create_locked_cfg(cfg, pfile, opts.quiet)
        except DirectoryTypeError as exc:
            logging.error('Top dir: %s', exc)
        finally:
            sys.exit(0)

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
