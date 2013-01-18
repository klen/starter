from logging import INFO, getLogger
from unittest import TestCase

from os import path as op
from starter.core import Starter, Template
from starter.main import PARSER
from inirama import Namespace


TESTDIR = op.join(op.dirname(__file__), 'tests')


class StarterTests(TestCase):

    def setUp(self):
        self.params = PARSER.parse_args(['test'])

    def test_template(self):
        t = Template('custom', Namespace(
            template_dir=TESTDIR
        ), getLogger())
        self.assertEqual(t.path, op.join(TESTDIR, 'custom'))
        files = list(t.files)
        self.assertEqual(len(files), 2)

    def test_base(self):
        self.params.config = op.join(TESTDIR, 'custom.ini')

        starter = Starter(self.params, curdir=TESTDIR)
        self.assertEqual(starter.context['curdir'], TESTDIR)
        self.assertEqual(starter.context['deploy_dir'], op.dirname(TESTDIR))
        self.assertEqual(starter.context['template_dir'], op.dirname(TESTDIR))
        self.assertEqual(starter.context['customkey'], 'customvalue')
        self.assertEqual(starter.logger.level, INFO)

    def test_start(self):
        from tempfile import mkdtemp

        target_dir = mkdtemp()

        self.params.TEMPLATES = ['custom']
        self.params.source = TESTDIR
        self.params.target = target_dir

        starter = Starter(self.params, curdir=target_dir)
        self.assertEqual(
            starter.parser.default['deploy_dir'],
            target_dir
        )
        starter.start()

        self.assertTrue(op.isfile(op.join(
            target_dir, 'custom', 'root_file'
        )))
