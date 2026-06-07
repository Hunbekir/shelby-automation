"""
utils/post_history.py
---------------------
Persistent log of every post and reply AI Shelby creates.

Lives next to config.json (same volume) so it survives redeploys. Provides
the data backing the dashboard's /history view — gives Shelby visibility
into exactly what the bot has been doing in her name, without having to
scroll the Skool community manually.

This log is for human auditing only; the duplicate-reply guard uses
replied_store.py for its own dedup state.
"""

import json
import logging
import os
from datetime import datetime, timezone
from threading import Lock

logger = logging.getLogger(__name__)


def _default_path() -> str:
    """Place the history file beside config.json so it shares the volume."""
    cfg = os.environ.get("CONFIG_PATH")
    base = (
        os.path.dirname(cfg)
        if cfg
        else os.path.dirname(os.path.dirname(__file__))
    )
    return os.path.join(base, "post_history.json")


HISTORY_PATH = os.environ.get("POST_HISTORY_PATH") or _default_path()

# Bounded log — keep the most recent N entries. At one daily post + ~20 hourly
# reply runs/day, this is many weeks of activity.
MAX_ENTRIES = 500

_lock = Lock()


def _read() -> list:
    """Reads the history list. Returns [] if missing/unreadable."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        logger.warning("post_history.json unreadable — treating as empty.")
        return []


def _write(entries: list) -> None:
    """Writes the list back, trimmed to MAX_ENTRIES newest."""
    parent = os.path.dirname(HISTORY_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries[-MAX_ENTRIES:], f, indent=2, ensure_ascii=False)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record_post(*, title: str, content: str, post_id: str | None, url: str | None) -> None:
    """Records a successful top-level post (daily post / weekly event)."""
    entry = {
        "type": "post",
        "timestamp": _now_iso(),
        "title": title,
        "content": content,
        "post_id": post_id,
        "url": url,
    }
    with _lock:
        entries = _read()
        entries.append(entry)
        _write(entries)
    logger.info(f"[POST_HISTORY] Recorded post {post_id}")


def record_reply(
    *,
    content: str,
    root_id: str,
    parent_id: str,
    reply_id: str | None,
    url: str | None,
) -> None:
    """Records a successful comment reply."""
    entry = {
        "type": "reply",
        "timestamp": _now_iso(),
        "content": content,
        "root_id": root_id,
        "parent_id": parent_id,
        "reply_id": reply_id,
        "url": url,
    }
    with _lock:
        entries = _read()
        entries.append(entry)
        _write(entries)
    logger.info(f"[POST_HISTORY] Recorded reply {reply_id} (parent={parent_id})")


def read_all() -> list:
    """Returns all entries in chronological order (oldest first)."""
    with _lock:
        return _read()


def clear() -> int:
    """Wipes the history. Returns how many entries were removed."""
    with _lock:
        existing = _read()
        count = len(existing)
        _write([])
    logger.info(f"[POST_HISTORY] Cleared {count} entries")
    return count
