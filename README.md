# philiprehberger-retry-kit

[![Tests](https://github.com/philiprehberger/py-retry-kit/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-retry-kit/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-retry-kit.svg)](https://pypi.org/project/philiprehberger-retry-kit/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-retry-kit)](https://github.com/philiprehberger/py-retry-kit/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-retry-kit)](https://github.com/philiprehberger/py-retry-kit/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-retry-kit)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-retry-kit/bug)](https://github.com/philiprehberger/py-retry-kit/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-retry-kit/enhancement)](https://github.com/philiprehberger/py-retry-kit/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
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

### Preset Functions with Jitter

Preset functions accept a `jitter` parameter that randomizes the initial delay by a factor between 0.8 and 1.2, helping to spread out retry storms.

```python
from philiprehberger_retry_kit import exponential, gentle, network_request, database_query, retry

result = retry(lambda: fetch_data(), **exponential(jitter=True))
result = retry(lambda: gentle_op(), **gentle(jitter=True))
result = retry(lambda: api_call(), **network_request(jitter=True))
result = retry(lambda: db_query(), **database_query(jitter=True))
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

### Circuit Breaker as Context Manager

```python
breaker = CircuitBreaker(failure_threshold=3, reset_timeout=10.0)

try:
    with breaker:
        result = fetch_data()
except CircuitOpenError:
    print("Circuit is open")
```

On `__enter__`, the breaker checks if the circuit is open and raises `CircuitOpenError` if so. On `__exit__`, it records success or failure based on whether an exception occurred.

### Async Circuit Breaker

```python
result = await breaker.async_call(lambda: async_fetch_data())
```

## API

| Function / Class | Description |
|---|---|
| `retry(fn, *, max_attempts=3, backoff="exponential", initial_delay=1.0, max_delay=30.0, jitter=True, retry_on=None, on_retry=None, on_success=None, on_failure=None)` | Retry a callable with configurable backoff |
| `async_retry(fn, *, ...)` | Async version of `retry()` with the same parameters |
| `CircuitBreaker(failure_threshold=5, reset_timeout=30.0, half_open_max_attempts=1, on_state_change=None, on_circuit_open=None)` | Circuit breaker that fails fast after repeated failures |
| `CircuitBreaker.call(fn)` | Execute function through the circuit breaker |
| `CircuitBreaker.async_call(fn)` | Async version of `call()` |
| `CircuitBreaker.__enter__` / `__exit__` | Context manager support for circuit breaker |
| `RetryError` | Raised when all retry attempts fail (`.attempts`, `.last_error`) |
| `CircuitOpenError` | Raised when circuit breaker is open |
| `presets` | Dict of preset configs: `"aggressive"`, `"gentle"`, `"network_request"`, `"database_query"` |
| `exponential(jitter=False)` | Preset function returning aggressive config, with optional jitter |
| `gentle(jitter=False)` | Preset function returning gentle config, with optional jitter |
| `network_request(jitter=False)` | Preset function returning network request config, with optional jitter |
| `database_query(jitter=False)` | Preset function returning database query config, with optional jitter |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
