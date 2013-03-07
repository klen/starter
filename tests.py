from os import path as op

from tempfile import mkdtemp
from unittest import TestCase

from starter.core import Starter, Template
from starter.log import setup_logging
from starter.main import PARSER


TESTDIR = op.join(op.dirname(__file__), 'tests')


class StarterTests(TestCase):

    def setUp(self):
        self.params = PARSER.parse_args(['test'])
        setup_logging(0)

    def test_template(self):

        t = Template('django', source='starter/templates/python-module')
        self.assertEqual(t.configuration, 'starter/templates/python-module.ini')

        t = Template('custom', tplparams=dict(custom=op.join(TESTDIR, 'custom')))
        self.assertEqual(t.name, 'custom')

        t = Template('python-module')
        self.assertEqual(op.basename(t.configuration), 'python-module.ini')
        self.assertTrue(t.path.endswith('starter/templates/python-module'))

        T = lambda n: Template(n, tpldirs=[TESTDIR])

        # Check base template properties
        t = T('custom')
        self.assertEqual(t.path, op.join(TESTDIR, 'custom'))
        self.assertEqual(len(list(t.files)), 4)
        self.assertEqual(t.configuration, op.join(TESTDIR, 'custom.ini'))

        t1 = T('custom')
        self.assertEqual(t, t1)

        self.assertEqual(
            set((T('custom'), T('include'), T('include'))),
            set((T('custom'), T('include')))
        )

    def test_starter_init(self):
        self.params.config = op.join(TESTDIR, 'custom.ini')
        starter = Starter(self.params, TESTDIR)
        self.assertEqual(starter.parser.default['deploy_dir'], op.dirname(TESTDIR))
        self.assertEqual(starter.parser.default['customkey'], 'customvalue')

        self.params.context = [('foo', 'bar')]
        starter = Starter(self.params, TESTDIR)
        self.assertEqual(starter.parser.default['foo'], 'bar')

    def test_starter_copy(self):
        target_dir = mkdtemp()

        self.params.TEMPLATES = ['custom']
        self.params.TARGET = target_dir

        starter = Starter(self.params, TESTDIR)
        self.assertEqual(starter.parser.default['deploy_dir'], target_dir)
        templates = starter.prepare_templates()
        self.assertTrue(templates)

        starter.copy()

        self.assertTrue(op.isfile(op.join(target_dir, 'root_file')))
        self.assertTrue(op.isfile(op.join(target_dir, 'dir', 'file')))
        t = op.join(target_dir, 'dir', 'template')
        with open(t) as f:
            body = f.read()
            self.assertTrue(target_dir in body)
            self.assertTrue('customvalue' in body)
            self.assertTrue('boss = {0}'.format(starter.parser.default['USER']) in body)

        f = op.join(target_dir, 'test_customvalue.ls')
        with open(f) as f:
            self.assertTrue(f)

    def test_template_not_found(self):
        self.params.TEMPLATES = ['custom2']
        starter = Starter(self.params, TESTDIR)
        try:
            starter.copy()
        except AssertionError as e:
            self.assertTrue(e)
        except:
            raise

    def test_builtin_templates(self):
        target_dir = mkdtemp()
        self.params.TEMPLATES = ['python-module']
        self.params.TARGET = target_dir

        starter = Starter(self.params)
        self.params.TARGET = mkdtemp()
        starter.parser.default['AUTHOR_NAME'] = 'John Conor'

        starter.copy()
        self.assertEqual(starter.parser.default['AUTHOR_NAME'], 'John Conor')
        with open(op.join(target_dir, 'LICENSE')) as f:
            body = f.read()
            self.assertTrue("Copyright (c) {0} by {1}".format(starter.parser.default['datetime'][:4], starter.parser.default['AUTHOR_NAME']) in body)
