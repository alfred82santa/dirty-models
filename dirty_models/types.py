class ListModel():

    """
    Dirty model for a list. It has the behavior to work as a list implementing its methods
    and has also the methods export_data, export_modified_data, import_data and flat_data
    to work also as a model, having the old and the modified values.
    """

    _original_data = None
    _modified_data = None

    def __init__(self, seq=None, field_type=None):
        self.field_type = field_type
        if seq is not None:
            self.extend(seq)

    def get_validated_object(self, value):
        """
        Returns the value validated by the field_type
        """
        try:
            if self.field_type.check_value(value) or self.field_type.can_use_value(value):
                return self.field_type.use_value(value)
            else:
                return None
        except AttributeError:
            return value

    def initialise_modified_data(function):
        """
        Decorator to initialise the modified_data if necessary. To be used in list functions
        to modify the list
        """
        def func(*args, **kwargs):
            if args[0]._modified_data is None:
                if args[0]._original_data:
                    args[0]._modified_data = list(args[0]._original_data)
                else:
                    args[0]._modified_data = []
            return function(*args, **kwargs)
        return func

    @initialise_modified_data
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

    @initialise_modified_data
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

    @initialise_modified_data
    def append(self, item):
        """
        Appending elements to our list
        """
        validated_value = self.get_validated_object(item)
        if validated_value is not None:
            self._modified_data.append(validated_value)

    @initialise_modified_data
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
        Resets our list
        """
        self._original_data = None
        self._modified_data = None

    @initialise_modified_data
    def remove(self, value):
        """
        Deleting an element from the list
        """
        return self._modified_data.remove(value)

    @initialise_modified_data
    def extend(self, iterable):
        """
        Given an iterable, it adds the elements to our list
        """
        for value in iterable:
            self.append(value)

    @initialise_modified_data
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

    @initialise_modified_data
    def reverse(self):
        """
        Reverses the list order
        """
        if self._modified_data:
            self._modified_data.reverse()

    @initialise_modified_data
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
            try:
                value.flat_data()
                return value
            except AttributeError:
                return value

        self._original_data = [flat_field(value) for value in self._modified_data]
        self._modified_data = None

    def export_data(self):
        """
        Retrieves the data in a jsoned form
        """

        def export_field(value):
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
            try:
                return value.export_modified_data()
            except AttributeError:
                if is_modified_seq:
                    return value

        if self._modified_data is not None:
            return [export_modfield(value) for value in self._modified_data]

        if self._original_data is not None:
            return list(filter(lambda x: x is not None, [export_modfield(value) for value in self._original_data]))
        return []

    def import_data(self, data):
        """
        Uses data to add it to the list
        """
        if hasattr(data, '__iter__'):
            self.extend(data)