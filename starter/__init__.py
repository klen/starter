"""
    Creates the sceleton for new projects.
    Similar to the template part of PasteScript, but uses Jinja templates.

"""
from os import getcwd, path as op


# Module information
# ==================

__version__ = '0.2.0'
__project__ = 'Starter'
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"


# Global configuration
# ====================

CFGFILE = '.starter.ini'
CURDIR = getcwd()
TPLDIR = op.relpath(op.join(op.dirname(__file__), 'templates'))
