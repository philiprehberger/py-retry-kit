from __future__ import annotations

import asyncio
import time
from unittest.mock import patch, MagicMock

import pytest

from philiprehberger_retry_kit import (
    retry,
    async_retry,
    RetryError,
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    presets,
)


# --- retry basics ---

def test_retry_succeeds_first_try():
    result = retry(lambda: 42, max_attempts=3, jitter=False)
    assert result == 42


def test_retry_succeeds_on_nth_try():
    calls = {"count": 0}
    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("fail")
        return "ok"
    result = retry(flaky, max_attempts=5, initial_delay=0, jitter=False)
    assert result == "ok"
    assert calls["count"] == 3


def test_retry_exhausts_all_attempts():
    with pytest.raises(RetryError) as exc_info:
        retry(lambda: (_ for _ in ()).throw(RuntimeError("boom")), max_attempts=3, initial_delay=0, jitter=False)
    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value.last_error, RuntimeError)


# --- RetryError attributes ---

def test_retry_error_attributes():
    try:
        retry(lambda: (_ for _ in ()).throw(ValueError("test")), max_attempts=2, initial_delay=0, jitter=False)
    except RetryError as e:
        assert e.attempts == 2
        assert isinstance(e.last_error, ValueError)
        assert str(e.last_error) == "test"


# --- Backoff strategies ---

@patch("philiprehberger_retry_kit.retry.time.sleep")
def test_exponential_backoff(mock_sleep):
    calls = {"count": 0}
    def fail_twice():
        calls["count"] += 1
        if calls["count"] <= 2:
            raise RuntimeError("fail")
        return "ok"
    retry(fail_twice, max_attempts=3, backoff="exponential", initial_delay=1.0, jitter=False)
    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0][0][0] == 1.0
    assert mock_sleep.call_args_list[1][0][0] == 2.0


@patch("philiprehberger_retry_kit.retry.time.sleep")
def test_linear_backoff(mock_sleep):
    calls = {"count": 0}
    def fail_twice():
        calls["count"] += 1
        if calls["count"] <= 2:
            raise RuntimeError("fail")
        return "ok"
    retry(fail_twice, max_attempts=3, backoff="linear", initial_delay=1.0, jitter=False)
    assert mock_sleep.call_args_list[0][0][0] == 1.0
    assert mock_sleep.call_args_list[1][0][0] == 2.0


@patch("philiprehberger_retry_kit.retry.time.sleep")
def test_fixed_backoff(mock_sleep):
    calls = {"count": 0}
    def fail_twice():
        calls["count"] += 1
        if calls["count"] <= 2:
            raise RuntimeError("fail")
        return "ok"
    retry(fail_twice, max_attempts=3, backoff="fixed", initial_delay=1.5, jitter=False)
    assert mock_sleep.call_args_list[0][0][0] == 1.5
    assert mock_sleep.call_args_list[1][0][0] == 1.5


# --- Jitter ---

@patch("philiprehberger_retry_kit.retry.time.sleep")
def test_jitter_delay_in_range(mock_sleep):
    calls = {"count": 0}
    def fail_once():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("fail")
        return "ok"
    retry(fail_once, max_attempts=2, backoff="fixed", initial_delay=2.0, jitter=True)
    delay = mock_sleep.call_args[0][0]
    assert 1.0 <= delay <= 2.0  # 2.0 * [0.5, 1.0]


# --- retry_on filter ---

def test_retry_on_matching():
    calls = {"count": 0}
    def flaky():
        calls["count"] += 1
        if calls["count"] == 1:
            raise ConnectionError("timeout")
        return "ok"
    result = retry(flaky, max_attempts=3, initial_delay=0, jitter=False,
                   retry_on=lambda e: isinstance(e, ConnectionError))
    assert result == "ok"


def test_retry_on_non_matching():
    with pytest.raises(ValueError):
        retry(
            lambda: (_ for _ in ()).throw(ValueError("bad")),
            max_attempts=3, initial_delay=0, jitter=False,
            retry_on=lambda e: isinstance(e, ConnectionError),
        )


# --- Callbacks ---

def test_on_retry_callback():
    log = []
    calls = {"count": 0}
    def fail_once():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("fail")
        return "ok"
    retry(fail_once, max_attempts=3, initial_delay=0, jitter=False,
          on_retry=lambda e, a: log.append((str(e), a)))
    assert log == [("fail", 1)]


def test_on_success_callback():
    log = []
    retry(lambda: "ok", max_attempts=3, jitter=False,
          on_success=lambda r, a: log.append((r, a)))
    assert log == [("ok", 1)]


def test_on_failure_callback():
    log = []
    with pytest.raises(RetryError):
        retry(lambda: (_ for _ in ()).throw(RuntimeError("boom")),
              max_attempts=2, initial_delay=0, jitter=False,
              on_failure=lambda e, m: log.append((str(e), m)))
    assert log == [("boom", 2)]


# --- Validation ---

def test_max_attempts_zero_raises():
    with pytest.raises(ValueError, match="max_attempts"):
        retry(lambda: 1, max_attempts=0)


def test_invalid_backoff_raises():
    with pytest.raises(ValueError, match="Invalid backoff"):
        retry(lambda: 1, backoff="unknown")


def test_negative_initial_delay_raises():
    with pytest.raises(ValueError, match="initial_delay"):
        retry(lambda: 1, initial_delay=-1.0)


# --- Presets ---

def test_presets_have_required_keys():
    required = {"max_attempts", "backoff", "initial_delay", "max_delay", "jitter"}
    for name, preset in presets.items():
        assert required.issubset(preset.keys()), f"Preset '{name}' missing keys"


def test_preset_can_be_spread_into_retry():
    result = retry(lambda: "ok", **{**presets["gentle"], "jitter": False})
    assert result == "ok"


# --- CircuitBreaker ---

def test_circuit_closed_to_open():
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    assert cb.state == CircuitState.OPEN


def test_open_rejects_immediately():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=999.0)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    with pytest.raises(CircuitOpenError):
        cb.call(lambda: "ok")


def test_half_open_to_closed_on_success():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.01)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    assert cb.state == CircuitState.OPEN
    time.sleep(0.02)
    result = cb.call(lambda: "recovered")
    assert result == "recovered"
    assert cb.state == CircuitState.CLOSED


def test_half_open_to_open_on_failure():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.01)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    time.sleep(0.02)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail again")))
    assert cb.state == CircuitState.OPEN


def test_state_change_callback():
    log = []
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0,
                        on_state_change=lambda f, t: log.append((f, t)))
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    assert log == [(CircuitState.CLOSED, CircuitState.OPEN)]


def test_circuit_open_callback():
    log = []
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0,
                        on_circuit_open=lambda count: log.append(count))
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    assert log == [1]


# --- CircuitBreaker validation ---

def test_circuit_failure_threshold_zero_raises():
    with pytest.raises(ValueError, match="failure_threshold"):
        CircuitBreaker(failure_threshold=0)


def test_circuit_reset_timeout_negative_raises():
    with pytest.raises(ValueError, match="reset_timeout"):
        CircuitBreaker(reset_timeout=-1)


# --- async_retry ---

def test_async_retry_success():
    async def fn():
        return "async_ok"
    result = asyncio.run(async_retry(fn, max_attempts=2, jitter=False))
    assert result == "async_ok"


def test_async_retry_exhaustion():
    async def fn():
        raise RuntimeError("async fail")
    with pytest.raises(RetryError):
        asyncio.run(async_retry(fn, max_attempts=2, initial_delay=0, jitter=False))
