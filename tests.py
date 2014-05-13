from os import path as op
import pytest

from starter.core import Starter, Template


TESTDIR = op.join(op.dirname(__file__), 'tests', 'templates')


@pytest.fixture(scope='module')
def params():
    from starter.log import setup_logging
    from starter.main import PARSER

    setup_logging(0)
    return PARSER.parse_args(['test'])


def test_parse(params):
    from starter.main import PARSER

    params = PARSER.parse_args([
        "python-package", "mirror", "-x", "MODULE:mirror",
        "AUTHOR:user", "blabla"
    ])
    assert params.TARGET == "mirror"
    assert params.TEMPLATES == ["python-package"]
    assert params.context == [
        ("MODULE", "mirror"), ("AUTHOR", "user"), ("blabla", "")]


def test_template(params):

    templates = Template.scan(TESTDIR)
    assert len(templates) == 3

    t = Template('django', source='starter/templates/python-package')
    assert t.configuration == 'starter/templates/python-package/starter.ini'

    t = Template('python-package', dirs=Starter.default_tmpldirs)
    assert t.path.endswith('starter/templates/python-package')

    T = lambda n: Template(n, dirs=[TESTDIR])

    # Check base template properties
    t = T('custom')
    assert t.path == op.join(TESTDIR, 'custom')
    assert len(list(t.files)) == 4
    assert t.configuration == op.join(TESTDIR, t.name, 'starter.ini')

    t1 = T('custom')
    assert t == t1

    assert (
        set((T('custom'), T('include'), T('include'))) == set((T('custom'), T('include'))) # noqa
    )


def test_starter_init(params):
    params.config = op.join(op.dirname(TESTDIR), 'config.ini')

    starter = Starter(params, TESTDIR)
    assert starter.parser.default['_TRGDIR'] == params.TARGET
    assert starter.parser.default['customkey'] == 'customvalue'

    params.context = [('foo', 'bar')]
    starter = Starter(params, TESTDIR)
    assert starter.parser.default['foo'] == 'bar'


def test_starter_copy(params, tmpdir):

    tmpdir = str(tmpdir)
    params.TEMPLATES = ['custom']
    params.TARGET = tmpdir

    starter = Starter(params, TESTDIR)
    assert starter.parser.default['_TRGDIR'] == tmpdir

    templates = starter.prepare_templates()
    assert [t.name for t in templates] == ['include', 'john', 'custom']

    starter.copy()

    assert op.isfile(op.join(tmpdir, 'root_file'))

    assert op.isfile(op.join(tmpdir, 'dir', 'file'))
    t = op.join(tmpdir, 'dir', 'template')

    with open(t) as f:
        body = f.read()
        assert tmpdir in body
        assert 'customvalue' in body
        assert 'boss = %s' % starter.parser.default['_USER'] in body

    f = op.join(tmpdir, 'test_customvalue.ls')
    with open(f) as f:
        assert f


def test_template_not_found(params):
    params.TEMPLATES = ['custom2']
    starter = Starter(params, TESTDIR)
    with pytest.raises(ValueError):
        starter.copy()


def test_builtin_templates(params, tmpdir):
    tmpdir = str(tmpdir)

    params.TEMPLATES = ['python-package']
    params.TARGET = tmpdir

    starter = Starter(params)
    starter.parser.default['AUTHOR_NAME'] = 'John Conor'

    starter.copy()
    assert starter.parser.default['AUTHOR_NAME'] == 'John Conor'

    with open(op.join(tmpdir, 'LICENSE')) as f:
        body = f.read()
        assert ("Copyright (c) {0}, {1}".format(
                starter.parser.default['_DATETIME'][:4],
                starter.parser.default['AUTHOR_NAME']) in body)


def test_list_templates(params):
    starter = Starter(params)
    assert 'python-package' in [t.name for t in starter.iterate_templates()]

    starter = Starter(params, TESTDIR)
    assert 'custom' in [t.name for t in starter.iterate_templates()]

# pylama:ignore=W0621
