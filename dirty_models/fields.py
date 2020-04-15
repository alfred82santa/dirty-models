"""
Fields to be used with dirty models.
"""

from collections import Mapping
from datetime import date, datetime, time, timedelta
from enum import Enum
from functools import wraps

from dateutil.parser import parse as dateutil_parse

from .base import AccessMode, Creating
from .model_types import ListModel

__all__ = ['IntegerField', 'FloatField', 'BooleanField', 'StringField', 'StringIdField',
           'TimeField', 'DateField', 'DateTimeField', 'TimedeltaField', 'ModelField', 'ArrayField',
           'HashMapField', 'BlobField', 'MultiTypeField', 'EnumField']


class BaseField:
    """Base field descriptor."""

    def __init__(self, name=None, alias=None, getter=None, setter=None, read_only=None,
                 default=None, title=None, doc=None, metadata=None, access_mode=AccessMode.READ_AND_WRITE,
                 json_schema=None):
        if read_only is not None:
            if read_only:
                access_mode = AccessMode.READ_ONLY & access_mode
            else:
                access_mode = AccessMode.READ_AND_WRITE & access_mode

        self._name = None
        self.name = name
        self.alias = alias
        self.access_mode = access_mode
        self.default = default
        self.title = title
        self.metadata = metadata
        self.json_schema = json_schema
        self._getter = getter
        self._setter = setter
        self.__doc__ = doc or self.get_field_docstring()

    def get_field_docstring(self):
        dcstr = '{0} field'.format(self.__class__.__name__)
        if self.access_mode:
            if self.access_mode == AccessMode.WRITABLE_ONLY_ON_CREATION:
                dcstr += ' [WRITABLE ONLY ON CREATION]'
            elif self.access_mode == AccessMode.READ_ONLY:
                dcstr += ' [READ ONLY]'
            elif self.access_mode == AccessMode.HIDDEN:
                dcstr += ' [HIDDEN]'
        return dcstr

    def export_definition(self):
        return {'name': self.name,
                'alias': self.alias,
                'access_mode': self.access_mode,
                'title': self.title,
                'default': self.default,
                'json_schema': self.json_schema,
                'metadata': self.metadata,
                'doc': self.__doc__}

    @property
    def name(self):
        """Name getter: Field name or field alias that it will be set."""
        return self._name

    @name.setter
    def name(self, name):
        """Name setter: Field name or field alias that it will be set."""
        self._name = name

    def use_value(self, value, creating=False):
        """Converts value to field type or use original"""
        if self.check_value(value):
            return value
        if creating:
            return self.convert_value_creating(value)
        return self.convert_value(value)

    def convert_value(self, value):
        """Converts value to field type"""
        return value

    def convert_value_creating(self, value):
        return self.convert_value(value)

    def check_value(self, value):
        """Checks whether value is field's type"""
        return False

    def can_use_value(self, value):
        """Checks whether value could be converted to field's type"""
        return True

    def set_value(self, obj, value):
        """Sets value to model"""
        obj.set_field_value(self.name, value)

    def get_value(self, obj):
        """Gets value from model"""
        return obj.get_field_value(self.name)

    def delete_value(self, obj):
        """Removes field value from model"""
        obj.delete_field_value(self.name)

    def _check_name(self):
        if self._name is None:
            raise AttributeError("Field name must be set")

    def __get__(self, obj, cls=None):
        if obj is None:
            return self

        self._check_name()

        if self._getter:
            return self._getter(self, obj, cls)

        return self.get_value(obj)

    def __set__(self, obj, value):
        self._check_name()

        if self._setter:
            self._setter(self, obj, value)
            return

        from dirty_models.utils import Factory

        def set_value(v):
            if value is None:
                self.delete_value(obj)
            elif self.check_value(v) or self.can_use_value(v):
                self.set_value(obj, self.use_value(v, creating=obj.is_creating()))
            elif isinstance(value, Factory):
                set_value(v())

        set_value(value)

    def __delete__(self, obj):
        self._check_name()
        self.delete_value(obj)


