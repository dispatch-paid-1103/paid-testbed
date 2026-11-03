import pytest

from lru import LRUCache


@pytest.mark.parametrize("capacity", [0, -1])
def test_invalid_capacity_raises(capacity):
    with pytest.raises(ValueError):
        LRUCache(capacity)


def test_get_missing_returns_none():
    assert LRUCache(2).get("missing") is None


def test_put_then_get():
    cache = LRUCache(2)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_eviction_of_least_recently_used():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert len(cache) == 2


def test_get_counts_as_use():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_put_existing_updates_and_refreshes():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    assert len(cache) == 2
    assert cache.get("b") == 2
    cache.put("a", 11)
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 11
    assert cache.get("c") == 3


def test_len_grows_up_to_capacity():
    cache = LRUCache(3)
    assert len(cache) == 0
    for i, key in enumerate("abcd", start=1):
        cache.put(key, i)
        assert len(cache) == min(i, 3)


def test_capacity_one():
    cache = LRUCache(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert len(cache) == 1
