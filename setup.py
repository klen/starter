#!/usr/bin/env python

"""
Starter
-------

Starter -- Create the skeleton for new projects.

"""

from os import path as op, walk

from setuptools import setup, find_packages

from starter import __version__, __project__, __license__


def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

package_data = ['*.ini', '*.sh']
for root, dirs, files in walk(op.join(__project__, 'templates')):
    for filename in files:
        package_data.append("%s/%s" % (root[len(__project__) + 1:], filename))

setup(
    name=__project__,
    version=__version__,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' http://github.com/klen/starter',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    entry_points={
        'console_scripts': [
            'starter = starter.main:run',
        ]
    },

    packages = find_packages(),
    package_data=dict(starter=package_data),
    install_requires = [l for l in read('requirements.txt').split('\n') if l and not l.startswith('#')],
    test_suite = 'tests',
)