def can_use_enum(func):
    """
    Decorator to use Enum value on type checks.
    """

    @wraps(func)
    def inner(self, value):
        if isinstance(value, Enum):
            return self.check_value(value.value) or func(self, value.value)

        return func(self, value)

    return inner


def convert_enum(func):
    """
    Decorator to use Enum value on type casts.
    """

    @wraps(func)
    def inner(self, value):
        try:
            if self.check_value(value.value):
                return value.value
            return func(self, value.value)
        except AttributeError:
            pass

        return func(self, value)

    return inner


class IntegerField(BaseField):
    """
    It allows to use an integer as value in a field.

    **Automatic cast from:**

    * :class:`float`

    * :class:`str` if all characters are digits

    * :class:`~enum.Enum` if value of enum can be cast.

    """

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, str):
            return int(value, 0)
        return int(value)

    def check_value(self, value):
        return isinstance(value, int)

    @can_use_enum
    def can_use_value(self, value):
        if isinstance(value, float):
            return True
        elif isinstance(value, str):
            try:
                int(value, 0)
                return True
            except ValueError:
                pass
        return False


class FloatField(BaseField):
    """
    It allows to use a float as value in a field.

    **Automatic cast from:**

    * :class:`int`

    * :class:`str` if all characters are digits and there is only one dot (``.``).

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        return float(value)

    def check_value(self, value):
        return isinstance(value, float)

    @can_use_enum
    def can_use_value(self, value):
        try:
            float(value)
        except (ValueError, TypeError):
            return False
        else:
            return True


class BooleanField(BaseField):
    """
    It allows to use a boolean as value in a field.

    **Automatic cast from:**

    * :class:`int` ``0`` become ``False``, anything else ``True``

    * :class:`str` ``true`` and ``yes`` become ``True``, anything else ``False``. It is case-insensitive.

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, str):
            if value.lower().strip() in ['true', 'yes']:
                return True
            else:
                return False

        return bool(value)

    def check_value(self, value):
        return isinstance(value, bool)

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, str))


class StringField(BaseField):
    """
    It allows to use a string as value in a field.


    **Automatic cast from:**

    * :class:`int`

    * :class:`float`

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        return str(value)

    def check_value(self, value):
        return isinstance(value, str)

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, float))


class StringIdField(StringField):
    """
    It allows to use a string as value in a field, but not allows empty strings. Empty string are like ``None``
    and they will remove data of field.

    **Automatic cast from:**

    * :class:`int`

    * :class:`float`

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    def set_value(self, obj, value):
        """Sets value to model if not empty"""
        if value:
            obj.set_field_value(self.name, value)
        else:
            self.delete_value(obj)


class DateTimeBaseField(BaseField):
    """Base field for time or/and date fields."""

    date_parsers = {}

    def __init__(self, parse_format=None, **kwargs):
        """

        :param parse_format: String format to cast string to datetime. It could be
            an string format or a :class:`dict` with two keys:

                * ``parser`` key to set how string must be parsed. It could be a callable.
                * ``formatter`` key to set how datetime must be formatted. It could be a callable.

        :type parse_format: str or dict
        """
        super(DateTimeBaseField, self).__init__(**kwargs)
        self.parse_format = parse_format

    def export_definition(self):
        result = super(DateTimeBaseField, self).export_definition()
        result['parse_format'] = self.parse_format
        return result

    def get_parsed_value(self, value):
        """
        Helper to cast string to datetime using :member:`parse_format`.

        :param value: String representing a datetime
        :type value: str
        :return: datetime
        """

        def get_parser(parser_desc):
            try:
                return parser_desc['parser']
            except TypeError:
                try:
                    return get_parser(self.date_parsers[parser_desc])
                except KeyError:
                    return parser_desc
            except KeyError:
                pass

        parser = get_parser(self.parse_format)

        if parser is None:
            try:
                return dateutil_parse(value)
            except ValueError:
                return None

        if callable(parser):
            return parser(value)
        return datetime.strptime(value, parser)

    def get_formatted_value(self, value):
        """
        Returns a string from datetime using :member:`parse_format`.

        :param value: Datetime to cast to string
        :type value: datetime
        :return: str
        """

        def get_formatter(parser_desc):
            try:
                return parser_desc['formatter']
            except TypeError:
                if isinstance(parser_desc, str):
                    try:
                        return get_formatter(self.date_parsers[parser_desc])
                    except KeyError:
                        return parser_desc
                else:
                    pass
            except KeyError:
                try:
                    if isinstance(parser_desc['parser'], str):
                        return parser_desc['parser']
                except KeyError:
                    pass

        formatter = get_formatter(self.parse_format)

        if formatter is None:
            return str(value)

        if callable(formatter):
            return formatter(value)

        return value.strftime(format=formatter)


