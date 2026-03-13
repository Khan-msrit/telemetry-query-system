from typing import List, Dict


class QueryBuilder:

    @staticmethod
    def _build_where(start=None, end=None, filters: List[Dict] = None):
        clauses = []

        # Time range
        if start and end:
            clauses.append(f"time >= '{start}' AND time <= '{end}'")

        # Semantic filters
        if filters:
            for f in filters:
                param = f["parameter"]
                op = f["operator"]
                val = f["value"]

                if isinstance(val, str):
                    val = f"'{val}'"

                clauses.append(f'"{param}" {op} {val}')

        if not clauses:
            return ""

        return " WHERE " + " AND ".join(clauses)

    @staticmethod
    def metric(parameter, agg, start=None, end=None, filters=None):
        if agg.lower() not in ["avg", "min", "max", "count"]:
            raise ValueError("Unsupported aggregation")

        sql = f'SELECT {agg.upper()}("{parameter}") FROM "telemetry"'
        sql += QueryBuilder._build_where(start, end, filters)
        return sql

    @staticmethod
    def timeseries(parameter, start=None, end=None, limit=1000, filters=None):
        sql = f'SELECT "{parameter}", time FROM "telemetry"'
        sql += QueryBuilder._build_where(start, end, filters)
        sql += f' ORDER BY time ASC LIMIT {limit}'
        return sql

    @staticmethod
    def multi_timeseries(parameters, start=None, end=None, limit=1000, filters=None):
        cols = ", ".join(f'"{p}"' for p in parameters)
        sql = f'SELECT {cols}, time FROM "telemetry"'
        sql += QueryBuilder._build_where(start, end, filters)
        sql += f' ORDER BY time ASC LIMIT {limit}'
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
                parameter=params[0],
                agg=agg,
                start=start,
                end=end,
                filters=filters,
            )

        if query_type == "timeseries":
            return QueryBuilder.timeseries(
                parameter=params[0],
                start=start,
                end=end,
                filters=filters,
            )

        if query_type == "compare":
            return QueryBuilder.multi_timeseries(
                parameters=params,
                start=start,
                end=end,
                filters=filters,
            )

        raise ValueError("Unknown query type")
