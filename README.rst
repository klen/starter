Starter
#######

Starter -- Create the skeleton for new projects.

.. image:: https://secure.travis-ci.org/klen/starter.png?branch=develop
    :target: http://travis-ci.org/klen/starter
    :alt: Build Status

.. contents::

Requirements
=============

- python >= 2.7, 3.3


Installation
=============

**Starter** should be installed using pip: ::

    pip install starter


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


Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/starter/issues


Contributing
============

Development of starter happens at github: https://github.com/klen/starter


Contributors
=============

* klen_ (Kirill Klenov)


License
=======

Licensed under a `BSD license`_.


.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.com/
