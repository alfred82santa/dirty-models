"""
Base models for dirty_models.
"""

from collections import Mapping
from copy import deepcopy
from datetime import date, datetime, time, timedelta
from enum import Enum

import itertools

from dirty_models.fields import DateField, EnumField, TimeField, TimedeltaField
from .base import AccessMode, BaseData, Creating, InnerFieldTypeMixin
from .fields import ArrayField, BaseField, BooleanField, DateTimeField, FloatField, IntegerField, ModelField, \
    StringField
from .model_types import ListModel

__all__ = ['BaseModel', 'DynamicModel', 'FastDynamicModel', 'HashMapModel']


class DirtyModelMeta(type):
    """
    Metaclass for dirty_models. It sets automatic fieldnames and
    automatic model_class for ModelField fields.
    """

    def __init__(cls, name, bases, classdict):
        super(DirtyModelMeta, cls).__init__(name, bases, classdict)

        fields = {key: field for key, field in cls.__dict__.items() if isinstance(field, BaseField)}

        structure = {}
        for key, field in fields.items():
            cls.process_base_field(field, key)
            structure[field.name] = field

        cls.__structure__ = structure
        default_data = {}
        for p in bases:
            try:
                default_data.update(deepcopy(p.get_default_data()))
            except AttributeError:
                pass

        default_data.update(cls.get_default_data())
        default_data.update({f.name: f.default for f in structure.values() if f.default is not None})

        cls.__structure__ = {}
        for p in bases:
            try:
                cls.__structure__.update(deepcopy(p.get_structure()))
            except AttributeError:
                pass

        cls.__structure__.update(structure)
        cls.check_structure()
        cls.__default_data__ = {k: v for k, v in default_data.items() if k in cls.__structure__.keys()}

        override_field_access_modes = {}
        for p in bases:
            try:
                override_field_access_modes.update(p.__override_field_access_modes__)
            except AttributeError:
                pass

        override_field_access_modes.update({cls.get_field_obj(k).name: v
                                            for k, v in cls.__override_field_access_modes__.items()})

        cls.__override_field_access_modes__ = override_field_access_modes

    def process_base_field(cls, field, key):
        """
        Preprocess field instances.

        :param field: Field object
        :param key: Key where field was found
        """
        if not field.name:
            field.name = key
        elif key != field.name:
            if not isinstance(field.alias, list):
                field.alias = [key]
            else:
                field.alias.insert(0, key)
            setattr(cls, field.name, field)

        cls.prepare_field(field)

        if field.alias:
            for alias_name in field.alias:
                if key is not alias_name:
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

    def check_structure(cls):
        names = set()
        fields = {key: field for key, field in cls.__dict__.items() if isinstance(field, BaseField)}
        try:
            name, field = fields.popitem()
        except KeyError:
            field = None

        while field:
            [fields.pop(n) for n, f in fields.copy().items() if f is field]

            alias = set(field.alias or [])
            alias.add(field.name)
            for n in alias:
                if n in names:
                    raise RuntimeError("Field '{0}' used twice on model '{1}'".format(n, cls.__name__))
                names.add(n)

            try:
                name, field = fields.popitem()
            except KeyError:
                field = None


class CamelCaseMeta(DirtyModelMeta):
    """
    Metaclass for dirty_models. Sets camel case version of field's name as default field name.
    """

    def process_base_field(self, field, key):
        from .utils import underscore_to_camel

        if not field.name:
            field.name = underscore_to_camel(key)
        super(CamelCaseMeta, self).process_base_field(field, key)


def set_model_internal_data(model, original_data, modified_data, deleted_data):
    """
    Set internal data to model.
    """
    model.__original_data__ = original_data
    list(map(model._prepare_child, model.__original_data__))

    model.__modified_data__ = modified_data
    list(map(model._prepare_child, model.__modified_data__))

    model.__deleted_fields__ = deleted_data

    return model


def recover_model_from_data(model_class, original_data, modified_data, deleted_data):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class()
    return set_model_internal_data(model, original_data, modified_data, deleted_data)


