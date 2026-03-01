# Single source of truth for workflow rules

ALLOWED_TRANSITIONS = {
    "released": ["bulk", "exception"],
    "bulk": ["ready", "exception"],
    "ready": ["packed", "exception"],
    "packed": ["shipped", "exception"],
    "shipped": [],
    "exception": ["released"],  # optional, depends on your logic
}

WIP_LIMITS = {
    "released": None,
    "bulk": 6,
    "ready": 8,
    "packed": 5,
    "shipped": None,
    "exception": None,
}
