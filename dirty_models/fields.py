"""
fields.py

Fields to be used with dirty_models
"""
from .types import ListModel


class BaseField:

    """Base field descriptor."""

    def __init__(self, name=None, doc=None):
        self._name = None
        self.name = name
        self.__doc__ = doc

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
        if self._name is None:
            raise AttributeError("Field name must be set")
        return self.get_value(obj)

    def __set__(self, obj, value):
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


class ModelField(BaseField):

    """It allows to use a model as value in a field. Model type must be
    defined on constructor using param model_class. If it is not defined
    self model will be used. It means model inside field will be the same
    class than model who define field."""

    def __init__(self, name=None, doc=None, model_class=None):
        super(ModelField, self).__init__(name, doc)
        self._model_class = None

        self.model_class = model_class

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
        return isinstance(value, dict)

    def __set__(self, obj, value):
        if self._name is None:
            raise AttributeError("Field name must be set")

        original = self.get_value(obj)
        if original is None:
            super(ModelField, self).__set__(obj, value)
        elif self.check_value(value):
            original.import_data(value.export_data())
        elif self.can_use_value(value):
            original.import_data(value)


class ArrayField(BaseField):

    def __init__(self, name=None, model_object=BaseField()):
        super(ArrayField, self).__init__(name)
        self._model_object = model_object

    def convert_value(self, value):
        def convert_element(element):
            if not self._model_object.check_value(element) and self._model_object.can_use_value(element):
                return self._model_object.convert_value(element)
            return element
        return ListModel([convert_element(element) for element in value], field_type=self._model_object)

    def check_value(self, value):
        if isinstance(value, ListModel) and (type(value.field_type) == type(self._model_object)):
            for v in value:
                if not self._model_object.check_value(v):
                    return False
        else:
            return False
        return True

    def can_use_value(self, value):
        if isinstance(value, (set, list, ListModel)):
            for v in value:
                if self._model_object.can_use_value(v) or self._model_object.check_value(v):
                    return True
            return False
        else:
            return False