class BaseModel(BaseData, metaclass=DirtyModelMeta):
    """
    Base model with dirty feature. It stores original data and saves
    modifications in other side.
    """

    __default_data__ = {}
    __override_field_access_modes__ = {}

    def __init__(self, data=None, flat=False, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        BaseModel.__setattr__(self, '__original_data__', {})
        BaseModel.__setattr__(self, '__modified_data__', {})
        BaseModel.__setattr__(self, '__deleted_fields__', [])

        from .base import Unlocker
        with Unlocker(self):
            self.import_data(self.__default_data__)
            if isinstance(data, (dict, Mapping)):
                self.import_data(data)
            self.import_data(kwargs)

        if flat:
            self.flat_data()

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """

        return recover_model_from_data, (self.__class__, self.__original_data__,
                                         self.__modified_data__, self.__deleted_fields__,)

    def get_real_name(self, name):
        obj = self.get_field_obj(name)
        try:
            return obj.name
        except AttributeError:
            return None

    def set_field_value(self, name, value):
        """
        Set the value to the field modified_data
        """
        name = self.get_real_name(name)

        if not name or not self._can_write_field(name):
            return

        if name in self.__deleted_fields__:
            self.__deleted_fields__.remove(name)
        if self.__original_data__.get(name) == value:
            try:
                self.__modified_data__.pop(name)
            except KeyError:
                pass
        else:
            self.__modified_data__[name] = value
            self._prepare_child(value)

            if name not in self.__structure__:
                return

            try:
                value.set_access_mode(self.__structure__[name].access_mode & self.get_access_mode())
            except AttributeError:
                pass

    def get_field_value(self, name):
        """
        Get the field value from the modified data or the original one
        """
        name = self.get_real_name(name)

        if not name or name in self.__deleted_fields__:
            return None
        modified = self.__modified_data__.get(name)
        if modified is not None:
            return modified
        return self.__original_data__.get(name)

    def delete_field_value(self, name):
        """
        Mark this field to be deleted
        """
        name = self.get_real_name(name)

        if name and self._can_write_field(name):
            if name in self.__modified_data__:
                self.__modified_data__.pop(name)

            if name in self.__original_data__ and name not in self.__deleted_fields__:
                self.__deleted_fields__.append(name)

    def reset_field_value(self, name):
        """
        Resets value of a field
        """
        name = self.get_real_name(name)

        if name and self._can_write_field(name):
            if name in self.__modified_data__:
                del self.__modified_data__[name]

            if name in self.__deleted_fields__:
                self.__deleted_fields__.remove(name)

            try:
                self.__original_data__[name].clear_modified_data()
            except (KeyError, AttributeError):
                pass

    def is_modified_field(self, name):
        """
        Returns whether a field is modified or not
        """
        name = self.get_real_name(name)

        if name in self.__modified_data__ or name in self.__deleted_fields__:
            return True

        try:
            return self.get_field_value(name).is_modified()
        except Exception:
            return False

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if self.get_access_mode() != AccessMode.READ_AND_WRITE:
            return

        if isinstance(data, BaseModel):
            data = data.export_data()

        if not isinstance(data, (dict, Mapping)):
            raise TypeError('Impossible to import data')

        self._import_data(data)

    def _import_data(self, data):
        for key, value in data.items():
            if not self.get_field_obj(key):
                self._not_allowed_field(key)
                continue
            setattr(self, key, value)

    def _not_allowed_field(self, name):
        pass

    def _not_allowed_value(self, name, value):
        pass

    def _not_allowed_modify(self, name):
        pass

    def import_deleted_fields(self, data):
        """
        Set data fields to deleted
        """

        if self.get_access_mode() != AccessMode.READ_AND_WRITE:
            return

        if isinstance(data, str):
            data = [data]

        for key in data:
            if hasattr(self, key):
                delattr(self, key)
                continue

            keys = key.split('.', 1)

            if len(keys) != 2:
                continue

            child = getattr(self, keys[0])
            child.import_deleted_fields(keys[1])

    def export_data(self):
        """
        Get the results with the modified_data
        """
        result = {}
        data = self.__original_data__.copy()
        data.update(self.__modified_data__)
        for key, value in data.items():
            if key in self.__deleted_fields__:
                continue

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
        result = {key: None for key in self.__deleted_fields__}

        for key, value in self.__modified_data__.items():
            if key in result.keys():
                continue
            try:
                result[key] = value.export_modified_data()
            except AttributeError:
                result[key] = value

        for key, value in self.__original_data__.items():
            if key in result.keys():
                continue
            try:
                if value.is_modified():
                    result[key] = value.export_modified_data()
            except AttributeError:
                pass

        return result

    def export_modifications(self):
        """
        Returns model modifications.
        """

        result = {}

        for key, value in self.__modified_data__.items():
            try:
                result[key] = value.export_data()
            except AttributeError:
                result[key] = value

        for key, value in self.__original_data__.items():
            if key in result.keys() or key in self.__deleted_fields__:
                continue
            try:
                if not value.is_modified():
                    continue
                modifications = value.export_modifications()
            except AttributeError:
                continue

            try:
                result.update({'{}.{}'.format(key, f): v for f, v in modifications.items()})
            except AttributeError:
                result[key] = modifications

        return result

    def get_original_field_value(self, name):
        """
        Returns original field value or None
        """
        name = self.get_real_name(name)

        try:
            value = self.__original_data__[name]
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

        return {key: self.get_original_field_value(key) for key in self.__original_data__.keys()}

    def export_deleted_fields(self):
        """
        Resturns a list with any deleted fields form original data.
        In tree models, deleted fields on children will be appended.
        """
        result = self.__deleted_fields__.copy()

        for key, value in self.__original_data__.items():
            if key in result:
                continue
            try:
                partial = value.export_deleted_fields()
                result.extend(['.'.join([key, key2]) for key2 in partial])
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

        modified_dict = self.__original_data__
        modified_dict.update(self.__modified_data__)
        self.__original_data__ = {k: flat_field(v)
                                  for k, v in modified_dict.items()
                                  if k not in self.__deleted_fields__}

        self.clear_modified_data()

    def clear_modified_data(self):
        """
        Clears only the modified data
        """
        self.__modified_data__ = {}
        self.__deleted_fields__ = []

        for value in self.__original_data__.values():
            try:
                value.clear_modified_data()
            except AttributeError:
                pass

    def clear(self):
        """
        Clears all the data in the object, keeping original data
        """
        self.__modified_data__ = {}
        self.__deleted_fields__ = [field for field in self.__original_data__.keys()]

    def clear_all(self):
        """
        Clears all the data in the object
        """
        self.__modified_data__ = {}
        self.__original_data__ = {}
        self.__deleted_fields__ = []

    def get_fields(self):
        """
        Returns used fields of model
        """
        result = [key for key in self.__original_data__.keys()
                  if key not in self.__deleted_fields__]
        result.extend([key for key in self.__modified_data__.keys()
                       if key not in result and key not in self.__deleted_fields__])

        return result

    def is_modified(self):
        """
        Returns whether model is modified or not
        """
        if len(self.__modified_data__) or len(self.__deleted_fields__):
            return True

        for value in self.__original_data__.values():
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

    def _get_field_access_mode(self, name):
        if name not in self.__structure__:
            return AccessMode.READ_AND_WRITE
        try:
            fam = self.__override_field_access_modes__[name]
        except KeyError:
            fam = self.__structure__[name].access_mode

        if fam == AccessMode.READ_AND_WRITE \
                or (fam == AccessMode.WRITABLE_ONLY_ON_CREATION
                    and self.is_creating()) \
                or not self.is_locked():
            return AccessMode.READ_AND_WRITE
        return fam

    def _can_write_field(self, name):
        if (self._get_field_access_mode(name) & self.get_access_mode()) == AccessMode.READ_AND_WRITE:
            return True
        else:
            self._not_allowed_modify(name)
            return False

    def _update_access_mode(self):
        for name, value in itertools.chain(self.__original_data__.items(), self.__modified_data__.items()):
            try:
                value.set_access_mode(self._get_field_access_mode(name) & self.get_access_mode())
            except AttributeError:
                pass

    def __str__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 ",".join(["'{0}': {1}".format(field, repr(self.get_field_value(field)))
                                           for field in sorted(self.get_fields())]))

    def __repr__(self):
        return str(self)

    def __contains__(self, item):
        return item in self.__modified_data__ or (item in self.__original_data__ and
                                                  item not in self.__deleted_fields__)

    @classmethod
    def get_field_obj(cls, name):
        obj_field = getattr(cls, name, None)
        return obj_field if isinstance(obj_field, BaseField) else None

    def _get_fields_by_path(self, field):

        try:
            field, next_field = field.split('.', 1)
        except ValueError:
            next_field = ''

        if field == '*':
            return self.get_fields(), next_field
        else:
            return [field], next_field

    def get_attrs_by_path(self, field_path, stop_first=False):
        """
        It returns list of values looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: list or None.
        :param stop_first: Stop iteration on first value looked up. Default: False.
        :type stop_first: bool
        :return: A list of values or None it was a invalid path.
        :rtype: :class:`list` or :class:`None`
        """
        fields, next_field = self._get_fields_by_path(field_path)
        values = []
        for field in fields:
            if next_field:
                try:
                    res = self.get_field_value(field).get_attrs_by_path(next_field, stop_first=stop_first)
                    if res is None:
                        continue
                    values.extend(res)

                    if stop_first and len(values):
                        break

                except AttributeError:
                    pass
            else:
                value = self.get_field_value(field)
                if value is None:
                    continue
                if stop_first:
                    return [value, ]
                values.append(value)

        return values if len(values) else None

    def get_1st_attr_by_path(self, field_path, **kwargs):
        """
        It returns first value looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: str
        :param default: Default value if field does not exist.
                        If it is not defined :class:`AttributeError` exception will be raised.
        :return: value
        """

        res = self.get_attrs_by_path(field_path, stop_first=True)
        if res is None:
            try:
                return kwargs['default']
            except KeyError:
                raise AttributeError("Field '{0}' does not exist".format(field_path))
        return res.pop()

    def delete_attr_by_path(self, field_path):
        """
        It deletes fields looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: str
        """
        fields, next_field = self._get_fields_by_path(field_path)
        for field in fields:
            if next_field:
                try:
                    self.get_field_value(field).delete_attr_by_path(next_field)
                except AttributeError:
                    pass
            else:
                self.delete_field_value(field)

    def reset_attr_by_path(self, field_path):
        """
        It restores original values for fields looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: str
        """
        fields, next_field = self._get_fields_by_path(field_path)
        for field in fields:
            if next_field:
                try:
                    self.get_field_value(field).reset_attr_by_path(next_field)
                except AttributeError:
                    pass
            else:
                self.reset_field_value(field)

    def __getitem__(self, key):
        try:
            return self.get_1st_attr_by_path(key)
        except AttributeError as ex:
            raise KeyError(str(ex))

    @classmethod
    def get_structure(cls):
        """
        Returns a dictionary with model field objects.

        :return: dict
        """
        return cls.__structure__.copy()

    @classmethod
    def get_default_data(cls):
        """
        Returns a dictionary with default data.

        :return: dict
        """
        return deepcopy(cls.__default_data__)

    def __len__(self):
        return len(self.export_data())

    @classmethod
    def create_new_model(cls, data):
        with Creating(cls()) as model:
            model.import_data(data)

        return model


class BaseDynamicModel(BaseModel):
    """

    """
    __dynamic_model__ = None

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
        elif isinstance(value, time):
            return TimeField(name=key)
        elif isinstance(value, datetime):
            return DateTimeField(name=key)
        elif isinstance(value, date):
            return DateField(name=key)
        elif isinstance(value, timedelta):
            return TimedeltaField(name=key)
        elif isinstance(value, Enum):
            return EnumField(name=key, enum_class=type(value))
        elif isinstance(value, (dict, BaseDynamicModel, Mapping)):
            return ModelField(name=key, model_class=self.__dynamic_model__ or self.__class__)
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

    def _import_data(self, data):
        """
        Set the fields established in data to the instance
        """

        for key, value in data.items():
            if key.startswith('__'):
                self._not_allowed_field(key)
                continue

            if not self.get_field_obj(key) and not self._define_new_field_by_value(key, value):
                self._not_allowed_value(key, value)
                continue

            setattr(self, key, value)


def recover_dynamic_model_from_data(model_class, original_data, modified_data, deleted_data, structure):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class()

    model.__structure__ = {k: d[0](**d[1]) for k, d in structure.items()}

    return set_model_internal_data(model, original_data, modified_data, deleted_data)


class DynamicModel(BaseDynamicModel):
    """
    DynamicModel allow to create model with no structure. Each instance has its own
    derivated class from DynamicModels.
    """

    _next_id = 0

    def __init__(self, *args, **kwargs):
        super(DynamicModel, self).__init__(*args, **kwargs)
        self.__structure__ = {}

    def __new__(cls, *args, **kwargs):
        new_class = type('DynamicModel_' + str(cls._next_id), (cls,), {'__dynamic_model__': DynamicModel})
        cls._next_id = id(new_class)
        return super(DynamicModel, new_class).__new__(new_class)

    def _define_new_field_by_value(self, name, value):
        field_type = self._get_field_type(name, value)

        if not field_type:
            return False
        self.__structure__[field_type.name] = field_type
        setattr(self.__class__, name, field_type)
        return True

    def __setattr__(self, name, value):
        if not self.__hasattr__(name):
            if not self.get_access_mode() or not self.is_locked():
                if not self._define_new_field_by_value(name, value):
                    self._not_allowed_value(name, value)
                    return

        super(DynamicModel, self).__setattr__(name, value)

    # def get_field_obj(self, name):
    #    return self.__structure__[name]

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
        return recover_dynamic_model_from_data, (DynamicModel, self.__original_data__,
                                                 self.__modified_data__, self.__deleted_fields__,
                                                 {field.name: (field.__class__, field.export_definition())
                                                  for field in self.__structure__.values()})


def recover_hashmap_model_from_data(model_class, original_data, modified_data, deleted_data, field_type):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class(field_type=field_type[0](**field_type[1]))
    return set_model_internal_data(model, original_data, modified_data, deleted_data)


class HashMapModel(InnerFieldTypeMixin, BaseModel):
    """
    Hash map model with dirty feature. It stores original data and saves
    modifications in other side.
    """

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """
        return recover_hashmap_model_from_data, (self.__class__, self.__original_data__,
                                                 self.__modified_data__, self.__deleted_fields__,
                                                 (self.get_field_type().__class__,
                                                  self.get_field_type().export_definition()))

    def get_real_name(self, name):
        new_name = super(HashMapModel, self).get_real_name(name)
        return new_name if new_name else name

    def get_field_obj(self, name):
        return super(HashMapModel, self).get_field_obj(name) or self.__field_type__

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

    def _import_data(self, data):
        """
        Set the fields in data to the hashmap instance.
        """

        for key, value in data.items():
            if key.startswith('__'):
                self._not_allowed_field(key)
                continue
            setattr(self, key, value)

    def __setattr__(self, name, value):
        if not self.__hasattr__(name) and (not self.get_access_mode() or not self.is_locked()):
            if value is None:
                delattr(self, name)
                return
            validated_value = self.get_validated_object(value)

            if validated_value is not None and \
                    (name not in self.__original_data__ or self.__original_data__[name] != validated_value):
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
        if not self.__hasattr__(name) and (not self.get_access_mode() or not self.is_locked()):
            self.delete_field_value(name)
            return
        super(HashMapModel, self).__delattr__(name)


def recover_fast_dynamic_model_from_data(model_class, original_data, modified_data, deleted_data, field_types):
    """
    Function to reconstruct a model from DirtyModel basic information: original data, the modified and deleted
    fields.
    Necessary for pickle an object
    """
    model = model_class()

    model.__field_types__ = {k: d[0](**d[1]) for k, d in field_types.items()}

    return set_model_internal_data(model, original_data, modified_data, deleted_data)


class FastDynamicModel(BaseDynamicModel):
    """
    FastDynamicModel allow to create model with no structure.
    """

    __field_types__ = None

    def __init__(self, *args, **kwargs):
        self.__field_types__ = {}
        self.__dynamic_model__ = FastDynamicModel
        super(FastDynamicModel, self).__init__(*args, **kwargs)

    def get_real_name(self, name):
        return super(FastDynamicModel, self).get_real_name(name) or name

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
        struct.update(self.__field_types__)
        return struct

    def _define_new_field_by_value(self, name, value):
        field_type = self._get_field_type(name, value)

        if not field_type:
            return False
        self.__field_types__[name] = field_type
        return True

    def __setattr__(self, name, value):
        if self.__field_types__ is not None and not self.__hasattr__(name) \
                and (not self.get_access_mode() or not self.is_locked()):
            if value is None:
                delattr(self, name)
                return
            try:
                field_type = self.__field_types__[name]
            except KeyError:
                if not self._define_new_field_by_value(name, value):
                    self._not_allowed_value(name, value)
                    return
                field_type = self.__field_types__[name]

            validated_value = self.get_validated_object(field_type, value)
            if validated_value is not None and \
                    (name not in self.__original_data__ or self.__original_data__[name] != validated_value):
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
        if not self.__hasattr__(name) and (not self.get_access_mode() or not self.is_locked()):
            self.delete_field_value(name)
            return
        super(FastDynamicModel, self).__delattr__(name)

    def get_field_obj(self, name):
        try:
            return self.__field_types__[name]
        except KeyError:
            return super(FastDynamicModel, self).get_field_obj(name)

    def __reduce__(self):
        """
        Reduce function to allow dumpable by pickle
        """
        return recover_fast_dynamic_model_from_data, (self.__class__, self.__original_data__,
                                                      self.__modified_data__, self.__deleted_fields__,
                                                      {field.name: (field.__class__, field.export_definition())
                                                       for field in self.__field_types__.values()})
