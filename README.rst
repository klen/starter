Starter
#######

.. _description:

Starter -- Create the skeleton for new projects.

.. _badges:

.. image:: https://secure.travis-ci.org/klen/starter.png?branch=develop
    :target: http://travis-ci.org/klen/starter
    :alt: Build Status

.. image:: https://coveralls.io/repos/klen/starter/badge.png?branch=develop
    :target: https://coveralls.io/r/klen/starter
    :alt: Coverals

.. image:: https://pypip.in/v/Starter/badge.png
    :target: https://crate.io/packages/starter
    :alt: Version

.. image:: https://pypip.in/d/Starter/badge.png
    :target: https://crate.io/packages/starter
    :alt: Downloads

.. image:: https://dl.dropboxusercontent.com/u/487440/reformal/donate.png
    :target: https://www.gittip.com/klen/
    :alt: Donate


.. _documentation:

**Docs are available at https://starter.readthedocs.org/. Pull requests with documentation enhancements and/or fixes are awesome and most welcome.**


.. _contents:

.. contents::


.. _requirements:

Requirements
=============

- python >= (2.6, 2.7, 3.3)


.. _installation:

Installation
=============

**Starter** should be installed using pip: ::

    pip install starter



.. _usage:

Usage
=====
::

    $ starter --help
    usage: starter [-h] [-s SOURCE] [-l {debug,info,warn,error,critical}]
                [-c CONFIG] [-x [CONTEXT [CONTEXT ...]]] [-v]
                TEMPLATES [TARGET]

    positional arguments:
    TEMPLATES             Clone templates (comma separated list)
    TARGET                Target path

    optional arguments:
    -h, --help            show this help message and exit
    -s SOURCE             Template's source
    -l {debug,info,warn,error,critical}
                            Verbose level (info)
    -c CONFIG, --config CONFIG
                            Path to configuration file
    -x [CONTEXT [CONTEXT ...]]
                            Define context (NAME:VALUE)
    -v, --version         Show Starter version



.. _bagtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/starter/issues


.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/klen/starter


.. _license:

License
=======

Licensed under a `BSD license`_.


.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.com/
