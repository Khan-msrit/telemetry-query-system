from app.parser.rule_parser import parse_rule_based
from app.parser.time_parser import extract_time_range
from app.llm.client import call_llm
from app.llm.prompt import build_prompt
from app.llm.validator import validate_parsed_query
from app.query_builder import QueryBuilder
from app.db import TelemetryDB
from app.visualization import VisualizationRouter
from rag.parameter_search import search_parameter
from app.schema import get_telemetry_columns
import json


db = TelemetryDB()
qb = QueryBuilder()

TELEMETRY_COLUMNS = get_telemetry_columns()

def resolve_parameter(query: str):

    q = query.lower()

    # 1️⃣ Exact match first
    for col in TELEMETRY_COLUMNS:
        if col.lower() in q:
            return query

    # 2️⃣ Remove common keywords
    cleaned = (
        q.replace("show", "")
        .replace("average", "")
        .replace("max", "")
        .replace("min", "")
        .strip()
    )

    try:
        # 3️⃣ Semantic search
        best_param = search_parameter(cleaned)

        # 4️⃣ Validate parameter exists in schema
        if best_param in TELEMETRY_COLUMNS:
            return query.replace(cleaned, best_param)

    except Exception:
        pass

    return query

def parse_query(query: str):

    # ---- Rule-based first ----
    rule_result = parse_rule_based(query)

    if rule_result:
        return validate_parsed_query(rule_result)

    # ---- LLM fallback ----
    prompt = build_prompt(query)
    llm_output = call_llm(prompt)

    if not llm_output:
        return None

    try:
        parsed = json.loads(llm_output)
    except Exception:
        return None

    return validate_parsed_query(parsed)


def execute_nl_query(query: str):

    query = resolve_parameter(query)
    parsed = parse_query(query)

    if not parsed:
        return {"error": "Unable to parse query"}

    try:

        # ---- Extract time range ----
        start, end = extract_time_range(query)

        if start and end:
            parsed["start_time"] = start
            parsed["end_time"] = end

        # ---- Build SQL ----
        sql = qb.build(parsed)

        # ---- Execute ----
        df = db.query(sql)

        # ---- Format output ----
        return VisualizationRouter.build_response(df)

    except Exception as e:
        return {"error": str(e)}
