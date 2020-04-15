import re
from abc import abstractmethod
from datetime import date, datetime, time, timedelta
from enum import Enum
from json.encoder import JSONEncoder as BaseJSONEncoder

from .base import AccessMode
from .fields import MultiTypeField
from .model_types import ListModel
from .models import BaseModel

__all__ = ['underscore_to_camel',
           'BaseModelIterator',
           'ModelIterator',
           'ListFormatterIter',
           'BaseModelFormatterIter',
           'ModelFormatterIter',
           'JSONEncoder',
           'Factory',
           'factory']


def underscore_to_camel(string):
    """
    Converts underscored string to camel case.
    """
    return re.sub('_([a-z])', lambda x: x.group(1).upper(), string)


class BaseModelIterator:

    def __init__(self, model):
        self.model = model

    def __iter__(self):
        fields = self.model.get_fields()
        for fieldname in fields:
            field = self.model.get_field_obj(fieldname)
            name = self.model.get_real_name(fieldname)
            yield name, field, self.model.get_field_value(fieldname)


class ModelIterator(BaseModelIterator):
    """
    Helper in order to iterate over model fields.
    """

    def __iter__(self):
        for name, field, value in super(ModelIterator, self).__iter__():
            yield name, value

    items = __iter__

    def values(self):
        for _, value in self:
            yield value

    def keys(self):
        for name, _ in self:
            yield name


class BaseFormatterIter:

    @abstractmethod
    def format(self):  # pragma: no cover
        pass


class BaseFieldtypeFormatterIter(BaseFormatterIter):

    def __init__(self, obj, field, parent_formatter):
        self.obj = obj
        self.field = field
        self.parent_formatter = parent_formatter


class ListFormatterIter(BaseFieldtypeFormatterIter):

    def __iter__(self):
        for item in self.obj:
            yield self.parent_formatter.format_field(self.field, item)

    def format(self):
        return list(self)


class BaseModelFormatterIter(BaseModelIterator, BaseFormatterIter):
    """
    Base formatter iterator for Dirty Models.
    """

    def __iter__(self):
        for name, field, value in super(BaseModelFormatterIter, self).__iter__():
            if field.access_mode == AccessMode.HIDDEN:
                continue

            yield name, self.format_field(field,
                                          self.model.get_field_value(name))

    def format_field(self, field, value):
        if isinstance(field, MultiTypeField):
            return self.format_field(field.get_field_type_by_value(value), value)
        elif isinstance(value, BaseModel):
            return self.__class__(value)
        elif isinstance(value, ListModel):
            return ListFormatterIter(obj=value, field=value.get_field_type(), parent_formatter=self)
        elif isinstance(value, Enum):
            return self.format_field(field, value.value)

        return value

    def format(self):
        return {k: v.format() if isinstance(v, BaseFormatterIter) else v for k, v in self}


class ModelFormatterIter(BaseModelFormatterIter):
    """
    Iterate over model fields formatting them.
    """

    def format_field(self, field, value):
        if isinstance(value, (date, datetime, time)) and not isinstance(field, MultiTypeField):
            try:
                return field.get_formatted_value(value)
            except AttributeError:
                return str(value)
        elif isinstance(value, timedelta):
            return value.total_seconds()

        return super(ModelFormatterIter, self).format_field(field, value)


class JSONEncoder(BaseJSONEncoder):
    """
    Json encoder for Dirty Models
    """

    default_model_iter = ModelFormatterIter

    def default(self, obj):
        if isinstance(obj, BaseModel):
            return self.default(self.default_model_iter(obj))
        elif isinstance(obj, BaseFormatterIter):
            return obj.format()
        else:
            return super(JSONEncoder, self).default(obj)


class Factory:
    """
    Factory decorator could be used to define result of a function as default value. It could
    be useful to define a :class:`~dirty_models.fields.DateTimeField` with :meth:`datetime.datetime.now`
    in order to set the current datetime.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self):
        return self.func()


factory = Factory
