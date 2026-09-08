from app.db import TelemetryDB

_db = TelemetryDB()


def get_telemetry_columns():
    sql = """
    SELECT DISTINCT parameter
    FROM telemetry_numeric
    """
    df = _db.query(sql)
    return df["parameter"].tolist()


def get_status_parameters():
    """Parameters whose values are status/enum strings, not numeric."""
    sql = """
    SELECT DISTINCT parameter
    FROM telemetry_status
    """
    df = _db.query(sql)
    return df["parameter"].tolist()
