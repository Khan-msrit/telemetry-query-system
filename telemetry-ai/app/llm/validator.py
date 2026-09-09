from app.schema import get_telemetry_columns, get_status_parameters

VALID_COLUMNS = None


def validate_parsed_query(data: dict):
    global VALID_COLUMNS

    if not data:
        return None

    if VALID_COLUMNS is None:
        VALID_COLUMNS = set(get_telemetry_columns()) | set(get_status_parameters())

    params = data.get("parameters")

    if not params or not isinstance(params, list):
        return None

    valid_params = [p for p in params if p in VALID_COLUMNS]

    if not valid_params:
        return None

    data["parameters"] = valid_params

    filters = data.get("filters") or []
    valid_filters = [f for f in filters if f.get("parameter") in VALID_COLUMNS]
    data["filters"] = valid_filters

    return data
