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
                    param = words[i + 1].upper()

                    return {
                        "type": "metric",
                        "parameters": [param],
                        "aggregation": AGG_MAP[key],
                        "filters": filters if filters else None
                    }

    # ---- COMPARE DETECTION ----
    if "compare" in q and "and" in q:
        parts = q.split("compare")[1].strip()
        params = parts.split("and")

        return {
            "type": "compare",
            "parameters": [p.strip().upper() for p in params],
            "filters": filters if filters else None
        }

    # ---- TIMESERIES ----
    if "show" in q:
        words = q.split()

        for i, w in enumerate(words):
            if w == "show" and i + 1 < len(words):

                return {
                    "type": "timeseries",
                    "parameters": [words[i + 1].upper()],
                    "filters": filters if filters else None
                }

    return None
