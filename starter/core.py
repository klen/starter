import errno
import logging
import sys
import shutil
from os import path as op, walk, environ, makedirs
from jinja2 import Environment, FileSystemLoader

from . import CFGFILE, CURDIR


# Logging utils
# =============

def _wrap_with(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;" + c
        return "\033[{code}m{text}\033[0m".format(code=c, text=text)
    return inner


class ColoredFormater(logging.Formatter):
    """ Support terminal's colored output.
    """
    colors = lambda x: x
    colors.red = _wrap_with('31')
    colors.green = _wrap_with('32')
    colors.yellow = _wrap_with('33')
    colors.blue = _wrap_with('34')
    colors.magenta = _wrap_with('35')
    colors.cyan = _wrap_with('36')
    colors.white = _wrap_with('37')

    def format(self, record):
        s = logging.Formatter.format(self, record)

        # Debug
        if record.levelno == logging.DEBUG:
            return s

        # INFO
        if record.levelno == logging.INFO:
            return self.colors.white(s, bold=True)

        # WARN
        if record.levelno == logging.WARN:
            return self.colors.cyan("[WARN] " + s, bold=True)

        # ERROR
        return self.colors.red(s, bold=True)


STREAM_HANDLER = logging.StreamHandler(sys.stdout)
if sys.stdout.isatty():
    STREAM_HANDLER.setFormatter(ColoredFormater())


# Application
# ===========

class FS(object):
    """ File system interface.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def make_directory(self, path):
        """ Creates directory if that not exists.
        """
        try:
            makedirs(path)
            self.logger and self.logger.info('Directory created: {0}'.format(path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def copy_file(self, from_path, to_path):
        """ Copy file.
        """
        if not op.exists(op.dirname(to_path)):
            self.make_directory(op.dirname(to_path))

        shutil.copy(from_path, to_path)
        self.logger and self.logger.info('File copied: {0}'.format(to_path))


class Template(FS):

    tmpl_ext = '.tmpl'

    def __init__(self, name, ns, logger=None):
        self.name = name

        path = ns['templates'].get(name, name)

        self.path = (path or '').rstrip(op.sep)
        if not op.exists(self.path):
            self.path = op.join(ns.default['template_dir'], self.path)
        assert op.exists(self.path), "Template not found."

        self.env = Environment(loader=FileSystemLoader(self.path))

        super(Template, self).__init__(logger)

    @property
    def files(self):
        for root, _, files in walk(self.path):
            for f in filter(lambda x: x != CFGFILE, files):
                source = op.join(root, f)
                target = op.relpath(source, self.path)
                yield source, target

    def paste(self, deploy_dir, **context):
        for source, rel in self.files:
            target = op.join(deploy_dir, rel)
            if not rel.endswith(self.tmpl_ext):
                self.copy_file(source, target)
                continue

            with open(target[:-len(self.tmpl_ext)], 'w') as f:
                t = self.env.get_template(rel)
                f.write(t.render(**context))

    def __eq__(self, other):
        if isinstance(other, Template):
            return other.name == self.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "<Template: {0}>".format(self.path)


class Starter(FS):

    default_configs = map(lambda d: op.abspath(op.join(d, CFGFILE)), [
        environ.get('HOME', '~'),
        CURDIR
    ])

    def __init__(self, params, curdir=None, cfg_files=None):
        self.params = params
        self.curdir = op.abspath(curdir or CURDIR)

        self.setup_logger(params.level)
        self.setup_parser(*(cfg_files or []))

        self.logger.info('Starting templates: ' + str(self.params.TEMPLATES))

        self.make_directory(params.target)
        super(Starter, self).__init__(self.logger)

    def setup_logger(self, level='info'):
        """ Set logging.
        """
        self.logger = logging.getLogger('Starter')
        self.logger.setLevel(level.upper())
        self.logger.addHandler(STREAM_HANDLER)

    def setup_parser(self, *cfg_files):
        """ Load configuration.
        """
        from inirama import InterpolationNamespace

        self.parser = InterpolationNamespace(
            current_dir=self.curdir,
            deploy_dir=self.params.target,
            template_dir=self.params.source)
        cfg_files = cfg_files or self.default_configs
        self.parser.read(*cfg_files)
        self.parser.read(self.params.config)

    def copy(self):
        """ Copy structure.
        """
        templates = set(self.params.TEMPLATES)

        def paste(tname):
            t = Template(tname, self.parser, self.logger)
            t.paste(**self.parser.default)

        return map(paste, templates)

    def __repr__(self):
        return "<Starter '{0}'>".format(self.curdir)
