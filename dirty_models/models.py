from .fields import BaseField, ModelField


class DirtyModelMeta(type):

    def __new__(cls, name, bases, classdict):
        result = super(DirtyModelMeta, cls).__new__(
            cls, name, bases, classdict)

        fields = {key: field for key, field in result.__dict__.items()}

        for key, field in fields.items():
            if isinstance(field, BaseField):
                if not field.name:
                    field.name = key
                elif key != field.name:
                    setattr(result, field.name, field)
                if isinstance(field, ModelField) and not field.model_class:
                    field.model_class = result
        return result


class BaseModel(metaclass=DirtyModelMeta):

    def __init__(self, data={}, **kwargs):
        self._original_data = {}
        self._modified_data = {}
        self._deleted_fields = []
        self.import_data(data)
        self.import_data(kwargs)

    def set_field_value(self, name, value):
        """
        Set the value to the field modified_data
        """
        if name in self._deleted_fields:
            self._deleted_fields.remove(name)
        if self._original_data.get(name) == value:
            if self._modified_data.get(name):
                self._modified_data.pop(name)
        else:
            self._modified_data[name] = value

    def get_field_value(self, name):
        """
        Get the field value from the modified data or the original one
        """
        if name in self._deleted_fields:
            return None
        return self._modified_data.get(name) or self._original_data.get(name)

    def delete_field_value(self, name):
        """
        Mark this field to be deleted
        """
        if self._original_data.get(name) or self._modified_data.get(name):
            if self._modified_data.get(name):
                self._modified_data.pop(name)
            self._deleted_fields.append(name)

    def import_data(self, data):
        """
        Set the fields established in data to the instance
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def export_data(self):
        """
        Get the results with the modified_data
        """
        result = {}

        for key, value in self._modified_data.items():
            if key not in self._deleted_fields:
                try:
                    result[key] = value.export_data()
                except AttributeError:
                    result[key] = value

        for key, value in self._original_data.items():
            if key not in self._deleted_fields and not result.get(key):
                try:
                    result[key] = value.export_data()
                except AttributeError:
                    result[key] = value

        return result

    def export_modified_data(self):
        """
        Get the modified data
        """
        # TODO: why None? Try to get a better flag
        result = {key: None for key in self._deleted_fields}

        for key, value in self._modified_data.items():
            if key not in result.keys():
                try:
                    result[key] = value.export_modified_data()
                except AttributeError:
                    result[key] = value

        for key, value in self._original_data.items():
            if key not in result.keys():
                try:
                    result[key] = value.export_modified_data()
                except AttributeError:
                    pass

        return result

    def flat_data(self):
        """
        Pass all the data from modified_data to original_data
        """
        def flat_field(value):
            try:
                value.flat_data()
                return value
            except AttributeError:
                return value

        modified_dict = self._original_data
        modified_dict.update(self._modified_data)
        self._original_data = dict((k, flat_field(v))
                                   for k, v in modified_dict.items()
                                   if k not in self._deleted_fields)

        self.clear_modified_data()

    def clear_modified_data(self):
        """
        Clears only the modified data
        """
        self._modified_data = {}
        self._deleted_fields = []

    def clear(self):
        """
        Clears all the data in the object
        """
        self._modified_data = {}
        self._original_data = {}
        self._deleted_fields = []
