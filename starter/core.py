import errno
import re
from datetime import datetime
from os import path as op, walk, environ, makedirs, listdir

import logging
import shutil
from functools import partial
from inirama import InterpolationNamespace, InterpolationSection
from jinja2 import Environment, FileSystemLoader, Template as JinjaTemplate
from oset import oset

from . import CFGFILE, CURDIR, BUILTIN_TMPLDIR, HOME_TMPLDIR_NAME, _compat


# Application
# ===========

class JinjaInterpolationSection(InterpolationSection):

    """ Interpolate Jinja vars in ini files. """

    var_re = re.compile('{{([^}]+)}}')

    def __interpolate__(self, math):
        t = JinjaTemplate(math.group(0))
        return t.render(**dict(self.items(raw=True)))


class JinjaInterpolationNamespace(InterpolationNamespace):

    """ Interpolate Jinja vars in ini files. """

    section_type = JinjaInterpolationSection


class FS(object):

    """ File system interface. """

    @staticmethod
    def make_directory(path):
        """ Create directory if that not exists. """
        try:
            makedirs(path)
            logging.debug('Directory created: {0}'.format(path))

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def copy_file(self, from_path, to_path):
        """ Copy file. """
        if not op.exists(op.dirname(to_path)):
            self.make_directory(op.dirname(to_path))

        shutil.copy(from_path, to_path)
        logging.debug('File copied: {0}'.format(to_path))


class Template(FS):

    """ Implement template object. """

    tpl_ext = '.j2'
    var_re = re.compile(r'\{\{([^\}]+)\}\}')

    def __init__(self, name, source='', dirs=None):
        self.name = name
        self.path = source
        dirs = list(dirs or [])
        try:
            while not op.exists(self.configuration):
                self.path = op.join(dirs.pop(), name)
        except (IndexError, AttributeError):
            raise ValueError("Template `%s` not found." % name)

        self.env = Environment(loader=FileSystemLoader(self.path))

    def __eq__(self, other):
        if isinstance(other, Template):
            return other.path == self.path
        return False

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return "<Template: {0}>".format(self.path)

    @property
    def files(self):
        for root, _, files in walk(self.path):
            for f in [x for x in files if x != CFGFILE]:
                source = op.join(root, f)
                target = op.relpath(source, self.path)
                yield source, target

    @property
    def configuration(self):
        """ Return path to template configuration. """
        return op.join(self.path, CFGFILE)

    @property
    def params(self):
        """ Read self params from configuration. """
        parser = JinjaInterpolationNamespace()
        parser.read(self.configuration)
        return dict(parser['params'] or {})

    def paste(self, **context):
        logging.info('Paste template: {0}'.format(self.name))
        for source, rel in self.files:
            target = op.join(context.get('_TRGDIR', CURDIR), rel)

            # Interpolate vars in file path
            target = self.var_re.sub(
                lambda m: context.get(m.group(1), ''), target)

            # Copy files
            if not rel.endswith(self.tpl_ext):
                self.copy_file(source, target)
                continue

            # Render and copy templates
            target = target[:-len(self.tpl_ext)]
            self.make_directory(op.dirname(target))
            with open(target, 'w') as f:
                t = self.env.get_template(rel)
                f.write(t.render(**context))
                logging.debug('Template rendered: `{0}`'.format(f.name))

    @classmethod
    def scan(cls, path):
        """ Scan directory for templates. """
        result = []
        try:
            for _p in listdir(path):
                try:
                    result.append(Template(_p, op.join(path, _p)))
                except ValueError:
                    continue
        except OSError:
            pass

        return result


class Starter(FS):

    """ Clone templates to file system. """

    # Seek user configs
    default_configs = [
        op.abspath(op.join(path, CFGFILE)) for path in (
            environ.get('HOME', '~'), CURDIR)
    ]

    # Seek templates
    default_tmpldirs = [
        op.join(environ.get('HOME', '~'), HOME_TMPLDIR_NAME), BUILTIN_TMPLDIR]

    def __init__(self, params, *dirs):
        """ Save params and create INI parser. """
        self.params = params
        self.dirs = list(dirs) + self.default_tmpldirs

        # Initialize parser
        context = {
            '_TRGDIR': self.params.TARGET,
            '_CURDIR': CURDIR,
            '_USER': environ.get("USER"),
            '_DATETIME': datetime.now(),
        }
        context.update(params.context)
        self.parser = JinjaInterpolationNamespace(**context)
        self.parser.read(*self.default_configs)
        self.parser.read(self.params.config)

    def copy(self):
        """ Prepare and paste self templates. """
        templates = self.prepare_templates()
        if self.params.interactive:
            keys = list(self.parser.default)
            for key in keys:
                if key.startswith('_'):
                    continue
                prompt = "{0} (default is \"{1}\")? ".format(
                    key, self.parser.default[key])

                if _compat.PY2:
                    value = raw_input(prompt.encode('utf-8')).decode('utf-8')
                else:
                    value = input(prompt.encode('utf-8'))

                value = value.strip()
                if value:
                    self.parser.default[key] = value

        self.parser.default['templates'] = tt = ','.join(
            t.name for t in templates)
        logging.warning("Paste templates: {0}".format(tt))
        self.make_directory(self.params.TARGET)

        logging.debug("\nDefault context:\n----------------")
        logging.debug(
            ''.join('{0:<15} {1}\n'.format(*v)
                    for v in self.parser.default.items())
        )
        return [t.paste(
            **dict(self.parser.default.items())) for t in templates]

    def prepare_templates(self):
        to_template = partial(map, lambda t: Template(t, dirs=self.dirs))
        templates = list(to_template(self.params.TEMPLATES))
        cache = set(templates)

        def open_templates(*templates):

            for t in templates:
                self.parser.read(t.configuration, update=False)
                cache.add(t)

                try:
                    include = self.parser['params'].pop('include')
                    include = filter(None, oset(
                        include.replace(' ', '').split(',')))
                    requirements = filter(  # noqa
                        lambda t: t not in cache, to_template(include))
                    for tt in open_templates(*requirements):
                        yield tt
                except KeyError:
                    pass

                yield t

        return list(open_templates(*templates))

    def iterate_templates(self):
        """ Iterate self starter templates.

        :returns: A templates generator

        """
        return [t for dd in self.dirs for t in Template.scan(dd)]

    def __repr__(self):
        return "<Starter '%s'>" % CURDIR
