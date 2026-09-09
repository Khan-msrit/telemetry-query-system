import re


AGG_MAP = {
    "average": "avg",
    "avg": "avg",
    "maximum": "max",
    "max": "max",
    "minimum": "min",
    "min": "min",
    "count": "count",
}


COMPARISON_MAP = {
    "greater than": ">",
    "above": ">",
    "less than": "<",
    "below": "<",
    "equal to": "=",
}

# Trailing phrases that indicate "everything from here on is a time/filter
# clause, not part of the parameter name" - shared by every branch below so
# a fix here never has to be duplicated per-branch again.
_TRAILING_MARKERS = [" last ", " yesterday", " today", " between ", " above ", " below "]


def _strip_trailing_clause(text: str) -> str:
    text = text.strip()
    for marker in _TRAILING_MARKERS:
        if marker in text:
            text = text.split(marker)[0].strip()
    return text


def extract_filters(q: str):
    filters = []

    for phrase, op in COMPARISON_MAP.items():
        pattern = rf"(\w+)\s+{phrase}\s+(\d+)"
        matches = re.findall(pattern, q)

        for match in matches:
            param = match[0].upper()
            value = int(match[1])

            filters.append({
                "parameter": param,
                "operator": op,
                "value": value
            })

    return filters


def parse_rule_based(query: str):
    q = query.lower()

    filters = extract_filters(q)

    # ---- METRIC DETECTION ----
    for key in AGG_MAP:
        if key in q:
            words = q.split()

            for i, w in enumerate(words):
                if w == key and i + 1 < len(words):
                    param = _strip_trailing_clause(" ".join(words[i + 1:])).upper()

                    return {
                        "type": "metric",
                        "parameters": [param],
                        "aggregation": AGG_MAP[key],
                        "filters": filters if filters else None
                    }

    # ---- COMPARE DETECTION ----
    if "compare" in q and "and" in q:
        parts = q.split("compare")[1].strip()
        raw_params = parts.split(" and ")

        params = [_strip_trailing_clause(p).upper() for p in raw_params]
        params = [p for p in params if p]  # drop anything that stripped to empty

        return {
            "type": "compare",
            "parameters": params,
            "filters": filters if filters else None
        }

    # ---- TIMESERIES / MULTI PARAMETER SHOW ----
    if "show" in q:

        remainder = q.split("show", 1)[1].strip()
        remainder = _strip_trailing_clause(remainder)

        # multi-parameter query
        if " and " in remainder:

            params = [
                p.strip().upper()
                for p in remainder.split(" and ")
                if p.strip()
            ]

            return {
                "type": "compare",
                "parameters": params,
                "filters": filters if filters else None
            }

        # single parameter query
        param = remainder.strip().upper()

        return {
            "type": "timeseries",
            "parameters": [param],
            "filters": filters if filters else None
        }

    return None
