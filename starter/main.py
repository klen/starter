import sys

import logging
from argparse import ArgumentParser

from . import CURDIR, __version__, __project__


# Command line parser
# ===================

PARSER = ArgumentParser(description=__doc__)

PARSER.add_argument(
    'TEMPLATES', nargs='?',
    default='',
    help='Clone templates (comma separated list)',
    type=lambda s: list(filter(None, s.split(',')))
)

PARSER.add_argument(
    'TARGET', nargs='?', default=CURDIR, help='Target path')

PARSER.add_argument(
    '-s', dest='source', help='Template\'s source')

PARSER.add_argument(
    '-l', dest='level', default='warn', help='Verbose level (info)',
    choices=['debug', 'info', 'warn', 'error', 'critical'])

PARSER.add_argument(
    '-c', '--config', help='Path to configuration file')

PARSER.add_argument(
    '-x', dest='context', default=[], nargs='*',
    help='Define context (NAME:VALUE)', type=lambda s: s.partition(':')[::2])

PARSER.add_argument(
    '-t', '--list', action="store_true", help='List available templates')

PARSER.add_argument(
    '-i', '--interactive', dest='interactive', action='store_true',
    help='Start in interactive mode')

PARSER.add_argument(
    '-v', '--version', action='version', version=__version__,
    help='Show {0} version'.format(__project__))


def main(*args):
    """ Enter point. """
    args = args or sys.argv[1:]
    params = PARSER.parse_args(args)

    from .log import setup_logging
    setup_logging(params.level.upper())

    from .core import Starter
    starter = Starter(params)

    if not starter.params.TEMPLATES or starter.params.list:
        setup_logging('WARN')
        for t in sorted(starter.iterate_templates()):
            logging.warn("%s -- %s", t.name, t.params.get(
                'description', 'no description'))
        return True

    try:
        starter.copy()

    except Exception as e: # noqa
        logging.error(e)
        sys.exit(1)


if __name__ == '__main__':
    main()

# pymode:lint_ignore=W801
