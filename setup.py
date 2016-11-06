import sys

import os
import re
from setuptools import setup

import dirty_models

install_requires = ['python-dateutil']

if sys.version_info < (3, 4):
    install_requires.append('enum34')

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as desc_file:
    long_desc = desc_file.read()

invalid_roles = ['meth', 'class']

long_desc = re.sub(r':({}):`([^`]+)`'.format('|'.join(invalid_roles)), r'``\2``', long_desc, re.M)

setup(
    name='dirty-models',
    url='https://github.com/alfred82santa/dirty-models',
    author='alfred82santa',
    version=dirty_models.__version__,
    author_email='alfred82santa@gmail.com',
    license='BSD',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta'],
    packages=['dirty_models'],
    include_package_data=False,
    install_requires=install_requires,
    description="Dirty models for python 3",
    long_description=long_desc,
    test_suite="nose.collector",
    tests_require="nose",
    zip_safe=True,
)
