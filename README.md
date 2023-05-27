# philiprehberger-retry-kit

[![Tests](https://github.com/philiprehberger/py-retry-kit/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-retry-kit/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-retry-kit.svg)](https://pypi.org/project/philiprehberger-retry-kit/)
[![License](https://img.shields.io/github/license/philiprehberger/py-retry-kit)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Retry with exponential backoff, circuit breaker, and presets for Python.

## Installation

```bash
pip install philiprehberger-retry-kit
```

## Usage

### Basic Retry

```python
from philiprehberger_retry_kit import retry

result = retry(lambda: fetch_data(), max_attempts=3)
```

### With Options

```python
result = retry(
    lambda: fetch_data(),
    max_attempts=5,
    backoff="exponential",      # "exponential" | "linear" | "fixed"
    initial_delay=1.0,
    max_delay=30.0,
    jitter=True,
    retry_on=lambda e: isinstance(e, ConnectionError),
    on_retry=lambda e, attempt: print(f"Retry {attempt}..."),
)
```

### Async Retry

```python
from philiprehberger_retry_kit import async_retry

result = await async_retry(
    lambda: async_fetch_data(),
    max_attempts=3,
    backoff="exponential",
)
```

### Presets

```python
from philiprehberger_retry_kit import retry, presets

result = retry(lambda: fetch_data(), **presets["network_request"])
result = retry(lambda: db_query(), **presets["database_query"])
result = retry(lambda: critical_op(), **presets["aggressive"])
result = retry(lambda: gentle_op(), **presets["gentle"])
```

### Circuit Breaker

```python
from philiprehberger_retry_kit import CircuitBreaker, CircuitOpenError

breaker = CircuitBreaker(
    failure_threshold=5,
    reset_timeout=30.0,
    on_state_change=lambda from_s, to_s: print(f"Circuit: {from_s} -> {to_s}"),
)

try:
    result = breaker.call(lambda: fetch_data())
except CircuitOpenError:
    print("Circuit is open, failing fast")
```

### Async Circuit Breaker

```python
result = await breaker.async_call(lambda: async_fetch_data())
```

## API Reference

| Function / Class | Description |
|---|---|
| `retry(fn, *, max_attempts=3, backoff="exponential", initial_delay=1.0, max_delay=30.0, jitter=True, retry_on=None, on_retry=None, on_success=None, on_failure=None)` | Retry a callable with configurable backoff |
| `async_retry(fn, *, ...)` | Async version of `retry()` with the same parameters |
| `CircuitBreaker(failure_threshold=5, reset_timeout=30.0, half_open_max_attempts=1, on_state_change=None, on_circuit_open=None)` | Circuit breaker that fails fast after repeated failures |
| `CircuitBreaker.call(fn)` | Execute function through the circuit breaker |
| `CircuitBreaker.async_call(fn)` | Async version of `call()` |
| `RetryError` | Raised when all retry attempts fail (`.attempts`, `.last_error`) |
| `CircuitOpenError` | Raised when circuit breaker is open |
| `presets` | Dict of preset configs: `"aggressive"`, `"gentle"`, `"network_request"`, `"database_query"` |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
