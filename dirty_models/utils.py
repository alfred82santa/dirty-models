import re
from json.encoder import JSONEncoder as BaseJSONEncoder
from datetime import date, datetime, time, timedelta
from .fields import MultiTypeField, DateTimeBaseField
from .model_types import ListModel
from .models import BaseModel, HashMapModel


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


class HashMapFormatterIter(BaseFieldtypeFormatterIter):

    def __iter__(self):
        for fieldname in self.obj.get_fields():
            value = self.obj.get_field_value(fieldname)
            yield fieldname, self.parent_formatter.format_field(self.field, value)


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
            yield field.name, self.format_field(field,
                                                self.model.get_field_value(fieldname))

    def format_field(self, field, value):
        if isinstance(field, MultiTypeField):
            return self.format_field(field.get_field_type_by_value(value), value)
        elif isinstance(value, HashMapModel):
            return HashMapFormatterIter(obj=value, field=value.get_field_type(), parent_formatter=self)
        elif isinstance(value, BaseModel):
            return self.__class__(value)
        elif isinstance(value, ListModel):
            return ListFormatterIter(obj=value, field=value.get_field_type(), parent_formatter=self)

        return value


class ModelFormatterIter(BaseModelFormatterIter):

    """
    Iterate over model fields formatting them.
    """

    def format_field(self, field, value):
        if isinstance(value, (date, datetime, time)) and \
                isinstance(field, DateTimeBaseField):
            return field.get_formatted_value(value)
        elif isinstance(value, timedelta):
            return value.total_seconds()

        return super(ModelFormatterIter, self).format_field(field, value)


class JSONEncoder(BaseJSONEncoder):

    """
    Json encoder for Dirty Models
    """

    def default(self, obj):
        if isinstance(obj, BaseModel):
            return {k: v for k, v in ModelFormatterIter(obj)}
        elif isinstance(obj, (HashMapFormatterIter, ModelFormatterIter)):
            return {k: v for k, v in obj}
        elif isinstance(obj, ListFormatterIter):
            return list(obj)
