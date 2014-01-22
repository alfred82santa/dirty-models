# fields.py

class BaseField:
    def __init__ (self, name=None):
        self.name = name
        
    def set_name(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def use_value(cls, value):
        return data
        
    def check_value(self, value):
        return False
        
    def can_use_value(self, value):
        return False

    def set_value(self, obj, value):
        obj.set_field_value(self.name, value)

    def get_value(self, obj):
        return obj.get_field_value(self.name)
        
    def delete_value(self, obj):
        obj.delete_field_value(self.name)

    def __get__(self, obj):
        if obj is None:
            return self
        if self.name is None:
            raise AttributeError("Field name must be set")
        return self.get_value(obj)
        
    def __set__(self, obj, value):
        if self.name is None:
            raise AttributeError("Field name must be set")
            
        if self.check_data(value):
            self.set_value(value)
            
        if self.can_use_value(value):
            self.set_value(self.use_value(value))
            
    def __delete__(self, obj):
        obj.delete_value(obj)
        
