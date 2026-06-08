from __future__ import annotations

from functools import wraps
from time import time


def audit_action(action_name: str | None = None):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            result = function(self, *args, **kwargs)
            audit_log = getattr(self, "audit_log", None)
            if isinstance(audit_log, list):
                audit_log.append(
                    {
                        "action": action_name or function.__name__,
                        "time": f"{time():.3f}",
                    }
                )
            return result

        return wrapper

    return decorator