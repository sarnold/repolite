"""
Repolite helps you manage git repo project dependencies according to your local yaml
config file(s).
"""

import sys

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

__version__ = version('repolite')
__all__ = [
    "__version__",
]
