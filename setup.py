from setuptools import setup
import os

setup(
    name='dirty-models',
    url='https://github.com/alfred82santa/dirty-models',
    author='alfred82santa',
    version='0.6.3',
    author_email='alfred82santa@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta'],
    packages=['dirty_models'],
    include_package_data=True,
    install_requires=['python-dateutil'],
    description="Dirty models for python 3",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    test_suite="nose.collector",
    tests_require="nose",
    zip_safe=True,
)
