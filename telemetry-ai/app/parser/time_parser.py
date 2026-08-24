import re
from datetime import datetime, timedelta


def extract_time_range(query: str):
    q = query.lower()

    now = datetime(2026, 2, 28, 23, 59, 0)
    #now = datetime.utcnow()

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

    # yesterday
    if "yesterday" in q:
        start = now - timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start.isoformat(), end.isoformat()

    # between dates
    match = re.search(r"between (.+) and (.+)", q)
    if match:
        try:
            start = datetime.strptime(match.group(1).strip(), "%b %d")
            end = datetime.strptime(match.group(2).strip(), "%b %d")

            start = start.replace(year=now.year)
            end = end.replace(year=now.year)

            return start.isoformat(), end.isoformat()
        except:
            pass

    return None, None
