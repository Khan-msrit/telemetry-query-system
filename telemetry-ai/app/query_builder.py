from typing import List, Dict


class QueryBuilder:

    @staticmethod
    def _build_where(parameter=None, parameters=None, start=None, end=None, filters=None):
        clauses = []

        if parameter:
            clauses.append(f"parameter = '{parameter}'")
        elif parameters:
            in_list = ", ".join(f"'{p}'" for p in parameters)
            clauses.append(f"parameter IN ({in_list})")

        if start and end:
            clauses.append(f"time >= '{start}' AND time <= '{end}'")

        # Value-threshold filters (e.g. "voltage > 5"). Only supports
        # filtering on the SAME parameter being queried - a filter on a
        # different parameter would need a join across two series at
        # matching timestamps, which isn't implemented.
        if filters:
            for f in filters:
                if parameter and f["parameter"] != parameter:
                    continue
                op = f["operator"]
                val = f["value"]
                clauses.append(f"value {op} {val}")

        return " WHERE " + " AND ".join(clauses) if clauses else ""

    @staticmethod
    def metric(parameter, agg, start=None, end=None, filters=None):
        if agg.lower() not in ["avg", "min", "max", "count"]:
            raise ValueError("Unsupported aggregation")
        sql = f'SELECT {agg.upper()}(value) AS agg_value FROM telemetry_numeric'
        sql += QueryBuilder._build_where(parameter=parameter, start=start, end=end, filters=filters)
        return sql

    @staticmethod
    def timeseries(parameter, start=None, end=None, limit=1000, filters=None):
        sql = 'SELECT time, value FROM telemetry_numeric'
        sql += QueryBuilder._build_where(parameter=parameter, start=start, end=end, filters=filters)
        sql += f' ORDER BY time ASC LIMIT {limit}'
        return sql

    @staticmethod
    def multi_timeseries(parameters, start=None, end=None, limit=1000, filters=None):
        sql = 'SELECT time, parameter, value FROM telemetry_numeric'
        sql += QueryBuilder._build_where(parameters=parameters, start=start, end=end, filters=filters)
        sql += f' ORDER BY time ASC LIMIT {limit * max(len(parameters), 1)}'
        return sql

    @staticmethod
    def status(parameter, start=None, end=None, limit=1):
        sql = f"SELECT time, value FROM telemetry_status WHERE parameter = '{parameter}'"
        if start and end:
            sql += f" AND time >= '{start}' AND time <= '{end}'"
        sql += f" ORDER BY time DESC LIMIT {limit}"
        return sql

    @staticmethod
    def build(parsed: dict):
        query_type = parsed["type"]
        params = parsed["parameters"]
        start = parsed.get("start_time")
        end = parsed.get("end_time")
        filters = parsed.get("filters")

        if query_type == "metric":
            agg = parsed.get("aggregation", "avg")
            return QueryBuilder.metric(
                parameter=params[0], agg=agg, start=start, end=end, filters=filters,
            )
        if query_type == "timeseries":
            return QueryBuilder.timeseries(
                parameter=params[0], start=start, end=end, filters=filters,
            )
        if query_type == "compare":
            return QueryBuilder.multi_timeseries(
                parameters=params, start=start, end=end, filters=filters,
            )
        if query_type == "status":
            limit = parsed.get("status_limit", 1)
            return QueryBuilder.status(
                parameter=params[0], start=start, end=end, limit=limit,
            )
        raise ValueError("Unknown query type")
