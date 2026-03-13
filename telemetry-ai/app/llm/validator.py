from app.schema import get_telemetry_columns

VALID_COLUMNS = None


def validate_parsed_query(data: dict):
    global VALID_COLUMNS

    if not data:
        return None

    # Load schema once
    if VALID_COLUMNS is None:
        VALID_COLUMNS = set(get_telemetry_columns())

    params = data.get("parameters")

    # Ensure parameters exist and are iterable
    if not params or not isinstance(params, list):
        return None

    # Keep only valid parameters
    valid_params = [p for p in params if p in VALID_COLUMNS]

    if not valid_params:
        return None

    data["parameters"] = valid_params

    # Validate filters safely
    filters = data.get("filters") or []

    valid_filters = []
    for f in filters:
        param = f.get("parameter")
        if param in VALID_COLUMNS:
            valid_filters.append(f)

    data["filters"] = valid_filters

    return data
