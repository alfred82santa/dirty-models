import ast
import sys

import os
import re
from setuptools import setup

path = os.path.join(os.path.dirname(__file__), 'dirty_models', '__init__.py')

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

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
    version=version,
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
