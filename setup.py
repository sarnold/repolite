#!/usr/bin/env python

import sys

if sys.version_info > (3,6):
    import setuptools

    setuptools.setup()
else:
    from distutils.core import setup

    pkg_name = 'repolite'
    sys.path[0:0] = ['src'/pkg_name]
    from _version import __version__

    setup(
        name=pkg_name,
        version=__version__,
        packages=[pkg_name],
        package_dir = {'': 'src'}
    )
