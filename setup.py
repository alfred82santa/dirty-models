from setuptools import setup, find_packages

setup(
    name='dirty-models',
    url='https://github.com/alfred82santa/dirty-models',
    author='alfred82santa',
    version='0.1',
    author_email='alfred82santa@gmail.com',
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    test_suite="nose.collector",
    tests_require="nose",
    zip_safe=False,
)
