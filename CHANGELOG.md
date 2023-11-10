# Changelog

## 0.3.0 (2026-03-27)

- Add context manager support (`__enter__` / `__exit__`) to `CircuitBreaker`
- Add preset functions (`exponential`, `gentle`, `network_request`, `database_query`) with `jitter` parameter
- Add 8 badges, Support section, and compliance fixes to README
- Add `[tool.pytest.ini_options]` and `[tool.mypy]` to pyproject.toml
- Add `.github/` issue templates, PR template, and Dependabot config

## 0.2.3

- Add Development section to README
- Add wheel build target to pyproject.toml

## 0.2.0

- Add input validation for `max_attempts`, `backoff`, and `initial_delay` in `retry()` and `async_retry()`
- Add input validation for `failure_threshold` and `reset_timeout` in `CircuitBreaker`
- Add comprehensive test suite (~30 tests)
- Add API reference table to README

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0
- Initial release
