import sys
from argparse import ArgumentParser

from . import CURDIR, __version__, __project__
from itertools import izip_longest


# Command line parser
# ===================

PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument(
    'TEMPLATES', nargs='+', help='Clone templates')
PARSER.add_argument(
    '-s', dest='source', help='Template\'s source')
PARSER.add_argument(
    '-t', dest='target', default=CURDIR, help='Target path')
PARSER.add_argument(
    '-l', dest='level', default='info', help='Verbose level (info)',
    choices=['debug', 'info', 'warn', 'error', 'critical'])
PARSER.add_argument(
    '-c', '--config', help='Path to configuration file')
PARSER.add_argument(
    '-x', dest='context', default=[], nargs='*', help='Define context (NAME:VALUE)')
PARSER.add_argument(
    '-v', '--version', action='version',
    version=__version__, help='Show {0} version'.format(__project__))


if __name__ == '__main__':
    args = sys.argv[1:]
    params = PARSER.parse_args(args)

    from .log import setup_logging
    setup_logging(params.level.upper())

    from .core import Starter

    # Prepare user context
    context = dict()
    params.context = [next(m) for m in [izip_longest(fillvalue='', *([iter(p.split(':'))] * 2)) for p in params.context]]
    starter = Starter(params)
    starter.copy()
