class ListModel():

    _original_data = None
    _modified_data = None

    def __init__(self, seq=None, field_type=None):
        self.field_type = field_type
        if seq is not None:
            self.extend(seq)

    def get_validated_object(self, value):
        try:
            if self.field_type.check_value(value) or self.field_type.can_use_value(value):
                return self.field_type.use_value(value)
            else:
                return None
        except AttributeError:
            return value

    def initialise_modified_data(function):
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
        if (self._original_data is not None and self._original_data.__getitem__(key) != value)\
            or not self._original_data:
            validated_value = self.get_validated_object(value)
            if validated_value is not None:
                self._modified_data.__setitem__(key, validated_value)

    def __getitem__(self, item):
        if self._modified_data:
            val = self._modified_data.__getitem__(item)
            if val is not None:
                return val
        if self._original_data:
            return self._original_data.__getitem__(item)

    @initialise_modified_data
    def __delitem__(self, key):
        del self._modified_data[key]

    def __len__(self):
        if self._modified_data is not None:
            return len(self._modified_data)
        elif self._original_data is not None:
            return len(self._original_data)
        return 0

    @initialise_modified_data
    def append(self, item):
        validated_value = self.get_validated_object(item)
        if validated_value is not None:
            self._modified_data.append(validated_value)

    @initialise_modified_data
    def insert(self, index, p_object):
        validated_value = self.get_validated_object(p_object)
        if validated_value is not None:
            self._modified_data.insert(index, validated_value)

    def index(self, value, start=None, stop=None):
        kwargs = {}
        if start:
            kwargs["start"] = start
        if stop:
            kwargs["stop"] = stop
        if self._modified_data is not None:
            return self._modified_data.index(value, **kwargs)
        if self._original_data is not None:
            return self._original_data.index(value, **kwargs)
        raise ValueError()

    def clear(self):
        self._original_data = None
        self._modified_data = None

    @initialise_modified_data
    def remove(self, value):
        return self._modified_data.remove(value)

    @initialise_modified_data
    def extend(self, iterable):
        for value in iterable:
            self.append(value)

    @initialise_modified_data
    def pop(self, index=None):
        if self._modified_data is not None:
            return self._modified_data.pop(index)
        raise IndexError()

    def count(self, value):
        if self._modified_data is not None:
            return self._modified_data.count(value)
        if self._original_data is not None:
            return self._original_data.count(value)
        return 0

    @initialise_modified_data
    def reverse(self):
        if self._modified_data:
            self._modified_data.reverse()

    @initialise_modified_data
    def sort(self, key=None, reverse=False):
        if self._modified_data:
            self._modified_data.sort(key, reverse)

    def __iter__(self):
        if self._modified_data is not None:
            return self._modified_data.__iter__()
        if self._original_data is not None:
            return self._original_data.__iter__()
        return [].__iter__()

    def flat_data(self):

        def flat_field(value):
            try:
                value.flat_data()
                return value
            except AttributeError:
                return value

        self._original_data = [flat_field(value) for value in self._modified_data]
        self._modified_data = None

    def export_data(self):

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

        def export_modified_field(value, is_modified_seq=True):
            try:
                return value.export_modified_data()
            except AttributeError:
                if is_modified_seq:
                    return value

        if self._modified_data is not None:
            return [export_modified_field(value) for value in self._modified_data]

        if self._original_data is not None:
            return list(filter(lambda x: x is not None,
                               [export_modified_field(value) for value in self._original_data]))
        return []

    def import_data(self, data):
        if hasattr(data, '__iter__'):
            self.extend(data)