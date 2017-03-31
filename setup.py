#!/usr/bin/env python

try:
    from setuptools import setup
    requires = {
                'install_requires': ['tornado', 'gitpython', 'futures'],
                }
except ImportError:
    from distutils.core import setup
    requires = {}

setup(
    name                = 'Tammer',
    version             = '0.0.23',
    description         = 'Tammer project',
    author              = 'Omenia Ltd.',
    author_email        = 'contact@omenia.fi',
    url                 = 'http://omenia.fi/',
    platforms           = 'any',
    package_dir         = {'tammer' : 'src/tammer'},
    packages            = ['tammer'],
    package_data        = {'tammer': ['js/*', 'static/*.html', 'css/img/*.png', 'css/*.css']},
    **requires
    )
