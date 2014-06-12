#!/usr/bin/env python

""".

Starter
-------

Starter -- Create the skeleton for new projects.

"""
import re
from os import path as op, walk
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

_meta = _read('starter/__init__.py')
_license = re.search(r'^__license__\s*=\s*"(.*)"', _meta, re.M).group(1)
_project = re.search(r'^__project__\s*=\s*"(.*)"', _meta, re.M).group(1)
_version = re.search(r'^__version__\s*=\s*"(.*)"', _meta, re.M).group(1)

install_requires = [
    l for l in _read('requirements.txt').split('\n')
    if l and not l.startswith('#')]

tests_require = [
    l for l in _read('requirements-tests.txt').split('\n')
    if l and not l.startswith('#')]


class __PyTest(TestCommand):

    test_args = []
    test_suite = True

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


package_data = ['*.ini', '*.sh']
for root, dirs, files in walk(op.join(_project, 'templates')):
    for filename in files:
        package_data.append("%s/%s" % (root[len(_project) + 1:], filename))


setup(
    name=_project,
    version=_version,
    license=_license,
    description=_read('DESCRIPTION'),
    long_description=_read('README.rst'),
    platforms=('Any'),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' http://github.com/klen/starter',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
    ],

    entry_points={
        'console_scripts': [
            'starter = starter.main:main',
        ]
    },

    packages=find_packages(),
    package_data=dict(starter=package_data),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': __PyTest},
)
