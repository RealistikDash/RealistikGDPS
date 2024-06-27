from __future__ import annotations

from copy import copy

from .base import AbstractAsyncCache
from .base import AbstractCache
from .base import KeyType

__all__ = (
    "SimpleMemoryCache",
    "LRUMemoryCache",
    "SimpleAsyncMemoryCache",
    "LRUAsyncMemoryCache",
)


def _ensure_key_type(key: KeyType) -> str:
    """To ensure behaviour parity with the database based caches, we convert
    the key to a string. This is because in memory, a key of `1` and `"1"` are
    different, but in the database, they are the same."""
    return str(key)


class SimpleMemoryCache[T](AbstractCache[T]):
    __slots__ = ("_cache",)

    def __init__(self) -> None:
        self._cache: dict[str, T] = {}

    def get(self, key: KeyType) -> T | None:
        # We are returning a copy to reflect the behaviour of the database
        # based caches.
        obj_db = self._cache.get(_ensure_key_type(key))

        if obj_db is None:
            return None

        return copy(obj_db)

    def set(self, key: KeyType, value: T) -> None:
        self._cache[_ensure_key_type(key)] = value

    def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


class LRUMemoryCache[T](AbstractCache[T]):
    __slots__ = ("_cache", "_max_size")

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[str, T] = {}

    def get(self, key: KeyType) -> T | None:
        key_str = _ensure_key_type(key)
        value = self._cache.get(key_str)
        if value is not None:
            del self._cache[key_str]
            self._cache[key_str] = value

        # We are returning a copy to reflect the behaviour of the database
        # based caches.
        return copy(value)

    def set(self, key: KeyType, value: T) -> None:
        while len(self._cache) >= self._capacity:
            # Cursed but the most efficient approach for large datasets
            del self._cache[next(iter(self._cache))]

        self._cache[_ensure_key_type(key)] = value

    def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


# Async variants
class SimpleAsyncMemoryCache[T](AbstractAsyncCache[T]):
    __slots__ = ("_cache",)

    def __init__(self) -> None:
        self._cache: dict[str, T] = {}

    async def get(self, key: KeyType) -> T | None:
        return self._cache.get(_ensure_key_type(key))

    async def set(self, key: KeyType, value: T) -> None:
        self._cache[_ensure_key_type(key)] = value

    async def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass


class LRUAsyncMemoryCache[T](AbstractAsyncCache[T]):
    __slots__ = ("_cache", "_max_size")

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[str, T] = {}

    async def get(self, key: KeyType) -> T | None:
        key_str = _ensure_key_type(key)
        value = self._cache.get(key_str)
        if value is not None:
            del self._cache[key_str]
            self._cache[key_str] = value
        return value

    async def set(self, key: KeyType, value: T) -> None:
        while len(self._cache) >= self._capacity:
            # Cursed but the most efficient approach for large datasets
            del self._cache[next(iter(self._cache))]

        self._cache[_ensure_key_type(key)] = value

    async def delete(self, key: KeyType) -> None:
        try:
            del self._cache[_ensure_key_type(key)]
        except KeyError:
            pass
