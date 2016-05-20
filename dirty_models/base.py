'''
Base classes for Dirty Models
'''

import weakref


class BaseData:

    """
    Base class for data inside dirty model.
    """

    __slots__ = []

    _locked = None
    _read_only = None
    _parent = None

    def __init__(self, *args, **kwargs):
        self._locked = True
        self._read_only = False
        self._parent = None

    def get_read_only(self):
        """
        Returns whether model could be modified or not
        """
        return self._read_only

    def set_read_only(self, value):
        """
        Sets whether model could be modified or not
        """
        if self._read_only != value:
            self._read_only = value
            self._update_read_only()

    def get_parent(self):
        """
        Returns parent model
        """
        return self._parent() if self._parent else None

    def set_parent(self, value):
        """
        Sets parent model
        """
        self._parent = weakref.ref(value)

    def unlock(self):
        """
        Unlock model to be able to write even it's read only
        """
        self._locked = False

    def lock(self):
        """
        Lock model to avoid modification on read only fields
        """
        self._locked = True

    def is_locked(self):
        """
        Returns whether model is locked
        """
        if not self._locked:
            return False
        elif self.get_parent():
            return self.get_parent().is_locked()

        return True

    def _prepare_child(self, value):
        try:
            value.set_parent(self)
        except AttributeError:
            pass

        if self.get_read_only():
            try:
                value.set_read_only(True)
            except AttributeError:
                pass


class InnerFieldTypeMixin:

    _field_type = None

    def __init__(self, *args, **kwargs):
        if 'field_type' in kwargs:
            self._field_type = kwargs.pop('field_type')
        super(InnerFieldTypeMixin, self).__init__(*args, **kwargs)

    def get_field_type(self):
        return self._field_type


class Unlocker():

    """
    Unlocker instances helps to lock and unlock models easily
    """

    def __init__(self, item):
        self.item = item

    def __enter__(self):
        self.item.unlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.item.lock()
