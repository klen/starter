import sys

import logging
from functools import partial


# Logging utils
# =============

COLORS = lambda c, t: "\033[{0}m{1}\033[0m".format(c, t)
COLORS.red = partial(COLORS, 31)
COLORS.green = partial(COLORS, 32)
COLORS.yellow = partial(COLORS, 33)
COLORS.blue = partial(COLORS, 34)
COLORS.magenta = partial(COLORS, 35)
COLORS.cyan = partial(COLORS, 36)
COLORS.white = partial(COLORS, 37)


class ColoredFormater(logging.Formatter):
    """ Support terminal's colored output.
    """

    def format(self, record):
        s = logging.Formatter.format(self, record)

        # Debug
        if record.levelno <= logging.DEBUG:
            return s

        # INFO
        if record.levelno <= logging.INFO:
            return COLORS.green(s)

        # WARN
        if record.levelno <= logging.WARN:
            return COLORS.yellow(s)

        # ERROR
        return COLORS.red(s)


STREAM_HANDLER = logging.StreamHandler(sys.stdout)
if sys.stdout.isatty():
    STREAM_HANDLER.setFormatter(ColoredFormater())


def setup_logging(level):
    logging.root.setLevel(level)
    logging.root.addHandler(STREAM_HANDLER)
