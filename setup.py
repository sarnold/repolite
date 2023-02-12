#!/usr/bin/env python

import os
import sys

if sys.version_info.minor > 6:
    import setuptools

    setuptools.setup()
else:
    from distutils.core import setup

    sys.path.append(os.path.abspath("src"))
    from repolite._version import __version__
    sys.path.pop()

    setup(
        name="repolite",
        version=__version__,
        packages=["repolite"],
        package_dir={"": "src"},
    )
