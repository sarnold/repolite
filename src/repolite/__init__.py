"""
Repolite manages git repos according to your local yaml config file.
"""

from ._version import __version__
from .repolite import install_with_pip

__description__ = "Lite git repository manager for small-ish projects."

__all__ = ["__version__", "__description__", "install_with_pip"]
