"""
Internal types for dirty models
"""
import itertools
from .base import BaseData, InnerFieldTypeMixin
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

    def __init__(self, seq=None, *args, **kwargs):
        super(ListModel, self).__init__(*args, **kwargs)
        self.__original_data__ = []
        self.__modified_data__ = None
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
        if self.__modified_data__ is None:
            if self.__original_data__:
                self.__modified_data__ = list(self.__original_data__)
            else:
                self.__modified_data__ = []

    @modified_data_decorator
    def __setitem__(self, key, value):
        """
        Function to set a value to an element e.g list[key] = value
        """

        validated_value = self.get_validated_object(value)
        if validated_value is not None:
            self.__modified_data__.__setitem__(key, validated_value)

    def __getitem__(self, item):
        """
        Function to get an item from a list e.g list[key]
        """
        if not isinstance(item, (str, int, slice)):
            raise TypeError("Item must be an integer, slice or string")

        if isinstance(item, str):
            try:
                return self.get_1st_attr_by_path(item)
            except AttributeError as ex:
                raise KeyError(str(ex))

        if self.__modified_data__ is not None:
            val = self.__modified_data__.__getitem__(item)
            if val is not None:
                return val
        return self.__original_data__.__getitem__(item)

    @modified_data_decorator
    def __delitem__(self, key):
        """
        Delete item from a list
        """
        del self.__modified_data__[key]

    def __len__(self):
        """
        Function to get the list length
        """
        if self.__modified_data__ is not None:
            return len(self.__modified_data__)
        return len(self.__original_data__)

    @modified_data_decorator
    def append(self, item):
        """
        Appending elements to our list
        """
        validated_value = self.get_validated_object(item)
        if validated_value is not None:
            self.__modified_data__.append(validated_value)

    @modified_data_decorator
    def insert(self, index, p_object):
        """
        Insert an element to a list
        """
        validated_value = self.get_validated_object(p_object)
        if validated_value is not None:
            self.__modified_data__.insert(index, validated_value)

    def index(self, value):
        """
        Gets the index in the list for a value
        """
        if self.__modified_data__ is not None:
            return self.__modified_data__.index(value)
        return self.__original_data__.index(value)

    def clear(self):
        """
        Resets our list, keeping original data
        """
        self.__modified_data__ = None

    def clear_all(self):
        """
        Resets our list
        """
        self.__original_data__ = []
        self.__modified_data__ = None

    @modified_data_decorator
    def remove(self, value):
        """
        Deleting an element from the list
        """
        return self.__modified_data__.remove(value)

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
        if self.__modified_data__ is not None:
            return self.__modified_data__.pop(index)

    def count(self, value):
        """
        Gives the number of occurrencies of a value in the list
        """
        if self.__modified_data__ is not None:
            return self.__modified_data__.count(value)
        return self.__original_data__.count(value)

    @modified_data_decorator
    def reverse(self):
        """
        Reverses the list order
        """
        if self.__modified_data__:
            self.__modified_data__.reverse()

    @modified_data_decorator
    def sort(self):
        """
        Sorts the list
        """
        if self.__modified_data__:
            self.__modified_data__.sort()

    def __iter__(self):
        """
        Defined behaviour for our iterable to be iterated
        """
        if self.__modified_data__ is not None:
            return self.__modified_data__.__iter__()
        return self.__original_data__.__iter__()

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

        modified_data = self.__modified_data__ if self.__modified_data__ is not None else self.__original_data__
        if modified_data is not None:
            self.__original_data__ = [flat_field(value) for value in modified_data]
        self.__modified_data__ = None

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

        if self.__modified_data__ is not None:
            return [export_field(value) for value in self.__modified_data__]
        return [export_field(value) for value in self.__original_data__]

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

        if self.__modified_data__ is not None:
            return [export_modfield(value) for value in self.__modified_data__]
        return list(x for x in [export_modfield(value) for value in self.__original_data__] if x is not None)

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
        return [export_field(val) for val in self.__original_data__]

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
        if self.__modified_data__ is not None:
            return True
        for value in self.__original_data__:
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
        self.__modified_data__ = None

        for value in self.__original_data__:
            try:
                value.clear_modified_data()
            except AttributeError:
                pass

    def _update_read_only(self):
        for value in itertools.chain(self.__original_data__ if self.__original_data__ else [],
                                     self.__modified_data__ if self.__modified_data__ else []):
            try:
                value.set_read_only(self.get_read_only())
            except AttributeError:
                pass

    def get_attrs_by_path(self, field_path, stop_first=False):
        """
        It returns list of values looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: list or None.
        :param stop_first: Stop iteration on first value looked up. Default: False.
        :type stop_first: bool
        :return: value
        """
        index_list, next_field = self._get_indexes_by_path(field_path)
        values = []
        for idx in index_list:
            if next_field:
                try:
                    res = self[idx].get_attrs_by_path(next_field, stop_first=stop_first)
                    if res is None:
                        continue
                    values.extend(res)

                    if stop_first and len(values):
                        break

                except AttributeError:
                    pass
            else:
                if stop_first:
                    return [self[idx], ]
                values.append(self[idx])

        return values if len(values) else None

    def get_1st_attr_by_path(self, field_path, **kwargs):
        """
        It returns first value looked up by field path.
        Field path is dot-formatted string path: ``parent_field.child_field``.

        :param field_path: field path. It allows ``*`` as wildcard.
        :type field_path: str
        :param default: Default value if field does not exist.
                        If it is not defined :class:`AttributeError` exception will be raised.
        :return: value
        """

        res = self.get_attrs_by_path(field_path, stop_first=True)
        if res is None:
            if 'default' in kwargs:
                return kwargs['default']
            raise AttributeError("Field '{0}' does not exist".format(field_path))
        return res.pop()

    def delete_attr_by_path(self, field):
        """
        Function for deleting a field specifying the path in the whole model as described
        in :func:`dirty:models.models.BaseModel.perform_function_by_path`
        """
        index_list, next_field = self._get_indexes_by_path(field)
        if index_list:
            for index in reversed(index_list):
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
        Returns a list of indexes by field path.

        :param field: Field structure as following:
         *.subfield_2  would apply the function to the every subfield_2 of the elements
         1.subfield_2  would apply the function to the subfield_2 of the element 1
         * would apply the function to every element
         1 would apply the function to element 1
        """
        try:
            field, next_field = field.split('.', 1)
        except ValueError:
            next_field = ''

        if field == '*':
            index_list = []
            for item in self:
                index_list.append(self.index(item))
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

    def __contains__(self, item):
        return item in self.__modified_data__ if self.__modified_data__ is not None else item in self.__original_data__
