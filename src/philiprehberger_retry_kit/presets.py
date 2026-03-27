from __future__ import annotations

import random
from typing import Any


def _apply_jitter(config: dict[str, Any], jitter: bool) -> dict[str, Any]:
    """Return a copy of config. When jitter is True, multiply initial_delay by a random factor [0.8, 1.2]."""
    result = dict(config)
    if jitter:
        factor = 0.8 + random.random() * 0.4
        result["initial_delay"] = result["initial_delay"] * factor
    return result


def exponential(*, jitter: bool = False) -> dict[str, Any]:
    """Return the aggressive preset config, optionally with jitter applied to delay."""
    config: dict[str, Any] = {
        "max_attempts": 5,
        "backoff": "exponential",
        "initial_delay": 0.5,
        "max_delay": 5.0,
        "jitter": True,
    }
    return _apply_jitter(config, jitter)


def gentle(*, jitter: bool = False) -> dict[str, Any]:
    """Return the gentle preset config, optionally with jitter applied to delay."""
    config: dict[str, Any] = {
        "max_attempts": 3,
        "backoff": "exponential",
        "initial_delay": 2.0,
        "max_delay": 30.0,
        "jitter": True,
    }
    return _apply_jitter(config, jitter)


def network_request(*, jitter: bool = False) -> dict[str, Any]:
    """Return the network_request preset config, optionally with jitter applied to delay."""
    config: dict[str, Any] = {
        "max_attempts": 3,
        "backoff": "exponential",
        "initial_delay": 1.0,
        "max_delay": 10.0,
        "jitter": True,
    }
    return _apply_jitter(config, jitter)


def database_query(*, jitter: bool = False) -> dict[str, Any]:
    """Return the database_query preset config, optionally with jitter applied to delay."""
    config: dict[str, Any] = {
        "max_attempts": 3,
        "backoff": "linear",
        "initial_delay": 0.5,
        "max_delay": 5.0,
        "jitter": False,
    }
    return _apply_jitter(config, jitter)


presets = {
    "aggressive": {
        "max_attempts": 5,
        "backoff": "exponential",
        "initial_delay": 0.5,
        "max_delay": 5.0,
        "jitter": True,
    },
    "gentle": {
        "max_attempts": 3,
        "backoff": "exponential",
        "initial_delay": 2.0,
        "max_delay": 30.0,
        "jitter": True,
    },
    "network_request": {
        "max_attempts": 3,
        "backoff": "exponential",
        "initial_delay": 1.0,
        "max_delay": 10.0,
        "jitter": True,
    },
    "database_query": {
        "max_attempts": 3,
        "backoff": "linear",
        "initial_delay": 0.5,
        "max_delay": 5.0,
        "jitter": False,
    },
}