class TimeField(DateTimeBaseField):
    """
    It allows to use a time as value in a field.

    **Automatic cast from:**

    * :class:`list` items will be used to construct :class:`~datetime.time` object as arguments.

    * :class:`dict` items will be used to construct :class:`~datetime.time` object as keyword arguments.

    * :class:`str` will be parsed using a function or format in ``parser`` constructor parameter.

    * :class:`int` will be used as timestamp.

    * :class:`~datetime.datetime` will get time part.

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    def __init__(self, parse_format=None, default_timezone=None, **kwargs):
        """

        :param parse_format: String format to cast string to datetime. It could be
            an string format or a :class:`dict` with two keys:

                * ``parser`` key to set how string must be parsed. It could be a callable.
                * ``formatter`` key to set how datetime must be formatted. It could be a callable.

        :type parse_format: str or dict

        :param default_timezone: Default timezone to use when value does not have one.

        :type default_timezone: datetime.tzinfo
        """
        super(TimeField, self).__init__(parse_format=parse_format, **kwargs)
        self.default_timezone = default_timezone

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, list):
            return time(*value)
        elif isinstance(value, dict):
            return time(**value)
        elif isinstance(value, int):
            return self.convert_value(datetime.fromtimestamp(value, tz=self.default_timezone))
        elif isinstance(value, str):
            try:
                if not self.parse_format:
                    value = dateutil_parse(value)
                    return value.time()

                return self.convert_value(self.get_parsed_value(value))
            except Exception:
                return None
        elif isinstance(value, datetime):
            return value.timetz()

    def check_value(self, value):
        return isinstance(value, time)

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, str, datetime, list, dict))

    def set_value(self, obj, value: time):
        if self.default_timezone and value.tzinfo is None:
            value = value.replace(tzinfo=self.default_timezone)

        super(TimeField, self).set_value(obj, value)

    def export_definition(self):
        result = super(TimeField, self).export_definition()
        if self.default_timezone:
            result['default_timezone'] = self.default_timezone
        return result


class DateField(DateTimeBaseField):
    """
    It allows to use a date as value in a field.

    **Automatic cast from:**

    * :class:`list` items will be used to construct :class:`~datetime.date` object as arguments.

    * :class:`dict` items will be used to construct :class:`~datetime.date` object as keyword arguments.

    * :class:`str` will be parsed using a function or format in ``parser`` constructor parameter.

    * :class:`int` will be used as timestamp.

    * :class:`~datetime.datetime` will get date part.

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, list):
            return date(*value)
        elif isinstance(value, dict):
            return date(**value)
        elif isinstance(value, int):
            return self.convert_value(datetime.fromtimestamp(value))
        elif isinstance(value, str):
            try:
                if not self.parse_format:
                    value = dateutil_parse(value)
                    return value.date()

                return self.convert_value(self.get_parsed_value(value))
            except Exception:
                return None
        elif isinstance(value, datetime):
            return value.date()

    def check_value(self, value):
        return type(value) is date

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, str, datetime, list, dict))


