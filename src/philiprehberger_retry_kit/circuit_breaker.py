from __future__ import annotations

import time
from enum import Enum
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    def __init__(self) -> None:
        super().__init__("Circuit breaker is open — request rejected")


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        half_open_max_attempts: int = 1,
        on_state_change: Callable[[CircuitState, CircuitState], None] | None = None,
        on_circuit_open: Callable[[int], None] | None = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._half_open_max_attempts = half_open_max_attempts
        self._on_state_change = on_state_change
        self._on_circuit_open = on_circuit_open

        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time = 0.0
        self._half_open_attempts = 0

    @property
    def state(self) -> CircuitState:
        return self._state

    def _transition(self, to: CircuitState) -> None:
        if self._state != to:
            from_state = self._state
            self._state = to
            if self._on_state_change:
                self._on_state_change(from_state, to)

    def call(self, fn: Callable[[], T]) -> T:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self._reset_timeout:
                self._transition(CircuitState.HALF_OPEN)
                self._half_open_attempts = 0
            else:
                raise CircuitOpenError()

        if self._state == CircuitState.HALF_OPEN and self._half_open_attempts >= self._half_open_max_attempts:
            raise CircuitOpenError()

        try:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_attempts += 1

            result = fn()

            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.CLOSED)
            self._failures = 0
            return result
        except Exception:
            self._failures += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.OPEN)
                if self._on_circuit_open:
                    self._on_circuit_open(self._failures)
            elif self._failures >= self._failure_threshold:
                self._transition(CircuitState.OPEN)
                if self._on_circuit_open:
                    self._on_circuit_open(self._failures)

            raise

    async def async_call(self, fn: Callable[[], Awaitable[T]]) -> T:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self._reset_timeout:
                self._transition(CircuitState.HALF_OPEN)
                self._half_open_attempts = 0
            else:
                raise CircuitOpenError()

        if self._state == CircuitState.HALF_OPEN and self._half_open_attempts >= self._half_open_max_attempts:
            raise CircuitOpenError()

        try:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_attempts += 1

            result = await fn()

            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.CLOSED)
            self._failures = 0
            return result
        except Exception:
            self._failures += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.OPEN)
                if self._on_circuit_open:
                    self._on_circuit_open(self._failures)
            elif self._failures >= self._failure_threshold:
                self._transition(CircuitState.OPEN)
                if self._on_circuit_open:
                    self._on_circuit_open(self._failures)

            raise
