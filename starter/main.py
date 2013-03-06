import sys
from argparse import ArgumentParser

from . import CURDIR, __version__, __project__
try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest


# Command line parser
# ===================

PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument(
    'TEMPLATES', help='Clone templates (comma separated list)')
PARSER.add_argument(
    'TARGET', nargs='?', default=CURDIR, help='Target path')
PARSER.add_argument(
    '-s', dest='source', help='Template\'s source')
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


def run(*args):
    args = args or sys.argv[1:]
    params = PARSER.parse_args(args)
    params.TEMPLATES = filter(None, params.TEMPLATES.split(','))

    from .log import setup_logging
    setup_logging(params.level.upper())

    from .core import Starter

    # Prepare user context
    params.context = [
        next(m)
        for m in [
            zip_longest(fillvalue='', *([iter(p.split(':'))] * 2))
            for p in params.context]]

    starter = Starter(params)
    try:
        starter.copy()
    except Exception as e:
        import logging
        logging.error(e)


if __name__ == '__main__':
    run()

# pymode:lint_ignore=W801
