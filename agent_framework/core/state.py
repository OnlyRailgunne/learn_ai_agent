#state.py
import copy

class State:
    """Agent runtime state manager for storing and retrieving key-value data.

    Provides a simple interface for managing state during agent execution,
    including setting, getting, checking, and clearing state data.
    """

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def has(self, key):
        return key in self._data

    def clear(self):
        self._data.clear()

    def export(self):
        """Export the current state as a dictionary."""
        return self._data.copy()

    def restore(self, data):
        """Restore the state from a dictionary."""
        self._data = copy.deepcopy(data)