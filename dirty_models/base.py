'''
Created on 28/03/2014

@author: alfred
'''
import weakref


class BaseData():

    def __init__(self, *args, **kwargs):
        self._locked = True
        self._read_only = False
        self._parent = None

    def get_read_only(self):
        return self._read_only

    def set_read_only(self, value):
        if self._read_only != value:
            self._read_only = value
            self._update_read_only()

    def get_parent(self):
        return self._parent() if self._parent else None

    def set_parent(self, value):
        self._parent = weakref.ref(value)

    def unlock(self):
        self._locked = False

    def lock(self):
        self._locked = True

    def is_locked(self):
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


class Unlocker():

    def __init__(self, item):
        self.item = item

    def __enter__(self):
        self.item.unlock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.item.lock()
