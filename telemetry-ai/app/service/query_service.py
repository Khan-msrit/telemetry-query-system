from app.parser.rule_parser import parse_rule_based
from app.parser.time_parser import extract_time_range
from app.llm.client import call_llm
from app.llm.prompt import build_prompt
from app.llm.validator import validate_parsed_query
from app.query_builder import QueryBuilder
from app.db import TelemetryDB
from app.visualization import VisualizationRouter
from rag.parameter_search import search_parameter
from app.schema import get_telemetry_columns, get_status_parameters
from app.service.parameter_mapper import map_parameters, map_parameter
import json


db = TelemetryDB()
qb = QueryBuilder()

TELEMETRY_COLUMNS = get_telemetry_columns()       # numeric parameters
STATUS_COLUMNS = get_status_parameters()           # status/text parameters
ALL_COLUMNS = list(set(TELEMETRY_COLUMNS) | set(STATUS_COLUMNS))

STATUS_HISTORY_KEYWORDS = ["history", "log", "changes", "trend", "over time"]


def resolve_parameter(query: str):
    q = query.lower().strip()

    for col in ALL_COLUMNS:
        if col.lower() in q:
            return {"resolved_query": query, "candidates": []}

    try:
        results = search_parameter(query, top_k=5)
        if not results:
            return {"resolved_query": query, "candidates": []}
        best = results[0]
        if best["score"] > 0.75:
            return {"resolved_query": query, "candidates": [best]}
        return {"resolved_query": query, "candidates": results}
    except Exception:
        return {"resolved_query": query, "candidates": []}


def parse_query(query: str, candidates=None):
    rule_result = parse_rule_based(query)

    if rule_result:
        rule_result["parameters"] = map_parameters(rule_result.get("parameters", []), ALL_COLUMNS)
        validated = validate_parsed_query(rule_result)
        if validated:
            print("RULE PARSER SUCCESS AFTER MAPPING:", validated)
            return validated

    print("RULE PARSER FAILED → FALLING BACK TO LLM")

    for attempt in range(2):
        prompt = build_prompt(query, candidates)
        if attempt == 1:
            prompt += "\n\nIMPORTANT: Your previous response was invalid. Return ONLY valid JSON."

        print(f"\n=== PROMPT (attempt {attempt+1}) ===\n", prompt)
        llm_output = call_llm(prompt)
        print(f"\n=== LLM OUTPUT (attempt {attempt+1}) ===\n", llm_output)

        if not llm_output:
            continue
        try:
            parsed = json.loads(llm_output)
        except Exception as e:
            print("JSON PARSE ERROR:", e)
            continue

        validated = validate_parsed_query(parsed)
        if validated:
            print("\n=== VALIDATED ===\n", validated)
            return validated

    print("LLM FAILED AFTER RETRY")
    return None


def execute_nl_query(query: str):
    resolved = resolve_parameter(query)
    if not isinstance(resolved, dict):
        return {"error": "Parameter resolution failed"}

    query = resolved.get("resolved_query", query)
    candidates = resolved.get("candidates", [])

    parsed = parse_query(query, candidates)

    if not parsed:
        return {
            "type": "error",
            "message": "Could not understand query",
            "suggestions": [
                "avg battery voltage",
                "show battery voltage trend",
                "max battery voltage"
            ]
        }

    query_lower = query.lower()

    parsed["parameters"] = map_parameters(parsed.get("parameters", []), ALL_COLUMNS)

    # ---- Status override: if any resolved parameter is a status/enum
    # parameter, this MUST be a status query - aggregation/trend/compare
    # don't apply to text values like "ON" or "5E0F". ----
    status_params = [p for p in parsed["parameters"] if p in STATUS_COLUMNS]

    if status_params:
        parsed["type"] = "status"
        parsed["parameters"] = [status_params[0]]  # one status parameter per query, for now
        parsed["status_limit"] = 20 if any(k in query_lower for k in STATUS_HISTORY_KEYWORDS) else 1
    elif len(parsed.get("parameters", [])) > 1:
        parsed["type"] = "compare"

    print("TYPE (post-check):", parsed.get("type"), "| params:", parsed.get("parameters"))

    try:
        if parsed.get("filters"):
            parsed["filters"] = [f for f in parsed["filters"] if f.get("parameter", "").lower() != "time"]
            for f in parsed["filters"]:
                f["parameter"] = map_parameter(f["parameter"], ALL_COLUMNS)

        start, end = extract_time_range(query)
        if start and end:
            parsed["start_time"] = start
            parsed["end_time"] = end

        sql = qb.build(parsed)
        df = db.query(sql)

        return VisualizationRouter.build_response(df, parsed["type"], parsed.get("parameters"))

    except Exception as e:
        return {"error": str(e)}
