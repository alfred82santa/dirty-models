|travis-master| |coverall-master| |doc-master| |pypi-downloads| |pypi-lastrelease| |python-versions|
|project-status| |project-license| |project-format| |project-implementation|

.. |travis-master| image:: https://travis-ci.org/alfred82santa/dirty-models.svg?branch=master
    :target: https://travis-ci.org/alfred82santa/dirty-models

.. |coverall-master| image:: https://coveralls.io/repos/alfred82santa/dirty-models/badge.svg?branch=master&service=github
    :target: https://coveralls.io/r/alfred82santa/dirty-models?branch=master

.. |doc-master| image:: https://readthedocs.org/projects/dirty-models/badge/?version=latest
    :target: http://dirty-models.readthedocs.io/?badge=latest
    :alt: Documentation Status

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Downloads

.. |pypi-lastrelease| image:: https://img.shields.io/pypi/v/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Latest Version

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Supported Python versions

.. |project-status| image:: https://img.shields.io/pypi/status/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Development Status

.. |project-license| image:: https://img.shields.io/pypi/l/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: License

.. |project-format| image:: https://img.shields.io/pypi/format/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Download format

.. |project-implementation| image:: https://img.shields.io/pypi/implementation/dirty-models.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Supported Python implementations


============
dirty-models
============

Dirty models for python 3

-------------
Documentation
-------------

http://dirty-models.readthedocs.io/

--------
Features
--------

- Python 3 package.
- Easy to create a model.
- Non destructive modifications.
- Non false positive modifications.
- Able to restore original data for each field or whole model.
- Access to original data.
- Read only fields.
- Alias for fields.
- Custom getters and setters for each fields.
- Automatic cast value.
- Easy import from/export to dict.
- Basic field type implemented.
- Multi type fields.
- Default values for each field or whole model.
- HashMap model. It could be used instead of DynamicModel.
- FastDynamicModel. It could be used instead of DynamicModel. Same behavior, better performance.
- Pickable models.
- Datetime fields can use any datetime format using parser and formatter functions.
- No database dependent.
- Auto documentation using https://github.com/alfred82santa/dirty-models-sphinx
- Opensource (BSD License)

---------
Changelog
---------


Version 0.6.2
-------------

- Improved datetime fields parser and formatter definitions. Now there are three ways to define them:

    * Format string to use both parse and formatter:

    .. code-block:: python

        class ExampleModel(BaseModel):
            datetime_field = DateTimeField(parse_format='%Y-%m-%dT%H:%M:%SZ')


    * Define a format string or function for parse and format datetime:

    .. code-block:: python

        class ExampleModel(BaseModel):
            datetime_field = DateTimeField(parse_format={'parser': callable_func,
                                                         'formatter': '%Y-%m-%dT%H:%M:%SZ'})

    * Use predefined format:

    .. code-block:: python

        DateTimeField.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }
        class ExampleModel(BaseModel):
            datetime_field = DateTimeField(parse_format='iso8061')


Version 0.6.1
-------------

- Improved model field autoreference.

.. code-block:: python

    class ExampleModel(BaseModel):
        model_field = ModelField()  # Field with a ExampleModel
        array_of_model = ArrayField(field_type=ModelField())  # Array of ExampleModels


Version 0.6.0
-------------

- Added default value for fields.

..  code-block:: python

    class ExampleModel(BaseModel):
        integer_field = IntegerField(default=1)

    model = ExampleModel()
    assert model.integer_field is 1

- Added default values at model level. Inherit default values could be override on new model classes.

..  code-block:: python

    class InheritExampleModel(ExampleModel):
        _default_data = {'integer_field': 2}

    model = InheritExampleModel()
    assert model.integer_field is 2

- Added multi type fields.

..  code-block:: python

    class ExampleModel(BaseModel):
        multi_field = MultiTypeField(field_types=[IntegerField(), StringField()])

    model = ExampleModel()
    model.multi_field = 2
    assert model.multi_field is 2

    model.multi_field = 'foo'
    assert model.multi_field is 'foo'

Version 0.5.2
-------------

- Fixed model structure.
- Makefile helpers.


Version 0.5.1
-------------

- Added a easy way to get model structure. It will be used by autodoc libraries as sphinx or json-schema.

Version 0.5.0
-------------

- Added autolist parameter to ArrayField. It allows to assign a single item to a list field,
  so it will be converted to a list with this value.

..  code-block:: python

    class ExampleModel(BaseModel):
        array_field = ArrayField(field_type=StringField(), autolist=True)

    model = ExampleModel()
    model.array_field = 'foo'
    assert model.array_field[0] is 'foo'

------------
Installation
------------

.. code-block:: bash

    $ pip install dirty-models

------
Issues
------

- Getter and setter feature needs refactor to be able to use as decorators.
- DynamicModel is too strange. I don't trust in it. Try to use HashMapModel or FastDynamicModel.

-----------
Basic usage
-----------

.. code-block:: python

    from dirty_models.models import BaseModel
    from dirty_models.fields import StringField, IntegerField

    class FooBarModel(BaseModel):
        foo = IntegerField()
        bar = StringField(name="real_bar")
        alias_field = IntegerField(alias=['alias1', 'alias2'])



    fb = FooBarModel()

    fb.foo = 2
    assert fb.foo is 2

    fb.bar = 'wow'
    assert fb.bar is 'wow'
    assert fb.real_bar is 'wow'

    fb.alias_field = 3
    assert fb.alias_field is 3
    assert fb.alias1 is fb.alias_field
    assert fb.alias2 is fb.alias_field


.. note::

    Look at tests for more examples
