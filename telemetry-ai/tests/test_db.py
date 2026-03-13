from app.db import TelemetryDB

db = TelemetryDB()

df = db.query('SELECT COUNT(*) FROM "telemetry"')
print(df)

df2 = db.query('SELECT "BUS_VOL", time FROM "telemetry" LIMIT 5')
print(df2)

from app.query_builder import QueryBuilder

print("\nMetric test:")
sql = QueryBuilder.metric("BUS_VOL", "avg")
print(sql)
print(db.query(sql))

print("\nTimeseries test:")
sql = QueryBuilder.timeseries("BUS_VOL", limit=5)
print(sql)
print(db.query(sql))

print("\nMulti-series test:")
sql = QueryBuilder.multi_timeseries(["BUS_VOL", "BAT_VOL_M_FINE"], limit=5)
print(sql)
print(db.query(sql))

from app.visualization import VisualizationRouter

print("\nVisualization test:")

df_metric = db.query(QueryBuilder.metric("BUS_VOL", "avg"))
print(VisualizationRouter.build_response(df_metric))

df_ts = db.query(QueryBuilder.timeseries("BUS_VOL", limit=5))
print(VisualizationRouter.build_response(df_ts))

df_multi = db.query(QueryBuilder.multi_timeseries(["BUS_VOL", "BAT_VOL_M_FINE"], limit=5))
print(VisualizationRouter.build_response(df_multi))
