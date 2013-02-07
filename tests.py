from os import path as op

from inirama import Namespace
from logging import INFO
from unittest import TestCase

from starter.core import Starter, Template
from starter.main import PARSER


TESTDIR = op.join(op.dirname(__file__), 'tests')


class StarterTests(TestCase):

    def setUp(self):
        self.params = PARSER.parse_args(['test'])

    def test_template(self):
        ns = Namespace(template_dir=TESTDIR)
        t = Template('custom', ns)
        self.assertEqual(t.path, op.join(TESTDIR, 'custom'))
        files = list(t.files)
        self.assertEqual(len(files), 3)

        t1 = Template('custom', ns)
        self.assertEqual(t, t1)

        self.assertEqual(
            set((Template('custom', ns), Template('include', ns), Template('include', ns))),
            set((Template('custom', ns), Template('include', ns)))
        )

    def test_base(self):
        self.params.config = op.join(TESTDIR, 'custom.ini')

        starter = Starter(self.params, curdir=TESTDIR)
        self.assertEqual(starter.parser.default['current_dir'], TESTDIR)
        self.assertEqual(starter.parser.default['deploy_dir'], op.dirname(TESTDIR))
        self.assertEqual(starter.parser.default['template_dir'], op.dirname(TESTDIR))
        self.assertEqual(starter.parser.default['customkey'], 'customvalue')
        self.assertEqual(starter.logger.level, INFO)

    def test_copy(self):
        from tempfile import mkdtemp

        target_dir = mkdtemp()

        self.params.TEMPLATES = ['custom']
        self.params.source = TESTDIR
        self.params.target = target_dir

        starter = Starter(self.params, curdir=target_dir)
        self.assertEqual(starter.parser.default['deploy_dir'], target_dir)

        starter.copy()

        self.assertTrue(op.isfile(op.join(target_dir, 'root_file')))
        self.assertTrue(op.isfile(op.join(target_dir, 'dir', 'file')))
        t = op.join(target_dir, 'dir', 'template')
        b = open(t).read()
        self.assertTrue(target_dir in b)
        self.assertTrue(TESTDIR in b)
        self.assertTrue('customvalue' in b)

    def test_template_not_found(self):
        self.params.TEMPLATES = ['custom2']
        starter = Starter(self.params, curdir=TESTDIR)
        try:
            starter.copy()
        except AssertionError, e:
            self.assertTrue(e)
        except:
            raise

    def test_template_context(self):
        pass
