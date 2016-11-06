from datetime import date, datetime, time, timedelta
from enum import Enum
from json.encoder import JSONEncoder as BaseJSONEncoder

import re

from .fields import MultiTypeField
from .model_types import ListModel
from .models import BaseModel


def underscore_to_camel(string):
    """
    Converts underscored string to camel case.
    """
    return re.sub('_([a-z])', lambda x: x.group(1).upper(), string)


class BaseFormatterIter:
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


class BaseModelFormatterIter(BaseFormatterIter):
    """
    Base formatter iterator for Dirty Models.
    """

    def __init__(self, model):
        self.model = model

    def __iter__(self):
        fields = self.model.get_fields()
        for fieldname in fields:
            field = self.model.get_field_obj(fieldname)
            name = self.model.get_real_name(fieldname)
            yield name, self.format_field(field,
                                          self.model.get_field_value(fieldname))

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
            return {k: v for k, v in self.default_model_iter(obj)}
        elif isinstance(obj, (BaseModelFormatterIter)):
            return {k: v for k, v in obj}
        elif isinstance(obj, ListFormatterIter):
            return list(obj)
