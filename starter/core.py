import errno
from os import path as op, walk, environ, makedirs
from datetime import datetime

import logging
import shutil
import re
from functools import partial
from jinja2 import Environment, FileSystemLoader
from oset import oset
from inirama import InterpolationNamespace

from . import CFGFILE, CURDIR, TPLDIR


# Application
# ===========

class FS(object):
    """ File system interface.
    """
    @staticmethod
    def make_directory(path):
        """ Creates directory if that not exists.
        """
        try:
            makedirs(path)
            logging.debug('Directory created: {0}'.format(path))

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def copy_file(self, from_path, to_path):
        """ Copy file.
        """
        if not op.exists(op.dirname(to_path)):
            self.make_directory(op.dirname(to_path))

        shutil.copy(from_path, to_path)
        logging.debug('File copied: {0}'.format(to_path))


class Template(FS):

    tpl_ext = '.tmpl'
    cfg_ext = '.ini'
    dirs = [TPLDIR]
    var_re = re.compile('\+([^\+]+)\+')

    def __init__(self, name, source=None, tplparams=None, tpldirs=None):
        self.name = name

        tplparams = tplparams or dict()
        source = (source or tplparams.get(name, name)).rstrip(op.sep).replace('.', op.sep)
        tpldirs = list(self.dirs + (tpldirs or []))

        self.path = source
        while not op.exists(self.path) and tpldirs:
            self.path = op.join(tpldirs.pop(), source)
        assert op.exists(self.path), "Template not found."

        self.env = Environment(loader=FileSystemLoader(self.path))

    @property
    def files(self):
        for root, _, files in walk(self.path):
            for f in filter(lambda x: x != CFGFILE, files):
                source = op.join(root, f)
                target = op.relpath(source, self.path)
                yield source, target

    @property
    def configuration(self):
        name = op.basename(self.path)
        return op.join(op.dirname(self.path), '{0}{1}'.format(name, self.cfg_ext))

    def paste(self, **context):
        logging.info('Paste template: {0}'.format(self.name))
        for source, rel in self.files:
            target = op.join(context.get('deploy_dir', CURDIR), rel)

            # Interpolate vars in file path
            target = self.var_re.sub(lambda m: context.get(m.group(1), ''), target)

            if not rel.endswith(self.tpl_ext):
                self.copy_file(source, target)
                continue

            target = target[:-len(self.tpl_ext)]
            self.make_directory(op.dirname(target))
            with open(target, 'w') as f:
                t = self.env.get_template(rel)
                f.write(t.render(**context))
                logging.debug('Template rendered: `{0}`'.format(f.name))

    def __eq__(self, other):
        if isinstance(other, Template):
            return other.path == self.path
        return False

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return "<Template: {0}>".format(self.path)


class Starter(FS):

    default_configs = map(lambda d: op.abspath(op.join(d, CFGFILE)), [
        environ.get('HOME', '~'),
        CURDIR
    ])
    include_key = '__include__'

    def __init__(self, params, *tpldirs):
        self.params = params
        self.tpldirs = list(tpldirs)
        self.parser = InterpolationNamespace(
            current_dir=CURDIR,
            deploy_dir=self.params.target,
            datetime=datetime.now(),
            USER=environ.get("USER"),
            **dict(params.context)
        )
        self.parser.read(*self.default_configs)
        self.parser.read(self.params.config)

    def copy(self):
        """ Copy structure.
        """
        templates = self.prepare_templates()
        self.parser.default['templates'] = tt = ','.join(t.name for t in templates)
        logging.warning("Paste templates: {0}".format(tt))
        self.make_directory(self.params.target)
        return map(lambda t: t.paste(**self.parser.default), templates)

    def prepare_templates(self):
        to_template = partial(map, lambda t: Template(t, tpldirs=self.tpldirs))
        templates = to_template(self.params.TEMPLATES)
        cache = set(templates)

        def open_templates(*templates):

            for t in templates:
                self.parser.read(t.configuration, update=False)
                cache.add(t)

                try:
                    include = self.parser['templates'].pop(self.include_key)
                    include = filter(lambda x: x, oset(
                        include.replace(' ', '').split(',')))
                    requirements = filter(
                        lambda t: not t in cache, to_template(include))
                    for tt in open_templates(*requirements):
                        yield tt
                except KeyError:
                    pass

                yield t

        return list(open_templates(*templates))

    def __repr__(self):
        return "<Starter '{0}'>".format(CURDIR)
