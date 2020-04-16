|travis-master| |coverall-master| |doc-master| |pypi-lastrelease| |python-versions|
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

.. _Dirty Models Sphinx extension: http://dirty-models-sphinx-extension.readthedocs.io

============
Dirty Models
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
- Auto documentation using `Dirty Models Sphinx extension`_.
- Json encoder.
- Field access like dictionary but with wildcards.
- Opensource (BSD License)

---------
Changelog
---------

Version 0.12.3
--------------

* Fix HashMapsModel's hardcode field type.

Version 0.12.2
--------------

* Fix access to HashMapsModel's field type when it is hardcoded in a class.

Version 0.12.1
--------------

* Fix :class:`~dirty_models.fields.MultiFieldType` on creation mode.

* Fix :class:`~dirty_models.utils.BaseModelFormatterIter` to be aware about override access modes.

* Exposed all useful classes on package root.


Version 0.12.0
--------------

* Added `access_mode` property to fields.
  It could be :class:`~dirty_models.base.AccessMode.READ_AND_WRITE` in order to allow to read and write.
  :class:`~dirty_models.base.AccessMode.WRITABLE_ONLY_ON_CREATION` in order to set value only on creation.
  :class:`~dirty_models.base.AccessMode.READ_ONLY` in order to prevent writing.
  And :class:`~dirty_models.base.AccessMode.HIDDEN` in order to hide field.

* Old field property `read_only` is deprecated in favor of `access_mode` but it can be used like until this version.

* Helper :class:`~dirty_models.base.Creating` to mark model as in creation mode.

* Added class method :meth:`~dirty_models.models.BaseModel.create_new_model` build a model and insert data
  in creation mode.

* Allowed to override field access model on inherited fields using
  :attr:`~dirty_models.models.BaseModel.__override_field_access_modes__` hashmap.


Version 0.11.3
--------------

- Fix bug casting string negative float.
- Fix exception casting non valid values to enumerations.
- Added `title` property to fields.
- Added `metadata` property to fields. It could be used to store anything.
- Improved model formatter.

Version 0.11.2
--------------

- Fix bug #107.

- Added :class:`~dirty_models.utils.ModelIterator` class in order to be able to iterate over model fields.

  .. code-block:: python

     from dirty_models.utils import ModelIterator

     for fieldname, field_obj, value in ModelIterator(my_model):
         print('Field name: {}'.format(fieldname))
         print('Field alias: {}'.format(field_obj.alias))
         print('Field value: {}'.format(value))

- Some fixes about read only data.


Version 0.11.1
--------------

- Distribution fixes.


Version 0.11.0
--------------

- New field type :class:`~dirty_models.fields.BytesField`.

- String to integer casting could use any format allowed by Python: HEX (`0x23`), OCT (`0o43`) or
  no-meaning underscores (`1_232_232`, only since Python 3.6).

Version 0.10.1
--------------

- :class:`Factory<dirty_models.utils>` feature. It allows to define a factory as
  default value in order to be executed each time model is instanced. (Issue #100)

  .. code-block:: python

     from dirty_models.utils import factory
     from datetime import datetime

     class Model(BaseModel):

        field_1 = DateTimeField(default=factory(datetime.now))

     model = Model()
     print(model.field_1)

     # 2017-11-02 21:52:46.339040

- Makefile fixes.
- Python 3.6 is supported officially. It works since first day, but now tests run on Travis for Python 3.6.

Version 0.10.0
--------------

- Pickable lists.
- Improved pickle performance.
- Setting ``None`` to a field remove content.
- More tests.
- Some code improvements.

Version 0.9.2
-------------

- Fix timezone when convert timestamp to datetime.

Version 0.9.1
-------------

- Fix installation.

Version 0.9.0
-------------

- New EnumField.
- Fixes on setup.py.
- Fixes on requirements.
- Fixes on formatter iters.
- Fixes on code.
- Added ``__version__`` to main package file.
- Synchronized version between main packege file, ``setup.py`` and docs.
- Export only modifications.


Version 0.8.1
-------------

- Added __contains__ function to models and lists. It allows to use ``in`` operator.
- Added ``default_timezone`` parameter to DateTimeFields and TimeFields. If value entered has no a timezone
  defined, default one will be set.
- Added ``force_timezone`` parameter to DateTimeFields in order to convert values to a specific timezone.
- More cleanups.

Version 0.8.0
-------------

- Renamed internal fields. Now they use double score format ``__fieldname__``.
- Raise a RunTimeError exception if two fields use same alias in a model.
- Fixed default docstrings.
- Cleanup default data. Only real name fields are allowed to use as key.
- Added :meth:`~dirty_models.models.BaseModel.get_attrs_by_path` in order to get all values using path.
- Added :meth:`~dirty_models.models.BaseModel.get_1st_attr_by_path` in order to get first value using path.
- Added option to access fields like in a dictionary, but using wildcards. Only for getters.
  See: :meth:`~dirty_models.models.BaseModel.get_1st_attr_by_path`.
- Added some documentation.

Version 0.7.2
-------------

- Fixed inherited structure
- Added ``get_default_data`` method to models in order to retrieve default data.

Version 0.7.1
-------------

- Solved problem formatting dynamic models
- Added date, time and timedelta fields to dynamic models.

Version 0.7.0
-------------

- Timedelta field
- Generic formatters
- Json encoder

.. code-block:: python

    import json
    from datetime import datetime
    from dirty_models import BaseModel, DatetimeField
    from dirty_models.utils import JSONEncoder


    class ExampleModel(BaseModel):
        field_datetime = DatetimeField(parse_format="%Y-%m-%dT%H:%M:%S")

    model = ExampleModel(field_datetime=datetime.now())

    assert json.dumps(model, cls=JSONEncoder) == '{"field_datetime": "2016-05-30T22:22:22"}'

- Auto camelCase fields metaclass


Version 0.6.3
-------------

- Documentation fixed.
- Allow import main members from root package.

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
        __default_data__ = {'integer_field': 2}

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
    assert fb['alias_field'] is 3

.. note::

    More examples and documentation on http://dirty-models.readthedocs.io/
