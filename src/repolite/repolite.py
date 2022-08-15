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

import pkg_resources
from munch import Munch
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
# from logging_tree import printout  # debug logger environment


class FileTypeError(Exception):
    """Raise when the file extension is not '.yml' or '.yaml'"""

    __module__ = Exception.__module__


class StrYAML(YAML):
    """
    New API likes dumping straight to file/stdout, so we subclass and
    create 'inefficient' custom string dumper.
    """

    def dump(self, data, stream=None, **kw):
        stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        return stream.getvalue()


def load_config(file_encoding='utf-8'):
    """
    Load yaml configuration file and munchify the data. If ENV path or local
    file is not found in current directory, the default will be loaded.

    :param file_encoding: file encoding of config file
    :type file_encoding: str
    :return: Munch cfg obj and cfg file as Path obj
    :rtype tuple:
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
    suggested path is project working directory, but we should support
    any writable path.
    """
    workpath = Path('.').resolve()
    userpath = Path(upath).resolve()
    return workpath, userpath


def parse_config(ucfg):
    """
    Parse config file options and build list of repo objects. Return both
    global options and a list of Munch repo objects.

    :param ucfg:
    :type ucfg: Munch object from yaml cfg
    """
    urepos = []
    udir = ucfg.top_dir
    urebase = ucfg.pull_with_rebase
    for item in [x for x in ucfg.repos if x.repo_enable]:
        urepos.append(item)
    return [udir, urebase], urepos


def process_git_repos(flags, repos, pull, quiet):  # pylint: disable=R0914
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
    work_dir, top_dir = resolve_top_dir(flags[0])
    logging.debug('Running with top-level repo dir: %s', str(top_dir))
    try:
        top_dir.mkdir(parents=True, exist_ok=True)
    except (FileExistsError, PermissionError) as exc:
        logging.exception('Could not create top repo directory: %s', exc)

    os.chdir(top_dir)
    git_action = 'git clone '
    checkout_cmd = 'git checkout '

    if quiet:
        git_action = git_action + '-q '
        checkout_cmd = checkout_cmd + '-q '

    if pull:
        git_action = 'git pull --ff-only '
        if flags[1]:
            git_action = 'git pull --rebase=merges '

    for item in repos:
        git_fetch = f'git fetch {item.repo_remote}'
        git_checkout = checkout_cmd + f'{item.repo_branch}'
        logging.debug('Checkout cmd: %s', git_checkout)
        if not pull:
            git_clone = git_action + f'{item.repo_url} '
            if item.repo_alias:
                git_clone += item.repo_alias
            logging.debug('Clone cmd: %s', git_clone)
            sp.check_call(split(git_clone))
            sp.check_call(split(git_checkout))
        else:
            git_pull = git_action + f'{item.repo_remote} {item.repo_branch}'
            git_dir = item.repo_alias if item.repo_alias else item.repo_name
            try:
                os.chdir(git_dir)
            except OSError as exc:
                logging.exception("Could not change to repo directory: %s", exc)

            logging.debug('Fetch cmd: %s', git_fetch)
            sp.check_call(split(git_fetch))
            sp.check_call(split(git_checkout))
            logging.debug('Pull cmd: %s', git_pull)
            sp.check_call(split(git_pull))

        os.chdir(top_dir)
    os.chdir(work_dir)


def main(argv=None):
    """
    Manage git repository-based project dependencies.
    """
    if argv is None:
        argv = sys.argv

    debug = False
    quiet = False
    update = False

    parser = OptionParser(
        usage="usage: %prog [options]", version=f"%prog {VERSION}"
    )
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
        help='dump configuration file or example to stdout and exit',
    )

    (options, _) = parser.parse_args()

    if options.verbose:
        debug = True
    if options.quiet:
        quiet = True
    if options.update:
        update = True

    # basic logging setup must come before any other logging calls
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=log_level)
    # printout()  # logging_tree

    cfg, pfile = load_config()
    if options.dump:
        sys.stdout.write(pfile.read_text(encoding='utf-8'))
        sys.exit(0)

    flag_list, repo_list = parse_config(cfg)
    process_git_repos(flag_list, repo_list, update, quiet)


VERSION = pkg_resources.get_distribution('repolite').version
REPO_CFG = os.getenv('REPO_CFG', default='')


if __name__ == '__main__':
    main()
