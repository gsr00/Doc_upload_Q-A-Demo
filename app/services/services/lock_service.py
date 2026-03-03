import time
from threading import Lock

_LOCKS: dict[str, float] = {}
_MUTEX = Lock()

def acquire(key: str, ttl_seconds: int = 60) -> bool:
    """True if lock acquired; False if already held (and not expired)."""
    now = time.time()
    with _MUTEX:
        expires_at = _LOCKS.get(key)
        if expires_at is not None and expires_at <= now:
            _LOCKS.pop(key, None)

        if key in _LOCKS:
            return False

        _LOCKS[key] = now + ttl_seconds
        return True

def release(key: str) -> None:
    """Release lock (safe if missing)."""
    with _MUTEX:
        _LOCKS.pop(key, None)