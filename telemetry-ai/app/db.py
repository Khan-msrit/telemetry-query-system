from influxdb_client_3 import InfluxDBClient3
import pandas as pd
from app.config import settings


class TelemetryDB:
    def __init__(self):
        self.client = InfluxDBClient3(
            host=settings.INFLUX_HOST,
            token=settings.INFLUX_TOKEN,
            database=settings.INFLUX_DATABASE,
        )

    def query(self, sql: str) -> pd.DataFrame:
        if not sql.lower().strip().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        try:
            result = self.client.query(sql)
            return result.to_pandas()
        except Exception as e:
            raise RuntimeError(f"Query failed: {e}")
