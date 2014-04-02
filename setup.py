from setuptools import setup

setup(
    name='dirty-models',
    url='https://github.com/alfred82santa/dirty-models',
    author='alfred82santa',
    version='0.2.3',
    author_email='alfred82santa@gmail.com',
    packages=['dirty_models'],
    include_package_data=True,
    install_requires=['python-dateutil'],
    test_suite="nose.collector",
    tests_require="nose",
    zip_safe=True,
)
