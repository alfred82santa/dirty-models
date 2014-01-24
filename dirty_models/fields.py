class BaseField:
    def __init__(self, name=None):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def use_value(self, value):
        if self.check_value(value):
            return value
        return self.convert_value(value)
    
    def convert_value(self, value):
        return value

    def check_value(self, value):
        return True

    def can_use_value(self, value):
        return True

    def set_value(self, obj, value):
        obj.set_field_value(self.name, value)

    def get_value(self, obj):
        return obj.get_field_value(self.name)

    def delete_value(self, obj):
        obj.delete_field_value(self.name)

    def __get__(self, obj, cls):
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
        self.delete_value(obj)
        
        
class IntegerField(BaseField):
    def convert_value(self, value):
        return int(value)

    def check_value(self, value):
        return isinstance(value, int)

    def can_use_value(self, value):
        return isinstance(value, float) \
            or (isinstance(value, str) and value.isdigit())
            
            
class FloatField(BaseField):
    def convert_value(self, value):
        return float(value)

    def check_value(self, value):
        return isinstance(value, float)

    def can_use_value(self, value):
        return isinstance(value, int) \
            or (isinstance(value, str) and value.replace('.','',1).isnumeric())

            
class BooleanField(BaseField):
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
    def convert_value(self, value):
        return str(value)

    def check_value(self, value):
        return isinstance(value, str)

    def can_use_value(self, value):
        return isinstance(value, (int, float))
