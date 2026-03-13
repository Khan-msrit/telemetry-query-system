from app.db import TelemetryDB

_db = TelemetryDB()


def get_telemetry_columns():
    sql = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'telemetry'
    """
    df = _db.query(sql)
    return df["column_name"].tolist()
