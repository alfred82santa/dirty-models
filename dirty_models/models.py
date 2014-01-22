from fields import BaseField

class BaseModel(metaclass=DirtyModelMeta):
    def __init__(self, data={}, **kwargs):
        self._original_data = {}
        self._data = {}
        self.import_data(data)
        self.import_data(kwargs)
        
    def set_field_value(self, name, value):
        try:
            if self._original_data[name] == value:
                try:
                  del self._data[name]  
                  
                except KeyError, e:
                    pass
                    
        except KeyError, e:
                pass
                
        self._data[name] = value
        
        
    def get_field_value(self, name):
        try:
            return self._data[name]
            
        except KeyError, e:
            return self._original_data[name]
         
         
    def delete_field_value(self, name):
        try:
            self._original_data[name]
            self.set_field_value(name, None)
            
        except KeyError, e:
            try:
                del self._data[name]
                
            except KeyError, e:
                pass
    
    
    def import_data(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
                
    def export_data(self):
        if not self._data:
            return self._original_data
        if not self._original_data:
            return self._data
            
        result = {}
        for key, value in self._original_data.items(): 
            try:
                result[key] = value.export_data()
            except AttributeError, e:
                result[key] = value
                
        for key, value in self._data.items(): 
            try:
                result[key] = value.export_data()
            except AttributeError, e:
                result[key] = value
                
        return result
        
        
    def export_modified_data(self):
        result = {}
        for key, value in self._original_data.items(): 
            try:
                result[key] = value.export_modified_data()
            except AttributeError, e:
                result[key] = value
                
        for key, value in self._data.items(): 
            try:
                result[key] = value.export_modified_data()
            except AttributeError, e:
                result[key] = value
                
        return result
        
        
    def flat_data(self):
        for key, value in self._data.items(): 
            self._original_data[key] = value
            
        for value in self._original_data.values(): 
            try:
                value.flat_data()
            except AttributeError, e:
                pass
                
                
class DirtyModelMeta(type):
    def __new__(cls, name, bases, classdict):
        result = type.__new__(cls, name, bases, classdict)
        for key, field in result.__dict__.items():
            if isinstance(field, BaseField):
                if not field.get_name():
                    field.set_field(key)
                elif key != field.get_name():
                    result.__dict__[field.get_name()] = field
        return result
            
