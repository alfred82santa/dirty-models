'''
Base classes for Dirty Models
'''

import weakref

__all__ = ['Unlocker', 'Creating', 'AccessMode']

from abc import abstractmethod

from enum import IntEnum


class AccessMode(IntEnum):
    READ_AND_WRITE = 0
    WRITABLE_ONLY_ON_CREATION = 1
    READ_ONLY = 2
    HIDDEN = 3

    def __and__(self, other):
        return max(self, other)

    def __or__(self, other):
        return min(self, other)


class BaseData:
    """
    Base class for data inside dirty model.
    """

    __locked__ = None
    __access_mode__ = None
    __is_creating__ = None
    __parent__ = None

    def __init__(self, *args, __is_creating=False, **kwargs):
        self.__locked__ = True
        self.__access_mode__ = AccessMode.READ_AND_WRITE
        self.__is_creating__ = __is_creating
        self.__parent__ = None

    def get_access_mode(self):
        """
        Returns how model could be acceded
        """
        am = self.__access_mode__
        if not am \
                or (self.is_creating() and am <= AccessMode.WRITABLE_ONLY_ON_CREATION) \
                or not self.is_locked():
            am = AccessMode.READ_AND_WRITE

        if self.get_parent():
            am &= self.get_parent().get_access_mode()
        return am

    def set_access_mode(self, value):
        """
        Sets whether model could be acceded
        """
        if self.__access_mode__ != value:
            self.__access_mode__ = value
            self._update_access_mode()

    @abstractmethod
    def _update_access_mode(self):  # pragma: no cover
        pass

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

    def start_creation(self):
        """
        Mark model to be able to set creation-only fields.
        """
        self.__is_creating__ = True

    def end_creation(self):
        """
        Unmark model to be able to set creation-only fields.
        """
        self.__is_creating__ = False

    def is_creating(self):
        """
        Returns whether model is marked on creation mode.
        """
        if self.__is_creating__:
            return True
        elif self.get_parent():
            return self.get_parent().is_creating()

        return False

    def _prepare_child(self, value):
        try:
            value.set_parent(self)
        except AttributeError:
            pass


class InnerFieldTypeMixin:
    __field_type__ = None

    def __init__(self, *args, **kwargs):
        if 'field_type' in kwargs:
            self.__field_type__ = kwargs.pop('field_type')
        super(InnerFieldTypeMixin, self).__init__(*args, **kwargs)

    def get_field_type(self):
        return self.__field_type__


class Unlocker():
    """
    Unlocker instances helps to lock and unlock models easily
    """

    def __init__(self, item):
        self.item = item

    def __enter__(self):
        self.item.unlock()
        return self.item

    def __exit__(self, exc_type, exc_value, traceback):
        self.item.lock()


class Creating():
    """
    Creating instances helps to mark and unmark models as creating easily
    """

    def __init__(self, item):
        self.item = item

    def __enter__(self):
        self.item.start_creation()
        return self.item

    def __exit__(self, exc_type, exc_value, traceback):
        self.item.end_creation()
