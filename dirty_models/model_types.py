"""
Internal types for dirty models
"""
import itertools
from dirty_models.base import BaseData, InnerFieldTypeMixin
from functools import wraps


def modified_data_decorator(function):
    """
    Decorator to initialise the modified_data if necessary. To be used in list functions
    to modify the list
    """

    @wraps(function)
    def func(self, *args, **kwargs):
        """Decorator function"""
        if not self.get_read_only() or not self.is_locked():
            self.initialise_modified_data()
            return function(self, *args, **kwargs)
        return lambda: None
    return func


class ListModel(InnerFieldTypeMixin, BaseData):

    """
    Dirty model for a list. It has the behavior to work as a list implementing its methods
    and has also the methods export_data, export_modified_data, import_data and flat_data
    to work also as a model, having the old and the modified values.
    """

    _original_data = None
    _modified_data = None

    def __init__(self, seq=None, *args, **kwargs):
        super(ListModel, self).__init__(*args, **kwargs)
        if seq is not None:
            self.extend(seq)

    def get_validated_object(self, value):
        """
        Returns the value validated by the field_type
        """
        try:
            if self.get_field_type().check_value(value) or self.get_field_type().can_use_value(value):
                data = self.get_field_type().use_value(value)
                self._prepare_child(data)
                return data
            else:
                return None
        except AttributeError:
            return value

    def initialise_modified_data(self):
        """
        Initialise the modified_data if necessary
        """
        if self._modified_data is None:
            if self._original_data:
                self._modified_data = list(self._original_data)
            else:
                self._modified_data = []

    @modified_data_decorator
    def __setitem__(self, key, value):
        """
        Function to set a value to an element e.g list[key] = value
        """

        if (self._original_data is not None and self._original_data.__getitem__(key) != value)\
                or not self._original_data:
            validated_value = self.get_validated_object(value)
            if validated_value is not None:
                self._modified_data.__setitem__(key, validated_value)

    def __getitem__(self, item):
        """
        Function to get an item from a list e.g list[key]
        """
        if self._modified_data:
            val = self._modified_data.__getitem__(item)
            if val is not None:
                return val
        if self._original_data:
            return self._original_data.__getitem__(item)

    @modified_data_decorator
    def __delitem__(self, key):
        """
        Delete item from a list
        """
        del self._modified_data[key]

    def __len__(self):
        """
        Function to get the list length
        """
        if self._modified_data is not None:
            return len(self._modified_data)
        elif self._original_data is not None:
            return len(self._original_data)
        return 0

    @modified_data_decorator
    def append(self, item):
        """
        Appending elements to our list
        """
        validated_value = self.get_validated_object(item)
        if validated_value is not None:
            self._modified_data.append(validated_value)

    @modified_data_decorator
    def insert(self, index, p_object):
        """
        Insert an element to a list
        """
        validated_value = self.get_validated_object(p_object)
        if validated_value is not None:
            self._modified_data.insert(index, validated_value)

    def index(self, value):
        """
        Gets the index in the list for a value
        """
        if self._modified_data is not None:
            return self._modified_data.index(value)
        if self._original_data is not None:
            return self._original_data.index(value)
        raise ValueError()

    def clear(self):
        """
        Resets our list, keeping original data
        """
        self._modified_data = []

    def clear_all(self):
        """
        Resets our list
        """
        self._original_data = None
        self._modified_data = None

    @modified_data_decorator
    def remove(self, value):
        """
        Deleting an element from the list
        """
        return self._modified_data.remove(value)

    @modified_data_decorator
    def extend(self, iterable):
        """
        Given an iterable, it adds the elements to our list
        """
        for value in iterable:
            self.append(value)

    @modified_data_decorator
    def pop(self, index=None):
        """
        Obtains and delete the element from the list
        """
        if self._modified_data is not None:
            return self._modified_data.pop(index)

    def count(self, value):
        """
        Gives the number of occurrencies of a value in the list
        """
        if self._modified_data is not None:
            return self._modified_data.count(value)
        if self._original_data is not None:
            return self._original_data.count(value)
        return 0

    @modified_data_decorator
    def reverse(self):
        """
        Reverses the list order
        """
        if self._modified_data:
            self._modified_data.reverse()

    @modified_data_decorator
    def sort(self):
        """
        Sorts the list
        """
        if self._modified_data:
            self._modified_data.sort()

    def __iter__(self):
        """
        Defined behaviour for our iterable to be iterated
        """
        if self._modified_data is not None:
            return self._modified_data.__iter__()
        if self._original_data is not None:
            return self._original_data.__iter__()
        return [].__iter__()

    def flat_data(self):
        """
        Function to pass our modified values to the original ones
        """

        def flat_field(value):
            """
            Flat item
            """
            try:
                value.flat_data()
                return value
            except AttributeError:
                return value

        modified_data = self._modified_data if self._modified_data is not None else self._original_data
        if modified_data is not None:
            self._original_data = [flat_field(value) for value in modified_data]
        self._modified_data = None

    def export_data(self):
        """
        Retrieves the data in a jsoned form
        """

        def export_field(value):
            """
            Export item
            """
            try:
                return value.export_data()
            except AttributeError:
                return value

        if self._modified_data is not None:
            return [export_field(value) for value in self._modified_data]
        if self._original_data is not None:
            return [export_field(value) for value in self._original_data]
        return []

    def export_modified_data(self):
        """
        Retrieves the modified data in a jsoned form
        """
        def export_modfield(value, is_modified_seq=True):
            """
            Export modified item
            """
            try:
                return value.export_modified_data()
            except AttributeError:
                if is_modified_seq:
                    return value

        if self._modified_data is not None:
            return [export_modfield(value) for value in self._modified_data]
        if self._original_data is not None:
            return list(x for x in [export_modfield(value) for value in self._original_data] if x is not None)
        return []

    def export_original_data(self):
        """
        Retrieves the original_data
        """
        def export_field(value):
            """
            Export item
            """
            try:
                return value.export_original_data()
            except AttributeError:
                return value
        return [export_field(val) for val in self._original_data]

    def import_data(self, data):
        """
        Uses data to add it to the list
        """
        if hasattr(data, '__iter__'):
            self.extend(data)

    def import_deleted_fields(self, data):
        """
        Set data fields to deleted
        """

        def child_delete_from_str(data_str):
            """
            Inner function to set children fields to deleted
            """
            parts = data_str.split('.', 1)
            if parts[0].isnumeric:
                self[int(parts[0])].import_deleted_fields(parts[1])

        if not self.get_read_only() or not self.is_locked():
            if isinstance(data, str):
                data = [data]
            if isinstance(data, list):
                for key in data:
                    child_delete_from_str(key)

    def export_deleted_fields(self):
        """
        Returns a list with any deleted fields form original data.
        In tree models, deleted fields on children will be appended.
        """
        result = []
        for item in self:
            try:
                deleted_fields = item.export_deleted_fields()
                index = str(self.index(item))
                for key in deleted_fields:
                    result.append(index + '.' + key)
            except AttributeError:
                pass
        return result

    def is_modified(self):
        """
        Returns whether list is modified or not
        """
        if self._modified_data is not None:
            return True
        for value in self._original_data:
            try:
                if value.is_modified():
                    return True
            except AttributeError:
                pass

        return False

    def clear_modified_data(self):
        """
        Clears only the modified data
        """
        self._modified_data = None

        for value in self._original_data:
            try:
                value.clear_modified_data()
            except AttributeError:
                pass

    def _update_read_only(self):
        for value in itertools.chain(self._original_data if self._original_data else [],
                                     self._modified_data if self._modified_data else []):
            try:
                value.set_read_only(self.get_read_only())
            except AttributeError:
                pass

    def delete_attr_by_path(self, field):
        """
        Function for deleting a field specifying the path in the whole model as described
        in :func:`dirty:models.models.BaseModel.perform_function_by_path`
        """
        index_list, next_field = self._get_indexes_by_path(field)
        if index_list:
            for index in index_list:
                if next_field:
                    self[index].delete_attr_by_path(next_field)
                else:
                    self.pop(index)

    def reset_attr_by_path(self, field):
        """
        Function for restoring a field specifying the path in the whole model as described
        in :func:`dirty:models.models.BaseModel.perform_function_by_path`
        """
        index_list, next_field = self._get_indexes_by_path(field)
        if index_list:
            if next_field:
                for index in index_list:
                    self[index].reset_attr_by_path(next_field)
            else:
                for index in index_list:
                    try:
                        self[index].clear_modified_data()
                    except (AttributeError, IndexError):
                        return

    def _get_indexes_by_path(self, field):
        """
        Function to perform a function to the field specified. Returns a list of index where the function has to be
        applied
        :param field: Field structure as following:
         *.subfield_2  would apply the function to the every subfield_2 of the elements
         1.subfield_2  would apply the function to the subfield_2 of the element 1
         * would apply the function to every element
         1 would apply the function to element 1
        :field function: string containing the function in the class to be applied to the field
        """
        try:
            field, next_field = field.split('.', 1)
        except ValueError:
            next_field = ''

        if field == '*':
            index_list = []
            for item in self:
                index_list.insert(0, self.index(item))
            if index_list:
                return index_list, next_field
            return [], None
        elif field.isnumeric():
            index = int(field)
            if index >= len(self):
                return None, None
            return [index], next_field

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str([item for item in self])
