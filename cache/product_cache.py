from cache.base import JSONCache


class ProductCache(JSONCache):
    def __init__(self, ttl: int = 3600):
        super().__init__(key_prefix="product", ttl=ttl)

    def get_product(self, product_id: str) -> dict | None:
        return self.get(product_id)

    def set_product(self, product_id: str, product_data: dict) -> None:
        self.set(product_id, product_data)

    def invalidate_product(self, product_id: str) -> None:
        self.delete(product_id)


def get_product_cache(ttl: int = 3600) -> ProductCache:
    if not hasattr(get_product_cache, "_instance"):
        get_product_cache._instance = ProductCache(ttl=ttl)  # type: ignore
    return get_product_cache._instance  # type: ignore