class DateTimeField(DateTimeBaseField):
    """
    It allows to use a datetime as value in a field.

    **Automatic cast from:**

    * :class:`list` items will be used to construct :class:`~datetime.datetime` object as arguments.

    * :class:`dict` items will be used to construct :class:`~datetime.datetime` object as keyword arguments.

    * :class:`str` will be parsed using a function or format in ``parser`` constructor parameter.

    * :class:`int` will be used as timestamp.

    * :class:`~datetime.date` will set date part.

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    def __init__(self, parse_format=None, default_timezone=None, force_timezone=False, **kwargs):
        """

        :param parse_format: String format to cast string to datetime. It could be
            an string format or a :class:`dict` with two keys:

                * ``parser`` key to set how string must be parsed. It could be a callable.
                * ``formatter`` key to set how datetime must be formatted. It could be a callable.

        :type parse_format: str or dict

        :param default_timezone: Default timezone to use when value does not have one.

        :type default_timezone: datetime.tzinfo

        :param force_timezone: If it is True value will be converted to timezone defined on ``default_timezone``
                               parameter. It ``default_timezone`` is not defined it is ignored.

        :type: bool
        """
        super(DateTimeField, self).__init__(parse_format=parse_format, **kwargs)
        self.default_timezone = default_timezone
        self.force_timezone = force_timezone

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, list):
            return datetime(*value)
        elif isinstance(value, dict):
            return datetime(**value)
        elif isinstance(value, int):
            return datetime.fromtimestamp(value, tz=self.default_timezone)
        elif isinstance(value, str):
            try:
                if not self.parse_format:
                    return dateutil_parse(value)

                return self.get_parsed_value(value)
            except Exception:
                return None
        elif isinstance(value, date):
            return datetime(year=value.year, month=value.month,
                            day=value.day)

    def check_value(self, value):
        return type(value) is datetime

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, str, date, dict, list))

    def set_value(self, obj, value):
        if self.default_timezone:
            if value.tzinfo is None:
                value = value.replace(tzinfo=self.default_timezone)
            elif self.force_timezone and value.tzinfo != self.default_timezone:
                value = value.astimezone(tz=self.default_timezone)

        super(DateTimeField, self).set_value(obj, value)

    def export_definition(self):
        result = super(DateTimeField, self).export_definition()
        if self.default_timezone:
            result['default_timezone'] = self.default_timezone
            result['force_timezone'] = self.force_timezone
        return result


class TimedeltaField(BaseField):
    """
    It allows to use a timedelta as value in a field.

    **Automatic cast from:**

    * :class:`float` as seconds.

    * :class:`int` as seconds.

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, (int, float)):
            return timedelta(seconds=value)

    def check_value(self, value):
        return type(value) is timedelta

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, float))


class ModelField(BaseField):
    """
    It allows to use a model as value in a field. Model type must be
    defined on constructor using param model_class. If it is not defined
    self model will be used. It means model inside field will be the same
    class than model who define field.

    **Automatic cast from:**

    * :class:`dict`.

    * :class:`collections.Mapping`.
    """

    def __init__(self, model_class=None, **kwargs):
        self._model_class = model_class

        try:
            self._model_setter = kwargs.pop('setter')
        except KeyError:
            self._model_setter = None

        super(ModelField, self).__init__(**kwargs)

    def export_definition(self):
        result = super(ModelField, self).export_definition()
        result['model_class'] = self.model_class
        return result

    def get_field_docstring(self):
        dcstr = super(ModelField, self).get_field_docstring()
        if self.model_class:
            dcstr += ' (:class:`{0}`)'.format('.'.join([self.model_class.__module__, self.model_class.__name__]))
        return dcstr

    @property
    def model_class(self):
        """Model_class getter: model class used on field"""
        return self._model_class

    @model_class.setter
    def model_class(self, model_class):
        """Model_class setter: model class used on field"""

        self._model_class = model_class

    def convert_value(self, value):
        return self._model_class(value)

    def convert_value_creating(self, value):
        return self._model_class.create_new_model(value)

    def check_value(self, value):
        return isinstance(value, self._model_class)

    def can_use_value(self, value):
        return isinstance(value, (dict, Mapping))

    def __set__(self, obj, value):
        if self._model_setter:
            self._model_setter(self, obj, value)
            return
        if self._name is None:
            raise AttributeError("Field name must be set")

        original = self.get_value(obj)
        if original is None:
            super(ModelField, self).__set__(obj, value)
        elif self.check_value(value):
            original.clear()
            original.import_data(value.export_data())
        elif self.can_use_value(value):
            original.import_data(value)


