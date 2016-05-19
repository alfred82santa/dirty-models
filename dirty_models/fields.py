"""
fields.py

Fields to be used with dirty_models
"""
from datetime import datetime, date, time
from dateutil.parser import parse as dateutil_parse
from .model_types import ListModel
from collections import Mapping


class BaseField:

    """Base field descriptor."""

    def __init__(self, name=None, alias=None, getter=None, setter=None, read_only=False, default=None, doc=None):
        self._name = None
        self.name = name
        self.alias = alias
        self.read_only = read_only
        self.default = default
        self._getter = getter
        self._setter = setter
        self.__doc__ = doc or self.get_field_docstring()

    def get_field_docstring(self):
        dcstr = '{0} field'.format(self.__class__.__name__)
        if self.read_only:
            dcstr += ' [READ ONLY]'
        return dcstr

    def export_definition(self):
        return {'name': self.name,
                'alias': self.alias,
                'read_only': self.read_only,
                'doc': self.__doc__}

    @property
    def name(self):
        """Name getter: Field name or field alias that it will be set."""
        return self._name

    @name.setter
    def name(self, name):
        """Name setter: Field name or field alias that it will be set."""
        self._name = name

    def use_value(self, value):
        """Converts value to field type or use original"""
        if self.check_value(value):
            return value
        return self.convert_value(value)

    def convert_value(self, value):
        """Converts value to field type"""
        return value

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

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        if self._getter:
            return self._getter(self, obj, cls)
        if self._name is None:
            raise AttributeError("Field name must be set")
        return self.get_value(obj)

    def __set__(self, obj, value):
        if self._setter:
            self._setter(self, obj, value)
            return
        if self._name is None:
            raise AttributeError("Field name must be set")

        if self.check_value(value) or self.can_use_value(value):
            self.set_value(obj, self.use_value(value))

    def __delete__(self, obj):
        if self._name is None:
            raise AttributeError("Field name must be set")
        self.delete_value(obj)


class IntegerField(BaseField):

    """It allows to use an integer as value in a field."""

    def convert_value(self, value):
        return int(value)

    def check_value(self, value):
        return isinstance(value, int)

    def can_use_value(self, value):
        return isinstance(value, float) \
            or (isinstance(value, str) and value.isdigit())


class FloatField(BaseField):

    """It allows to use a float as value in a field."""

    def convert_value(self, value):
        return float(value)

    def check_value(self, value):
        return isinstance(value, float)

    def can_use_value(self, value):
        return isinstance(value, int) \
            or (isinstance(value, str)
                and value.replace('.', '', 1).isnumeric())


class BooleanField(BaseField):

    """It allows to use a boolean as value in a field."""

    def convert_value(self, value):
        if isinstance(value, str):
            if value.lower().strip() == 'true':
                return True
            else:
                return False

        return bool(value)

    def check_value(self, value):
        return isinstance(value, bool)

    def can_use_value(self, value):
        return isinstance(value, (int, str))


class StringField(BaseField):

    """It allows to use a string as value in a field."""

    def convert_value(self, value):
        return str(value)

    def check_value(self, value):
        return isinstance(value, str)

    def can_use_value(self, value):
        return isinstance(value, (int, float))


class StringIdField(StringField):

    """It allows to use a stringId as value in a field."""

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
        super(DateTimeBaseField, self).__init__(**kwargs)
        self._parse_format = None
        self.parse_format = parse_format

    def export_definition(self):
        result = super(DateTimeBaseField, self).export_definition()
        result['parse_format'] = self.parse_format
        return result

    @property
    def parse_format(self):
        """Model_class getter: model class used on field"""
        return self._parse_format

    @parse_format.setter
    def parse_format(self, value):
        """Parse_format setter: datetime format used on field"""
        self._parse_format = value

    def get_parsed_value(self, value):

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

    """It allows to use a time as value in a field."""

    def convert_value(self, value):
        if isinstance(value, list):
            return time(*value)
        elif isinstance(value, dict):
            return time(**value)
        elif isinstance(value, int):
            return self.convert_value(datetime.fromtimestamp(value))
        elif isinstance(value, str):
            try:
                if not self.parse_format:
                    value = dateutil_parse(value)
                    return value.time()

                return self.convert_value(self.get_parsed_value(value))
            except:
                return None
        elif isinstance(value, datetime):
            return value.timetz()

    def check_value(self, value):
        return isinstance(value, time)

    def can_use_value(self, value):
        return isinstance(value, (int, str, datetime, list, dict))


class DateField(DateTimeBaseField):

    """It allows to use a date as value in a field."""

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
            except:
                return None
        elif isinstance(value, datetime):
            return value.date()

    def check_value(self, value):
        return type(value) is date

    def can_use_value(self, value):
        return isinstance(value, (int, str, datetime, list, dict))


class DateTimeField(DateTimeBaseField):

    """It allows to use a datetime as value in a field."""

    def convert_value(self, value):
        if isinstance(value, list):
            return datetime(*value)
        elif isinstance(value, dict):
            return datetime(**value)
        elif isinstance(value, int):
            return datetime.fromtimestamp(value)
        elif isinstance(value, str):
            try:
                if not self.parse_format:
                    return dateutil_parse(value)

                return self.get_parsed_value(value)
            except:
                return None
        elif isinstance(value, date):
            return datetime(year=value.year, month=value.month,
                            day=value.day)

    def check_value(self, value):
        return type(value) is datetime

    def can_use_value(self, value):
        return isinstance(value, (int, str, date, dict, list))


class ModelField(BaseField):

    """
    It allows to use a model as value in a field. Model type must be
    defined on constructor using param model_class. If it is not defined
    self model will be used. It means model inside field will be the same
    class than model who define field.
    """

    def __init__(self, model_class=None, **kwargs):
        self._model_class = None
        self.model_class = model_class
        self._model_setter = None
        if 'setter' in kwargs:
            self._model_setter = kwargs['setter']
            del(kwargs['setter'])
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
    It allows to create a ListModel (iterable in dirty_models.types) of different elements according
    to the specified field_type. So it is possible to have a list of Integers, Strings, Models, etc.
    When using a model with no specified model_class the model inside field.
    """

    def __init__(self, autolist=False, **kwargs):
        self._autolist = autolist
        super(ArrayField, self).__init__(**kwargs)

    def get_field_docstring(self):
        if self.field_type:
            return 'Array of {0}'.format(self.field_type.get_field_docstring())

    def convert_value(self, value):
        def convert_element(element):
            """
            Helper to convert a single item
            """
            if not self.field_type.check_value(element) and self._field_type.can_use_value(element):
                return self.field_type.convert_value(element)
            return element

        if isinstance(value, (set, list, tuple, ListModel)):
            return ListModel([convert_element(element) for element in value], field_type=self.field_type)
        elif self.autolist:
            return ListModel([convert_element(value)], field_type=self.field_type)

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

    def __init__(self, model_class=None, **kwargs):
        if model_class is None:
            from dirty_models.models import HashMapModel
            model_class = HashMapModel
        super(HashMapField, self).__init__(model_class=model_class,
                                           **kwargs)

    def convert_value(self, value):
        return self._model_class(data=value, field_type=self.field_type)


class BlobField(BaseField):
    pass


class MultiTypeField(BaseField):

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
            return 'Multiple type values allowed:\n{0}'.format("\n".join(["* {0}".format(field.get_field_docstring())
                                                                          for field in self._field_types]))

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

    @property
    def field_types(self):
        return self._field_types.copy()
