from typing import Optional, Iterable, Tuple, List
from django_redis import get_redis_connection


def redis_conn():
    """
    Returns the Redis connection
    """
    try:
        return get_redis_connection("default")
    except Exception:
        return None


def unread_cache_key(user_id: int) -> str:
    """
    Returns the unread cache key
    """
    return f"notif:unread:{user_id}"


def incr_unread(user_id: int, by: int = 1) -> None:
    """
    Increments the unread count
    """
    r = redis_conn()
    if not r:
        return
    r.incrby(unread_cache_key(user_id), by)


def decr_unread(user_id: int, by: int = 1) -> None:
    """
    Decrements the unread count
    """
    r = redis_conn()
    if not r:
        return
    r.decrby(unread_cache_key(user_id), by)


def get_unread(user_id: int) -> int:
    """
    Returns the unread count
    """
    r = redis_conn()
    if not r:
        return 0
    val = r.get(unread_cache_key(user_id))
    try:
        return int(val) if val is not None else 0
    except Exception:
        return 0
