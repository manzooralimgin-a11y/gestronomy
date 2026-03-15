"""Unit tests for JWT utility functions."""
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password() -> None:
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token() -> None:
    token = create_access_token(sub=42, extra={"role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "admin"


def test_create_and_decode_refresh_token() -> None:
    token = create_refresh_token(sub=42)
    payload = decode_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_access_token_rejected_as_refresh() -> None:
    token = create_access_token(sub=1)
    assert decode_refresh_token(token) is None


def test_refresh_token_rejected_as_access() -> None:
    token = create_refresh_token(sub=1)
    assert decode_access_token(token) is None


def test_decode_invalid_token_returns_none() -> None:
    assert decode_access_token("invalid.token.here") is None
    assert decode_refresh_token("invalid.token.here") is None
