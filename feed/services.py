import os
import time
from typing import Iterable, Optional, Tuple

from django_redis import get_redis_connection
from django.conf import settings


FEED_ZSET_KEY = "feed:global"


def now_epoch_ms() -> int:
    """
    Returns the current time in milliseconds
    """
    return int(time.time() * 1000)


def calculate_score(base_epoch_ms: Optional[int] = None, bonus: int = 0) -> float:
    """
    Calculates the score for a feed item
    """
    base = base_epoch_ms if base_epoch_ms is not None else now_epoch_ms()
    return float(base + bonus)


def redis_conn():
    """
    Returns the Redis connection
    """
    try:
        return get_redis_connection("default")
    except Exception:
        return None


def zadd_feed(item_id: int, score: float) -> None:
    """
    Adds an item to the feed
    """
    r = redis_conn()
    if not r:
        return
    r.zadd(FEED_ZSET_KEY, {item_id: score})


def zrem_feed(item_id: int) -> None:
    """
    Removes an item from the feed
    """
    r = redis_conn()
    if not r:
        return
    r.zrem(FEED_ZSET_KEY, item_id)


def zpage_by_cursor(limit: int, cursor: Optional[str]) -> Tuple[Iterable[int], Optional[str]]:
    """
    Returns (ids, next_cursor) from newest to oldest using score as ordering.
    Cursor format: "{score}:{id}". If no cursor, start from +inf.
    """
    r = redis_conn()
    if not r:
        return [], None

    if cursor:
        try:
            score_str, id_str = cursor.split(":", 1)
            # exclusive upper bound to avoid duplicate last item
            max_score = f"({float(score_str)}"
        except Exception:
            max_score = "+inf"
    else:
        max_score = "+inf"

    # Using BYSCORE with REV order (Redis >= 6.2). start/end are min/max in BYSCORE mode.
    ids = r.zrange(
        FEED_ZSET_KEY,
        start="-inf",
        end=max_score,
        desc=True,
        byscore=True,
        offset=0,
        num=limit,
    )
    ids = [int(x) for x in ids]
    if not ids:
        return [], None

    # next cursor based on last item's score
    last_score = r.zscore(FEED_ZSET_KEY, ids[-1])
    next_cursor = f"{last_score}:{ids[-1]}"
    return ids, next_cursor


