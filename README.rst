|travis-master| |coverall-master| |doc-master| |pypi-downloads| |pypi-lastrelease| |python-versions|
|project-status| |project-license| |project-format| |project-implementation|

.. |travis-master| image:: https://travis-ci.org/alfred82santa/dirty-models.svg?branch=master   
    :target: https://travis-ci.org/alfred82santa/dirty-models
    
.. |coverall-master| image:: https://coveralls.io/repos/alfred82santa/dirty-models/badge.png?branch=master 
    :target: https://coveralls.io/r/alfred82santa/dirty-models?branch=master
    
.. |doc-master| image:: https://readthedocs.org/projects/dirty-models/badge/?version=latest
    :target: https://readthedocs.org/projects/dirty-models/?badge=latest
    :alt: Documentation Status
    
.. |pypi-downloads| image:: https://pypip.in/download/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Downloads
    
.. |pypi-lastrelease| image:: https://pypip.in/version/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Latest Version
    
.. |python-versions| image:: https://pypip.in/py_versions/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Supported Python versions
    
.. |project-status| image:: https://pypip.in/status/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Development Status

.. |project-license| image:: https://pypip.in/license/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: License

.. |project-format| image:: https://pypip.in/format/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Download format

.. |project-implementation| image:: https://pypip.in/implementation/dirty-models/badge.svg
    :target: https://pypi.python.org/pypi/dirty-models/
    :alt: Supported Python implementations


============
dirty-models
============
Dirty models for python 3

*************
Documentation
*************

http://dirty-models.readthedocs.org

********
Features
********
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
- HashMap model. It could be used instead of DynamicModel.
- FastDynamicModel. It could be used instead of DynamicModel. Same behavior, better performance.
- Pickable models.
- Datetime fields can use any datetime format using parser and formatter functions.
- No database dependent.

*********
Changelog
*********

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

************
Installation
************
.. code-block:: bash

    $ pip install dirty-models

******
Issues
******
- Getter and setter feature needs refactor to be able to use as decorators.
- DynamicModel is too strange. I don't trust in it. Try to use HashMapModel or FastDynamicModel.

***********
Basic usage
***********

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
    
Note:
-----

Look at tests for more examples
    

*****************
Performance Tests
*****************

.. code-block:: bash
   
   $ python3 performancerunner.py 
   DynamicModel start
   DynamicModel: iteration no. 0 start
   DynamicModel: iteration no. 0 => 0:00:02.528166
   DynamicModel: iteration no. 1 start
   DynamicModel: iteration no. 1 => 0:00:03.415274
   DynamicModel: iteration no. 2 start
   DynamicModel: iteration no. 2 => 0:00:03.115128
   DynamicModel: iteration no. 3 start
   DynamicModel: iteration no. 3 => 0:00:04.091488
   DynamicModel: iteration no. 4 start
   DynamicModel: iteration no. 4 => 0:00:05.275302
   DynamicModel => 0:00:18.425358
   FastDynamicModel start
   FastDynamicModel: iteration no. 0 start
   FastDynamicModel: iteration no. 0 => 0:00:01.351796
   FastDynamicModel: iteration no. 1 start
   FastDynamicModel: iteration no. 1 => 0:00:01.265681
   FastDynamicModel: iteration no. 2 start
   FastDynamicModel: iteration no. 2 => 0:00:01.270142
   FastDynamicModel: iteration no. 3 start
   FastDynamicModel: iteration no. 3 => 0:00:01.273443
   FastDynamicModel: iteration no. 4 start
   FastDynamicModel: iteration no. 4 => 0:00:01.280512
   FastDynamicModel => 0:00:06.441574
   BlobField start
   BlobField: iteration no. 0 start
   BlobField: iteration no. 0 => 0:00:00.000082
   BlobField: iteration no. 1 start
   BlobField: iteration no. 1 => 0:00:00.000027
   BlobField: iteration no. 2 start
   BlobField: iteration no. 2 => 0:00:00.000025
   BlobField: iteration no. 3 start
   BlobField: iteration no. 3 => 0:00:00.000024
   BlobField: iteration no. 4 start
   BlobField: iteration no. 4 => 0:00:00.000023
   BlobField => 0:00:00.000181
   {'DynamicModel': {'results': [datetime.timedelta(0, 2, 528166), datetime.timedelta(0, 3, 415274),
   datetime.timedelta(0, 3, 115128), datetime.timedelta(0, 4, 91488), datetime.timedelta(0, 5, 275302)],
   'total': datetime.timedelta(0, 18, 425358)}, 'FastDynamicModel': {'results': [datetime.timedelta(0, 1, 351796),
   datetime.timedelta(0, 1, 265681), datetime.timedelta(0, 1, 270142), datetime.timedelta(0, 1, 273443),
   datetime.timedelta(0, 1, 280512)], 'total': datetime.timedelta(0, 6, 441574)}, 'BlobField':
   {'results': [datetime.timedelta(0, 0, 82), datetime.timedelta(0, 0, 27), datetime.timedelta(0, 0, 25),
   datetime.timedelta(0, 0, 24), datetime.timedelta(0, 0, 23)], 'total': datetime.timedelta(0, 0, 181)}}
   
   
