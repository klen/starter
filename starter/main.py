import sys
from argparse import ArgumentParser

from . import CURDIR, __version__, __project__
from .core import Starter


# Command line parser
# ===================

PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument(
    'TEMPLATES', nargs='+', help='Clone templates')
PARSER.add_argument(
    '-s', dest='source', default=CURDIR, help='Template\'s source')
PARSER.add_argument(
    '-t', dest='target', default=CURDIR, help='Target path')
PARSER.add_argument(
    '-l', dest='level', default='info', help='Verbose level (info)',
    choices=['debug', 'info', 'warn', 'error', 'critical'])
PARSER.add_argument(
    '-c', '--config', help='Path to configuration file')
PARSER.add_argument(
    '-v', '--version', action='version',
    version=__version__, help='Show {0} version'.format(__project__))


def main(*args):
    params = PARSER.parse_args(args)
    starter = Starter(params)
    starter.start()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(*args)
