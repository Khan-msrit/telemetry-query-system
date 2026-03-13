from app.parser.rule_parser import parse_rule_based
from app.parser.time_parser import extract_time_range
from app.llm.client import call_llm
from app.llm.prompt import build_prompt
from app.llm.validator import validate_parsed_query
from app.query_builder import QueryBuilder
from app.db import TelemetryDB
from app.visualization import VisualizationRouter
import json


db = TelemetryDB()
qb = QueryBuilder()


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
