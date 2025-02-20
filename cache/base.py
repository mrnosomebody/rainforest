import json
import random
from typing import Any, Optional

from django.core.cache import cache


class BaseCache:
    def __init__(self, key_prefix: str, ttl: int = 3600, jitter: int = 60):
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.jitter = jitter

    def _build_key(self, key: Any) -> str:
        return f"{self.key_prefix}:{key}"

    def get(self, key: Any) -> Optional[Any]:
        return cache.get(self._build_key(key))

    def set(self, key: Any, value: Any) -> None:
        cache.set(
            self._build_key(key), value, self.ttl + random.randint(0, self.jitter)
        )

    def delete(self, key: Any) -> None:
        cache.delete(self._build_key(key))


class JSONCache(BaseCache):
    def get(self, key: Any) -> Any | None:
        raw = super().get(key)
        if raw is not None:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        return None

    def set(self, key: Any, value: Any) -> None:
        json_value = json.dumps(value)
        super().set(key, json_value)
