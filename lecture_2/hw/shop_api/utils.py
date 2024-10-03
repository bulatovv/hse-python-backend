from typing import Any, OrderedDict

def get_last_key(od: OrderedDict, default: Any) -> Any:
    return next(reversed(od), default)
