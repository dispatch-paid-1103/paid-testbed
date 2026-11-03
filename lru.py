"""A simple least-recently-used (LRU) cache."""

from collections import OrderedDict
from typing import Any, Hashable


class LRUCache:
    """Fixed-capacity cache that evicts the least recently used entry.

    Both ``get`` and ``put`` count as a use of a key. Because ``get`` returns
    ``None`` for a missing key, a stored value of ``None`` cannot be told apart
    from a miss.
    """

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        # Least recently used entry first, most recently used last.
        self._data: "OrderedDict[Hashable, Any]" = OrderedDict()

    def get(self, key: Hashable) -> Any:
        """Return the value for ``key`` and mark it most recent, or ``None`` if missing."""
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: Hashable, value: Any) -> None:
        """Store ``value`` under ``key``, evicting the least recently used entry if full."""
        if key in self._data:
            self._data[key] = value
            self._data.move_to_end(key)
            return
        self._data[key] = value
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)
