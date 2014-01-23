class BaseField:
    def __init__(self, name=None):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def use_value(cls, value):
        return value

    def check_value(self, value):
        return True

    def can_use_value(self, value):
        return True

    def set_value(self, obj, value):
        obj.set_field_value(self._name, value)

    def get_value(self, obj):
        return obj.get_field_value(self._name)

    def delete_value(self, obj):
        obj.delete_field_value(self._name)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self._name is None:
            raise AttributeError("Field name must be set")
        return self.get_value(obj)

    def __set__(self, obj, value):
        if self._name is None:
            raise AttributeError("Field name must be set")

        if self.check_value(value):
            self.set_value(obj, value)

        if self.can_use_value(value):
            self.set_value(obj, self.use_value(value))
            
    def __delete__(self, obj):
        self.delete_value(obj)