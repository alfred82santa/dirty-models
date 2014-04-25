|travis-master| |coverall-master|

.. |travis-master| image:: https://travis-ci.org/alfred82santa/dirty-models.svg?branch=master   
    :target: https://travis-ci.org/alfred82santa/dirty-models
    
.. |coverall-master| image:: https://coveralls.io/repos/alfred82santa/dirty-models/badge.png?branch=master 
    :target: https://coveralls.io/r/alfred82santa/dirty-models?branch=master

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
- Pickable models.
- No database dependent.

************
Installation
************
.. code-block:: bash

    $ pip install dirty-models

******
Issues
******
- Getter and setter feature needs refactor to be able to use as decorators.
- DynamicModel is too strange. I don't trust in it.

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
    
.. note:: 
    Look at tests for more examples
    

