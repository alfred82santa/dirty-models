"""
models.py

Base model for dirty_models.
"""

import itertools
from datetime import datetime

from collections import Mapping
from copy import deepcopy

from dirty_models.base import BaseData, InnerFieldTypeMixin
from dirty_models.fields import IntegerField, FloatField, BooleanField, StringField, DateTimeField
from dirty_models.model_types import ListModel
from .fields import BaseField, ModelField, ArrayField


class DirtyModelMeta(type):
    """
    Metaclass for dirty_models. It sets automatic fieldnames and
    automatic model_class for ModelField fields.
    """

    def __init__(cls, name, bases, classdict):
        super(DirtyModelMeta, cls).__init__(name, bases, classdict)

        fields = {key: field for key, field in cls.__dict__.items()}
        structure = {}
        read_only_fields = []
        for key, field in fields.items():
            if isinstance(field, BaseField):
                cls.process_base_field(field, key)
                structure[field.name] = field
                if field.read_only:
                    read_only_fields.append(field.name)

        cls._structure = structure
        default_data = {}
        for p in bases:
            try:
                default_data.update(deepcopy(p._default_data))
            except AttributeError:
                pass

        default_data.update(deepcopy(cls._default_data))
        default_data.update({f.name: f.default for f in structure.values() if f.default is not None})
        cls._default_data = default_data

    def process_base_field(cls, field, key):
        """
        Preprocess field instances.

        :param field: Field object
        :param key: Key where field was found
        """
        if not field.name:
            field.name = key
        elif key != field.name:
            setattr(cls, field.name, field)

        cls.prepare_field(field)

        if field.alias:
            for alias_name in field.alias:
                setattr(cls, alias_name, field)

    def prepare_field(cls, field):
        if isinstance(field, ModelField) and not field.model_class:
            field.model_class = cls
            field.__doc__ = field.get_field_docstring()

        try:
            cls.prepare_field(field.field_type)
            field.field_type.__doc__ = field.field_type.get_field_docstring()
        except AttributeError:
            pass

        try:
            for inner_field in field.field_types:
                cls.prepare_field(inner_field)
        except AttributeError:
            pass


def recover_model_from_data(model_class, original_data, modified_data, deleted_data):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class(original_data, True)
    model.unlock()
    model.import_data(modified_data)
    model.import_deleted_fields(deleted_data)
    model.lock()
    return model


