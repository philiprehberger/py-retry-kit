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