class InnerFieldTypeMixin:

    def __init__(self, field_type=None, **kwargs):
        self._field_type = None
        if isinstance(field_type, tuple):
            field_type = field_type[0](**field_type[1])
        self.field_type = field_type if field_type else BaseField()
        super(InnerFieldTypeMixin, self).__init__(**kwargs)

    def export_definition(self):
        result = super(InnerFieldTypeMixin, self).export_definition()
        result['field_type'] = (self.field_type.__class__, self.field_type.export_definition())
        return result

    @property
    def field_type(self):
        """field_type getter: field type used on array or hashmap"""
        return self._field_type

    @field_type.setter
    def field_type(self, value):
        """Model_class setter: field type used on array or hashmap"""
        self._field_type = value


class ArrayField(InnerFieldTypeMixin, BaseField):
    """
    It allows to create a ListModel (iterable in :mod:`dirty_models.types`) of different elements according
    to the specified field_type. So it is possible to have a list of Integers, Strings, Models, etc.
    When using a model with no specified model_class the model inside field.

    **Automatic cast from:**

    * :class:`set`.

    * :class:`tuple`.
    """

    def __init__(self, autolist=False, **kwargs):
        self._autolist = autolist
        super(ArrayField, self).__init__(**kwargs)

    def get_field_docstring(self):
        if self.field_type:
            return 'Array of {0}'.format(self.field_type.get_field_docstring())

    def _convert_element(self, element):
        """
        Helper to convert a single item
        """
        if not self.field_type.check_value(element) and self._field_type.can_use_value(element):
            return self.field_type.convert_value(element)
        return element

    def convert_value(self, value):
        if isinstance(value, (set, list, tuple, ListModel)):
            return ListModel([self._convert_element(element) for element in value], field_type=self.field_type)
        elif self.autolist:
            return ListModel([self._convert_element(value)], field_type=self.field_type)

    def convert_value_creating(self, value):
        lst = ListModel(field_type=self.field_type)

        with Creating(lst):
            lst.extend(value)

        return lst

    def check_value(self, value):
        if not isinstance(value, ListModel) or not isinstance(value.get_field_type(), type(self.field_type)):
            return False
        return True

    def can_use_value(self, value):
        if isinstance(value, (set, list, tuple, ListModel)):
            if len(value) == 0:
                return True
            for item in value:
                if self.field_type.can_use_value(item) or self.field_type.check_value(item):
                    return True
            return False
        elif self.autolist and (self.field_type.check_value(value) or self.field_type.can_use_value(value)):
            return True
        else:
            return False

    @property
    def autolist(self):
        """
        autolist getter: autolist flag allows to convert a simple item on a list with
        one item.
        """
        return self._autolist

    @autolist.setter
    def autolist(self, value):
        """
        autolist setter: autolist flag allows to convert a simple item on a list with
        one item.
        """
        self._autolist = value


class HashMapField(InnerFieldTypeMixin, ModelField):
    """
    It allows to create a field which contains a hash map.

    **Automatic cast from:**

    * :class:`dict`.

    * :class:`BaseModel`.
    """

    def __init__(self, model_class=None, **kwargs):
        if model_class is None:
            from dirty_models.models import HashMapModel
            model_class = HashMapModel
        super(HashMapField, self).__init__(model_class=model_class,
                                           **kwargs)

    def convert_value(self, value):
        return self._model_class(data=value, field_type=self.field_type)


