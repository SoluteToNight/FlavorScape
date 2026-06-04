import threading
from collections import OrderedDict

from .config import TILE_CACHE_SIZE


class LRUTileCache:
    """Thread-safe in-memory LRU cache for PNG tile bytes."""

    def __init__(self, max_size: int = 512):
        self._cache: OrderedDict[tuple, bytes] = OrderedDict()
        self._max = max_size
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, z: int, x: int, y: int) -> bytes | None:
        key = (z, x, y)
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            self._cache.move_to_end(key)
            self.hits += 1
            return self._cache[key]

    def set(self, z: int, x: int, y: int, data: bytes) -> None:
        key = (z, x, y)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                self._cache[key] = data
                if len(self._cache) > self._max:
                    self._cache.popitem(last=False)

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


tile_cache = LRUTileCache(TILE_CACHE_SIZE)
