import pytest
from app.domain.entities import OwnerID
from app.infrastructure.opaque_token_repo import OpaqueTokenStore


def test_generate_and_get_token():
    store = OpaqueTokenStore(capacity=10)
    token = store.generate_and_store(OwnerID(owner_id="1"))
    assert token is not None
    assert len(token) > 0
    retrieved = store.get_token(token)
    assert retrieved == OwnerID(owner_id="1")


def test_get_token_nonexistent():
    store = OpaqueTokenStore(capacity=10)
    assert store.get_token("non_existent_opaque_token") is None


def test_remove_token_valid():
    store = OpaqueTokenStore(capacity=10)
    token = store.generate_and_store(OwnerID(owner_id="1"))
    result = store.remove_token(token)
    assert result is True
    assert store.get_token(token) is None


def test_remove_token_nonexistent():
    store = OpaqueTokenStore(capacity=10)
    result = store.remove_token("non_existent_token")
    assert result is False


def test_lru_capacity_eviction():
    store = OpaqueTokenStore(capacity=2)
    token1 = store.generate_and_store(OwnerID(owner_id="1"))
    token2 = store.generate_and_store(OwnerID(owner_id="2"))

    assert store.get_token(token1) == OwnerID(owner_id="1")

    token3 = store.generate_and_store(OwnerID(owner_id="3"))

    assert store.get_token(token1) == OwnerID(owner_id="1")
    assert store.get_token(token2) is None
    assert store.get_token(token3) == OwnerID(owner_id="3")