class BlobField(BaseField):
    """
    It allows any type of data.
    """
    pass


class MultiTypeField(BaseField):
    """
    It allows to define multiple type for a field. So, it is possible to define a field as
    a integer and as a model field, for example.
    """

    def __init__(self, field_types=None, **kwargs):
        self._field_types = []

        field_types = field_types or []

        for field_type in field_types:
            if isinstance(field_type, tuple):
                field_type = field_type[0](**field_type[1])
            self._field_types.append(field_type if field_type else BaseField())
        super(MultiTypeField, self).__init__(**kwargs)

    def get_field_docstring(self):
        if len(self._field_types):
            return 'Multiple type values are allowed:\n\n{0}'.format(
                "\n\n".join(["* {0}".format(field.get_field_docstring()) for field in self._field_types]))

    def export_definition(self):
        result = super(MultiTypeField, self).export_definition()
        result['field_types'] = [(field_type.__class__, field_type.export_definition())
                                 for field_type in self._field_types]
        return result

    def convert_value(self, value):
        for ft in self._field_types:
            if ft.can_use_value(value):
                return ft.convert_value(value)

    def check_value(self, value):
        for ft in self._field_types:
            if ft.check_value(value):
                return True
        return False

    def can_use_value(self, value):
        for ft in self._field_types:
            if ft.can_use_value(value):
                return True
        return False

    def get_field_type_by_value(self, value):
        for ft in self._field_types:
            if ft.check_value(value):
                return ft
        for ft in self._field_types:
            if ft.can_use_value(value):
                return ft

        raise TypeError("Value `{0}` can not be used on field `{1}`".format(value, self.name))

    @property
    def field_types(self):
        return self._field_types.copy()


class EnumField(BaseField):
    """
    It allows to create a field which contains a member of an enumeration.

    **Automatic cast from:**

    * Any value of enumeration.

    * Any member name of enumeration.
    """

    def __init__(self, enum_class, *args, **kwargs):
        """

        :param enum_class: Enumeration class
        :type enum_class: enum.Enum
        """
        self.enum_class = enum_class
        super(EnumField, self).__init__(*args, **kwargs)

    def export_definition(self):
        result = super(EnumField, self).export_definition()
        result['enum_class'] = self.enum_class

        return result

    def get_field_docstring(self):
        dcstr = super(EnumField, self).get_field_docstring()

        if self.enum_class:
            dcstr += ' (:class:`{0}`)'.format('.'.join([self.enum_class.__module__, self.enum_class.__name__]))
        return dcstr

    def convert_value(self, value):
        try:
            return self.enum_class(value)
        except ValueError:
            return getattr(self.enum_class, value)

    def check_value(self, value):
        return isinstance(value, self.enum_class)

    def can_use_value(self, value):
        try:
            self.enum_class(value)
            return True
        except ValueError:
            pass

        try:
            return value in self.enum_class.__members__.keys()
        except Exception:
            return False


class BytesField(BaseField):
    """
    It allows to use a bytes as value in a field.


    **Automatic cast from:**

    * :class:`str`

    * :class:`int`

    * :class:`bytearray`

    * :class:`list` of :class:`int` in range(0, 256)

    * :class:`~enum.Enum` if value of enum can be cast.
    """

    @convert_enum
    def convert_value(self, value):
        if isinstance(value, str):
            return value.encode()
        elif isinstance(value, (list, ListModel, bytearray, int)):
            if isinstance(value, int):
                value = bytes([value, ])
            elif isinstance(value, ListModel):
                value = value.export_data()
            try:
                return bytes(value)
            except TypeError:
                pass

        return None

    def check_value(self, value):
        return isinstance(value, bytes)

    @can_use_enum
    def can_use_value(self, value):
        return isinstance(value, (int, str, list, ListModel, bytearray))