class BaseModel(BaseData, metaclass=DirtyModelMeta):
    """
    Base model with dirty feature. It stores original data and saves
    modifications in other side.
    """
    _original_data = None
    _modified_data = None
    _deleted_fields = None

    _default_data = {}

    def __init__(self, data=None, flat=False, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self._original_data = {}
        self._modified_data = {}
        self._deleted_fields = []

        self.unlock()
        self.import_data(self._default_data)
        if isinstance(data, (dict, Mapping)):
            self.import_data(data)
        self.import_data(kwargs)
        if flat:
            self.flat_data()
        self.lock()

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """

        return recover_model_from_data, (self.__class__, self.export_original_data(),
                                         self.export_modified_data(), self.export_deleted_fields(),)

    def _get_real_name(self, name):
        obj = self.__class__.get_field_obj(name)
        try:
            return obj.name
        except AttributeError:
            return None

    def set_field_value(self, name, value):
        """
        Set the value to the field modified_data
        """
        name = self._get_real_name(name)

        if name and self._can_write_field(name):
            if name in self._deleted_fields:
                self._deleted_fields.remove(name)
            if self._original_data.get(name) == value:
                if self._modified_data.get(name):
                    self._modified_data.pop(name)
            else:
                self._modified_data[name] = value
                self._prepare_child(value)
                if name in self._structure and self._structure[name].read_only:
                    try:
                        value.set_read_only(True)
                    except AttributeError:
                        pass

    def get_field_value(self, name):
        """
        Get the field value from the modified data or the original one
        """
        name = self._get_real_name(name)

        if not name or name in self._deleted_fields:
            return None
        modified = self._modified_data.get(name)
        if modified is not None:
            return modified
        return self._original_data.get(name)

    def delete_field_value(self, name):
        """
        Mark this field to be deleted
        """
        name = self._get_real_name(name)

        if name and self._can_write_field(name):
            if name in self._modified_data:
                self._modified_data.pop(name)

            if name in self._original_data and name not in self._deleted_fields:
                self._deleted_fields.append(name)

    def reset_field_value(self, name):
        """
        Resets value of a field
        """
        name = self._get_real_name(name)

        if name and self._can_write_field(name):
            if name in self._modified_data:
                del self._modified_data[name]

            if name in self._deleted_fields:
                self._deleted_fields.remove(name)

            try:
                self._original_data[name].clear_modified_data()
            except (KeyError, AttributeError):
                pass

    def is_modified_field(self, name):
        """
        Returns whether a field is modified or not
        """
        name = self._get_real_name(name)

        if name in self._modified_data or name in self._deleted_fields:
            return True

        try:
            return self.get_field_value(name).is_modified()
        except:
            return False

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if not self.get_read_only() or not self.is_locked():
            if isinstance(data, BaseModel):
                data = data.export_data()
            if isinstance(data, (dict, Mapping)):
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

    def import_deleted_fields(self, data):
        """
        Set data fields to deleted
        """
        if not self.get_read_only() or not self.is_locked():
            if isinstance(data, str):
                data = [data]
            if isinstance(data, list):
                for key in data:
                    if hasattr(self, key):
                        delattr(self, key)
                    else:
                        keys = key.split('.', 1)
                        if len(keys) == 2:
                            child = getattr(self, keys[0])
                            child.import_deleted_fields(keys[1])

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
                    if value.is_modified():
                        result[key] = value.export_modified_data()
                except AttributeError:
                    pass

        return result

    def get_original_field_value(self, name):
        """
        Returns original field value or None
        """
        name = self._get_real_name(name)

        try:
            value = self._original_data[name]
        except KeyError:
            return None

        try:
            return value.export_original_data()
        except AttributeError:
            return value

    def export_original_data(self):
        """
        Get the original data
        """

        return {key: self.get_original_field_value(key) for key in self._original_data.keys()}

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

        for value in self._original_data.values():
            try:
                value.clear_modified_data()
            except AttributeError:
                pass

    def clear(self):
        """
        Clears all the data in the object, keeping original data
        """
        self._modified_data = {}
        self._deleted_fields = [field for field in self._original_data.keys()]

    def clear_all(self):
        """
        Clears all the data in the object
        """
        self._modified_data = {}
        self._original_data = {}
        self._deleted_fields = []

    def get_fields(self):
        """
        Returns used fields of model
        """
        result = [key for key in self._original_data.keys()
                  if key not in self._deleted_fields]
        result.extend([key for key in self._modified_data.keys()
                       if key not in result and key not in self._deleted_fields])

        return result

    def is_modified(self):
        """
        Returns whether model is modified or not
        """
        if len(self._modified_data) or len(self._deleted_fields):
            return True

        for value in self._original_data.values():
            try:
                if value.is_modified():
                    return True
            except AttributeError:
                pass

        return False

    def copy(self):
        """
        Creates a copy of model
        """
        return self.__class__(data=self.export_data())

    def __iter__(self):
        def iterfunc():
            for field in self.get_fields():
                yield (field, getattr(self, field))

        return iterfunc()

    def _can_write_field(self, name):
        return name not in self._structure or (not self._structure[name].read_only and not self.get_read_only()) or \
            not self.is_locked()

    def _update_read_only(self):
        for value in itertools.chain(self._original_data.values(), self._modified_data.values()):
            try:
                value.set_read_only(self.get_read_only())
            except AttributeError:
                pass

    def __str__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 ",".join(["'{0}': {1}".format(field, repr(self.get_field_value(field)))
                                           for field in sorted(self.get_fields())]))

    def __repr__(self):
        return str(self)

    @classmethod
    def get_field_obj(cls, name):
        return getattr(cls, name, None)

    def _get_fields_by_path(self, field):
        """
        Function to perform a function to the field specified. If the function has to be performed by the same object
        the field name is retrieved
        :param field: Field structure as following:
         field_1.*.subfield_2  would apply a the function to the every subfield_2 of the elements in field_1
         field_1.1.subfield_2  would apply a the function to the subfield_2 of the element 1 in field_1
        :field function: string containing the function in the class to be applied to the field
        """
        try:
            field, next_field = field.split('.', 1)
        except ValueError:
            next_field = ''

        if field == '*':
            return self.get_fields(), next_field
        else:
            return [field], next_field

    def delete_attr_by_path(self, field):
        """
        Function for deleting a field specifying the path in the whole model as described
        in :func:`dirty:models.models.BaseModel.perform_function_by_path`
        """
        fields, next_field = self._get_fields_by_path(field)
        for field in fields:
            if next_field:
                try:
                    self.get_field_value(field).delete_attr_by_path(next_field)
                except AttributeError:
                    pass
            else:
                self.delete_field_value(field)

    def reset_attr_by_path(self, field):
        """
        Function for restoring a field specifying the path in the whole model as described
        in :func:`dirty:models.models.BaseModel.perform_function_by_path`
        """
        fields, next_field = self._get_fields_by_path(field)
        for field in fields:
            if next_field:
                try:
                    self.get_field_value(field).reset_attr_by_path(next_field)
                except AttributeError:
                    pass
            else:
                self.reset_field_value(field)

    @classmethod
    def get_structure(cls):
        """
        Returns a dictionary with model field objects.
        :return: dict
        """
        return cls._structure.copy()


class BaseDynamicModel(BaseModel):
    """

    """
    _dynamic_model = None

    def __getattr__(self, name):
        try:
            return getattr(super(BaseDynamicModel, self), name)
        except AttributeError:
            return self.get_field_value(name)

    def _get_field_type(self, key, value):
        """
        Helper to create field object based on value type
        """
        if isinstance(value, bool):
            return BooleanField(name=key)
        elif isinstance(value, int):
            return IntegerField(name=key)
        elif isinstance(value, float):
            return FloatField(name=key)
        elif isinstance(value, str):
            return StringField(name=key)
        elif isinstance(value, datetime):
            return DateTimeField(name=key)
        elif isinstance(value, (dict, BaseDynamicModel, Mapping)):
            return ModelField(name=key, model_class=self._dynamic_model or self.__class__)
        elif isinstance(value, BaseModel):
            return ModelField(name=key, model_class=value.__class__)
        elif isinstance(value, (list, set, ListModel)):
            if not len(value):
                return None
            field_type = self._get_field_type(None, value[0])
            return ArrayField(name=key, field_type=field_type)
        elif value is None:
            return None
        else:
            raise TypeError("Invalid parameter: %s. Type not supported." % (key,))

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if isinstance(data, (dict, Mapping)):
            for key, value in data.items():
                setattr(self, key, value)


class DynamicModel(BaseDynamicModel):
    """
    DynamicModel allow to create model with no structure. Each instance has its own
    derivated class from DynamicModels.
    """

    _next_id = 0

    def __init__(self, *args, **kwargs):
        super(DynamicModel, self).__init__(*args, **kwargs)
        self._structure = {}

    def __new__(cls, *args, **kwargs):
        new_class = type('DynamicModel_' + str(cls._next_id), (cls,), {'_dynamic_model': DynamicModel})
        cls._next_id = id(new_class)
        return super(DynamicModel, new_class).__new__(new_class)

    def __setattr__(self, name, value):
        if not self.__hasattr__(name):
            if not self.get_read_only() or not self.is_locked():
                field_type = self._get_field_type(name, value)
                if not field_type:
                    return
                self._structure[field_type.name] = field_type
                setattr(self.__class__, name, field_type)

        super(DynamicModel, self).__setattr__(name, value)

    def __hasattr__(self, name):
        try:
            getattr(super(DynamicModel, self), name)
        except AttributeError:
            try:
                self.__dict__[name]
            except KeyError:
                try:
                    self.__class__.__dict__[name]
                except KeyError:
                    return False
        return True

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """
        return recover_model_from_data, (DynamicModel, self.export_original_data(),
                                         self.export_modified_data(), self.export_deleted_fields(),)


def recover_hashmap_model_from_data(model_class, original_data, modified_data, deleted_data, field_type):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class(original_data, True, field_type=field_type[0](**field_type[1]))
    model.unlock()
    model.import_data(modified_data)
    model.import_deleted_fields(deleted_data)
    model.lock()
    return model


class HashMapModel(InnerFieldTypeMixin, BaseModel):
    """
    Hash map model with dirty feature. It stores original data and saves
    modifications in other side.
    """

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """
        return recover_hashmap_model_from_data, (self.__class__, self.export_original_data(),
                                                 self.export_modified_data(), self.export_deleted_fields(),
                                                 (self.get_field_type().__class__,
                                                  self.get_field_type().export_definition()))

    def _get_real_name(self, name):
        new_name = super(HashMapModel, self)._get_real_name(name)
        if not new_name:
            return name
        return new_name

    def copy(self):
        """
        Creates a copy of model
        """
        return self.__class__(field_type=self.get_field_type(), data=self.export_data())

    def get_validated_object(self, value):
        """
        Returns the value validated by the field_type
        """
        try:
            if self.get_field_type().check_value(value) or self.get_field_type().can_use_value(value):
                data = self.get_field_type().use_value(value)
                self._prepare_child(data)
                return data
            else:
                return None
        except AttributeError:
            return value

    def __setattr__(self, name, value):
        if not self.__hasattr__(name) and (not self.get_read_only() or not self.is_locked()):
            if value is None:
                delattr(self, name)
                return
            validated_value = self.get_validated_object(value)

            if validated_value is not None and \
                    (name not in self._original_data or self._original_data[name] != validated_value):
                self.set_field_value(name, validated_value)
            return

        super(HashMapModel, self).__setattr__(name, value)

    def __hasattr__(self, name):
        try:
            getattr(super(HashMapModel, self), name)
        except AttributeError:
            try:
                self.__dict__[name]
            except KeyError:
                try:
                    self.__class__.__dict__[name]
                except KeyError:
                    return False

        return True

    def __getattr__(self, name):
        try:
            return getattr(super(HashMapModel, self), name)
        except AttributeError:
            return self.get_field_value(name)

    def __delattr__(self, name):
        if not self.__hasattr__(name) and (not self.get_read_only() or not self.is_locked()):
            self.delete_field_value(name)
            return
        super(HashMapModel, self).__delattr__(name)


class FastDynamicModel(BaseDynamicModel):
    """
    FastDynamicModel allow to create model with no structure.
    """

    _field_types = None

    def __init__(self, *args, **kwargs):
        self._field_types = {}
        self._dynamic_model = FastDynamicModel
        super(FastDynamicModel, self).__init__(*args, **kwargs)

    def _get_real_name(self, name):
        new_name = super(FastDynamicModel, self)._get_real_name(name)
        if not new_name:
            return name
        return new_name

    def get_validated_object(self, field_type, value):
        """
        Returns the value validated by the field_type
        """
        if field_type.check_value(value) or field_type.can_use_value(value):
            data = field_type.use_value(value)
            self._prepare_child(data)
            return data
        else:
            return None

    def get_current_structure(self):
        """
        Returns a dictionary with model field objects.
        :return: dict
        """

        struct = self.__class__.get_structure()
        struct.update(self._field_types)
        return struct

    def __setattr__(self, name, value):
        if self._field_types is not None and not self.__hasattr__(name) \
                and (not self.get_read_only() or not self.is_locked()):
            if value is None:
                delattr(self, name)
                return
            try:
                field_type = self._field_types[name]
            except KeyError:
                field_type = self._get_field_type(name, value)
                if not field_type:
                    return
                self._field_types[name] = field_type

            validated_value = self.get_validated_object(field_type, value)
            if validated_value is not None and \
                    (name not in self._original_data or self._original_data[name] != validated_value):
                self.set_field_value(name, validated_value)
            return

        super(FastDynamicModel, self).__setattr__(name, value)

    def __hasattr__(self, name):
        try:
            getattr(super(FastDynamicModel, self), name)
        except AttributeError:
            try:
                self.__dict__[name]
            except KeyError:
                try:
                    self.__class__.__dict__[name]
                except KeyError:
                    return False

        return True

    def __delattr__(self, name):
        if not self.__hasattr__(name) and (not self.get_read_only() or not self.is_locked()):
            self.delete_field_value(name)
            return
        super(FastDynamicModel, self).__delattr__(name)
