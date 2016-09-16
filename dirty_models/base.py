'''
Base classes for Dirty Models
'''

import weakref


class BaseData:

    """
    Base class for data inside dirty model.
    """

    __slots__ = []

    __locked__ = None
    __read_only__ = None
    __parent__ = None

    def __init__(self, *args, **kwargs):
        self.__locked__ = True
        self.__read_only__ = False
        self.__parent__ = None

    def get_read_only(self):
        """
        Returns whether model could be modified or not
        """
        return self.__read_only__

    def set_read_only(self, value):
        """
        Sets whether model could be modified or not
        """
        if self.__read_only__ != value:
            self.__read_only__ = value
            self._update_read_only()

    def get_parent(self):
        """
        Returns parent model
        """
        return self.__parent__() if self.__parent__ else None

    def set_parent(self, value):
        """
        Sets parent model
        """
        self.__parent__ = weakref.ref(value)

    def unlock(self):
        """
        Unlock model to be able to write even it's read only
        """
        self.__locked__ = False

    def lock(self):
        """
        Lock model to avoid modification on read only fields
        """
        self.__locked__ = True

    def is_locked(self):
        """
        Returns whether model is locked
        """
        if not self.__locked__:
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
