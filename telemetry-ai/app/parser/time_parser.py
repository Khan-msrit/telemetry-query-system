import re
import pandas as pd
from datetime import timedelta
from app.db import TelemetryDB

_db = TelemetryDB()
_cached_now = None


def _get_reference_now():
    """Uses the latest timestamp actually present in telemetry_numeric as
    the reference 'now' for relative time phrases (e.g. 'last 3 hours').
    This keeps time-window queries meaningful regardless of whether the
    loaded dataset is live data or a fixed historical recording - cached
    per process, so restart the backend after loading a new dataset."""
    global _cached_now
    if _cached_now is None:
        try:
            df = _db.query("SELECT MAX(time) AS max_time FROM telemetry_numeric")
            if not df.empty and pd.notna(df.iloc[0, 0]):
                _cached_now = pd.Timestamp(df.iloc[0, 0]).to_pydatetime()
            else:
                _cached_now = None
        except Exception:
            _cached_now = None
    return _cached_now


def extract_time_range(query: str):
    q = query.lower()
    now = _get_reference_now()
    if now is None:
        return None, None

    # last N minutes / minute
    match = re.search(r"last (\d+) minutes?", q)
    if match:
        minutes = int(match.group(1))
        start = now - timedelta(minutes=minutes)
        return start.isoformat(), now.isoformat()

    # last N hours / hour
    match = re.search(r"last (\d+) hours?", q)
    if match:
        hours = int(match.group(1))
        start = now - timedelta(hours=hours)
        return start.isoformat(), now.isoformat()

    # last N days / day
    match = re.search(r"last (\d+) days?", q)
    if match:
        days = int(match.group(1))
        start = now - timedelta(days=days)
        return start.isoformat(), now.isoformat()

    # yesterday (relative to the reference "now", not the real calendar)
    if "yesterday" in q:
        start = now - timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start.isoformat(), end.isoformat()

    # between dates
    match = re.search(r"between (.+) and (.+)", q)
    if match:
        try:
            from datetime import datetime
            start = datetime.strptime(match.group(1).strip(), "%b %d")
            end = datetime.strptime(match.group(2).strip(), "%b %d")
            start = start.replace(year=now.year)
            end = end.replace(year=now.year)
            return start.isoformat(), end.isoformat()
        except Exception:
            pass

    return None, None