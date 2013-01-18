"""
    Creates the sceleton for new projects.
    Similar to the template part of PasteScript but uses Jinja templates.

"""
import sys
from argparse import ArgumentParser


__version__ = '0.1.0'
__project__ = 'Starter'
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"


parser = ArgumentParser(description=__doc__)
parser.add_argument('TEMPLATE', help='Template name or path to template.')
parser.add_argument(
    '-l', default='info', help='Verbose level (info)',
    choices=['debug', 'info', 'warn', 'error', 'critical'])
parser.add_argument(
    '-v', '--version', action='version',
    version=__version__, help='Show {0} version'.format(__project__))

cfgfile = 'starter.ini'


class Starter(object):

    def __init__(self, path, params):
        self.path = path
        self.params = params

    def clone(self):
        pass

    @property
    def context(self):
        pass


def main(*args):
    params = parser.parse_args(args)
    import ipdb; ipdb.set_trace() ### XXX BREAKPOINT


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
