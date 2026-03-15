"""Tests for config validation logic."""
import os

import pytest


def test_production_rejects_default_secret() -> None:
    """In production, the default secret key must be rejected."""
    env_overrides = {
        "APP_ENV": "production",
        "SECRET_KEY": "change-me-to-a-random-secret-key-in-production",
    }
    original = {k: os.environ.get(k) for k in env_overrides}
    try:
        os.environ.update(env_overrides)
        from app.config import Settings

        with pytest.raises(ValueError, match="SECRET_KEY must be set"):
            Settings()
    finally:
        for k, v in original.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_development_allows_default_secret() -> None:
    """In development, the default secret key should be allowed."""
    env_overrides = {"APP_ENV": "development"}
    original = {k: os.environ.get(k) for k in env_overrides}
    try:
        os.environ.update(env_overrides)
        # Should not raise — remove cached settings
        from app.config import Settings

        s = Settings()
        assert s.secret_key == "change-me-to-a-random-secret-key-in-production"
    finally:
        for k, v in original.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_sql_echo_only_in_development() -> None:
    """sql_echo should only be True when both debug=True and app_env=development."""
    from app.config import Settings

    s = Settings(debug=True, app_env="development")
    assert s.sql_echo is True

    s = Settings(debug=True, app_env="staging")
    assert s.sql_echo is False

    s = Settings(debug=False, app_env="development")
    assert s.sql_echo is False
