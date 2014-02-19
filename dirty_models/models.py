"""
models.py

Base model for dirty_models.
"""

from .fields import BaseField, ModelField, ArrayField
from dirty_models.fields import IntegerField, FloatField, BooleanField, StringField, DateTimeField
from datetime import datetime
from dirty_models.types import ListModel


class DirtyModelMeta(type):

    """
    Metaclass for dirty_models. It sets automatic fieldnames and
    automatic model_class for ModelField fields.
    """

    def __new__(cls, name, bases, classdict):
        result = super(DirtyModelMeta, cls).__new__(
            cls, name, bases, classdict)

        fields = {key: field for key, field in result.__dict__.items()}

        for key, field in fields.items():
            if isinstance(field, BaseField):
                cls.process_base_field(cls, field, key, result)
        return result

    def process_base_field(cls, field, key, instance):
        """
        Preprocess class fields.
        """
        if not field.name:
            field.name = key
        elif key != field.name:
            setattr(instance, field.name, field)
        if isinstance(field, ModelField) and not field.model_class:
            field.model_class = instance
        if isinstance(field, ArrayField) and isinstance(field.field_type, ModelField) \
                and not field.field_type.model_class:
            field.field_type.model_class = instance


class BaseModel(metaclass=DirtyModelMeta):

    """
    Base model with dirty feature. It store original data and save
    modifications in other side.
    """

    def __init__(self, data=None, **kwargs):
        self._original_data = {}
        self._modified_data = {}
        self._deleted_fields = []
        if isinstance(data, dict):
            self.import_data(data)
        self.import_data(kwargs)

    def set_field_value(self, name, value):
        """
        Set the value to the field modified_data
        """
        if name in self._deleted_fields:
            self._deleted_fields.remove(name)
        if self._original_data.get(name) == value:
            if self._modified_data.get(name):
                self._modified_data.pop(name)
        else:
            self._modified_data[name] = value

    def get_field_value(self, name):
        """
        Get the field value from the modified data or the original one
        """
        if name in self._deleted_fields:
            return None
        modified = self._modified_data.get(name)
        if modified is not None:
            return modified
        return self._original_data.get(name)

    def delete_field_value(self, name):
        """
        Mark this field to be deleted
        """
        if self._original_data.get(name) or self._modified_data.get(name):
            if self._modified_data.get(name):
                self._modified_data.pop(name)
            self._deleted_fields.append(name)

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def export_data(self):
        """
        Get the results with the modified_data
        """
        result = {}
        data = self._original_data.copy()
        data.update(self._modified_data)
        for key, value in data.items():
            if key not in self._deleted_fields:
                try:
                    result[key] = value.export_data()
                except AttributeError:
                    result[key] = value

        return result

    def export_modified_data(self):
        """
        Get the modified data
        """
        # TODO: why None? Try to get a better flag
        result = {key: None for key in self._deleted_fields}

        for key, value in self._modified_data.items():
            if key not in result.keys():
                try:
                    result[key] = value.export_modified_data()
                except AttributeError:
                    result[key] = value

        for key, value in self._original_data.items():
            if key not in result.keys():
                try:
                    result[key] = value.export_modified_data()
                except AttributeError:
                    pass

        return result

    def export_deleted_fields(self):
        """
        Resturns a list with any deleted fields form original data.
        In tree models, deleted fields on children will be appended.
        """
        result = self._deleted_fields.copy()

        for key, value in self._original_data.items():
            if key not in result:
                try:
                    partial = value.export_deleted_fields()
                    for key2 in partial:
                        result.append(key + '.' + key2)
                except AttributeError:
                    pass

        return result

    def flat_data(self):
        """
        Pass all the data from modified_data to original_data
        """
        def flat_field(value):
            """
            Flat field data
            """
            try:
                value.flat_data()
                return value
            except AttributeError:
                return value

        modified_dict = self._original_data
        modified_dict.update(self._modified_data)
        self._original_data = dict((k, flat_field(v))
                                   for k, v in modified_dict.items()
                                   if k not in self._deleted_fields)

        self.clear_modified_data()

    def clear_modified_data(self):
        """
        Clears only the modified data
        """
        self._modified_data = {}
        self._deleted_fields = []

    def clear(self):
        """
        Clears all the data in the object
        """
        self._modified_data = {}
        self._original_data = {}
        self._deleted_fields = []


class DynamicModel(BaseModel):

    """
    DynamicModel allow to create model with no structure. Each instance has its own
    derivated class from DynamicModels.
    """

    _next_id = 0

    def __new__(cls, data=None, *args, **kwargs):
        new_class = type('DynamicModel_' + str(cls._next_id), (cls,), {})
        cls._next_id = id(new_class)
        return super(DynamicModel, new_class).__new__(new_class)

    def __setattr__(self, key, value):
        if key[0] != '_' and key not in self.__class__.__dict__.keys():
            if isinstance(value, bool):
                setattr(self.__class__, key, BooleanField(name=key))
            elif isinstance(value, int):
                setattr(self.__class__, key, IntegerField(name=key))
            elif isinstance(value, float):
                setattr(self.__class__, key, FloatField(name=key))
            elif isinstance(value, str):
                setattr(self.__class__, key, StringField(name=key))
            elif isinstance(value, datetime):
                setattr(self.__class__, key, DateTimeField(name=key))
            elif isinstance(value, (dict, DynamicModel)):
                setattr(self.__class__, key, ModelField(name=key, model_class=DynamicModel))
            elif isinstance(value, BaseModel):
                setattr(self.__class__, key, ModelField(name=key, model_class=value.__class__))
            elif isinstance(value, (list, ListModel)):
                setattr(self.__class__, key, ArrayField(name=key))
            else:
                raise TypeError("Invalid parameter: %s. Type not supported." % (key,))

        super(DynamicModel, self).__setattr__(key, value)

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if isinstance(data, dict):
            for key, value in data.items():
                setattr(self, key, value)
