===============
Getting started
===============

-----
About
-----

Dirty Model is a Python library to define transactional models. It means a model itself has no
functionality. It just defines a structure in order to store data. It is almost true, but it doesn't.
A Dirty Model has some functionality: it could be modified storing changes. This is the main propose
of this library.

---------------------
How to define a model
---------------------

To define a model is a simple task. You may create a new model class which inherit from
:class:`dirty_models.models.BaseModel` and use our field descriptors to define your fields.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField()
        my_string_field = StringField()

It is all! You has a new model.

Dirty Models defines an useful set of field descriptors to store any type of data: integer, string, non-empty string,
float, date, time, datetime, timedelta, model, list of anything, hashmap, dynamic data, etc. You see all of them in
:doc:`fields`.

All of them defines some common parameters on constructor:


* ``default`` defines default value when a new model is instanced.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField(default=3)
        my_string_field = StringField()

    model = MyModel()

    assert model.my_int_field == 3 # True

* ``alias`` defines a list of alias for field. Alias could be used like regular field there is no differences. It is not
  a good practice to define alias for same data, but it useful in some scenarios.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField(default=3, alias=['integer_field'])
        my_string_field = StringField()

    model = MyModel()

    assert model.my_int_field == 3 # True
    assert model.integer_field == 3 # True

* ``name`` defines real field name. It will be used on export data for example. Some time you need to define
  a field with weird characters to fit to a third party API. So, you could define a real name with this parameter.
  If it is not defined, name used on model definition is assumed as real name. Otherwise if it is defined, name defined
  on model become an alias for field.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField(default=3, name='real_integer_field')
        my_string_field = StringField()

    model = MyModel()

    assert model.my_int_field == 3 # True
    assert model.real_integer_field == 3 # True

    print(model.export_data())
    # Prints
    # {'real_integer_field': 3}


* ``read_only`` defines whether field could be modified (easily). Of course, there are ways to modify it, but they
  must be used explicitly. See :class:`~dirty_models.base.Unlocker`.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField(default=3, read_only=True)
        my_string_field = StringField()

    model = MyModel()

    assert model.my_int_field == 3 # True

    # Non read only field
    model.my_string_field = 'string'
    assert model.my_string_field == 'string' # True

    # Read only field
    model.my_int_field = 4
    assert model.my_int_field == 4 # False
    assert model.my_int_field == 3 # True

* ``doc`` allows to define field docstring programmatically. But, don't worry, you could use docstrings on regular
  way.

* ``getter`` allows to define a function to get value.

* ``setter`` allows to define a function to set value.


---------------
How to set data
---------------

There are some ways to set data in models.


Assign value to a field
=======================

Probably the most easy is just assigning value to field:

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField(default=3, read_only=True)
        my_string_field = StringField()

    model = MyModel()

    model.my_int_field = 3
    assert model.my_int_field == 3 # True

Be aware, Dirty Model will try to cast value to field type. It means that you
could assign string value ``'3'`` to a integer field and it will be cast to ``3``. If value could not be
cast it will be ignored. ``None`` is a particular value, it removes data from field.

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField()
        my_string_field = StringField()

    model = MyModel()

    # Automatic cast
    model.my_int_field = '3'
    assert model.my_int_field == 3 # True
    assert model.my_int_field == '3' # False

    # Using None to remove data
    model.my_int_field = None
    assert model.my_int_field is None # True


Set data for whole model on contructor
======================================

Dictionary could be cast to model on contructor:

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField()
        my_string_field = StringField()

    model = MyModel(data={'my_int_field': 3, 'my_string_field': 'string'})

    assert model.my_int_field == 3 # True
    assert model.my_string_field == 'string' # True

On the other hand you could use keyword arguments to set some fields:

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField()
        my_string_field = StringField()

    model = MyModel(my_int_field=3, my_string_field='string')

    assert model.my_int_field == 3 # True
    assert model.my_string_field == 'string' # True


Import data
===========

Some time you want to set data to whole model, but model already exists, so you could import data:

.. code-block:: python

    class MyModel(BaseModel):

        my_int_field = IntegerField()
        my_string_field = StringField()

    model = MyModel()

    model.import_data({'my_int_field': 3, 'my_string_field': 'string'})

    assert model.my_int_field == 3 # True
    assert model.my_string_field == 'string' # True
