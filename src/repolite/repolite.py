#!/usr/bin/env python

# Copyright 2022 Stephen L Arnold
#
# This is free software, licensed under the LGPL-2.1 license
# available in the accompanying LICENSE file.

"""
Manage small set of repository dependencies without manifest.xml or git
submodules. You get to write (local) project config files in yaml instead.
"""

import os
import sys
import subprocess as sp
from optparse import OptionParser  # pylint: disable=W0402
from pathlib import Path
from shlex import split

import pkg_resources
import yaml as yaml_loader
from munch import Munch
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


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
    cfgobj = Munch.fromYAML(cfgfile.read_text(encoding=file_encoding))

    return cfgobj, cfgfile


def parse_config(ucfg):
    """
    Parse config file options and build list of repo objects. Return both
    global options and a list of Munch repo objects.

    :param ucfg:
    :type ucfg: Munch object from yaml cfg
    """
    urepos = []
    top_dir = ucfg.top_dir
    rebase = ucfg.pull_with_rebase
    for item in [x for x in ucfg.repos if x.repo_enable]:
        urepos.append(item)
    return top_dir, rebase, urepos


def process_git_repos():
    """
    Process list of git repository objs and populate/update ``top_dir``.
    """


def main(argv=None):
    """
    Manage git repository-based project dependencies.
    """
    debug = False
    cfg, pfile = load_config()

    if argv is None:
        argv = sys.argv
    parser = OptionParser(
        usage="usage: %prog [options]", version=f"%prog {VERSION}"
    )
    parser.description = 'Manage local (git) project dependencies.'
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Display more processing info",
    )
    parser.add_option(
        '-d',
        '--dump-config',
        action='store_true',
        dest="dump",
        help='Dump configuration file or example to stdout',
    )

    (options, args) = parser.parse_args()

    if options.verbose:
        debug = True
    elif options.dump:
        sys.stdout.write(pfile.read_text(encoding='utf-8'))
        sys.exit(0)
    if not args:
        parser.print_help()
        sys.exit(1)


VERSION = pkg_resources.get_distribution('repolite').version
REPO_CFG = os.getenv('REPO_CFG', default='')

if __name__ == '__main__':
    main()
