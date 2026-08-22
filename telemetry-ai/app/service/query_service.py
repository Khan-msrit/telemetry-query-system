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
from app.service.parameter_mapper import map_parameters, map_parameter
import json


db = TelemetryDB()
qb = QueryBuilder()

TELEMETRY_COLUMNS = get_telemetry_columns()

def resolve_parameter(query: str):

    q = query.lower().strip()

    # Step 1: direct column match
    for col in TELEMETRY_COLUMNS:
        if col.lower() in q:
            return {
                "resolved_query": query,
                "candidates": []
            }

    # Step 2: semantic search
    try:
        results = search_parameter(query, top_k=5)

        if not results:
            return {
                "resolved_query": query,
                "candidates": []
            }

        best = results[0]

        # High confidence → still pass as candidate (DO NOT replace string)
        if best["score"] > 0.75:
            return {
                "resolved_query": query,
                "candidates": [best]
            }

        # Medium/low → pass all candidates
        return {
            "resolved_query": query,
            "candidates": results
        }

    except Exception:
        return {
            "resolved_query": query,
            "candidates": []
        }


def parse_query(query: str, candidates=None):

    # ---- Rule-based first ----
    rule_result = parse_rule_based(query)

    if rule_result:
        rule_result["parameters"] = map_parameters(
            rule_result.get("parameters", []),
            TELEMETRY_COLUMNS
        )

        validated = validate_parsed_query(rule_result)

        if validated:
            print("RULE PARSER SUCCESS AFTER MAPPING:", validated)
            return validated

    print("RULE PARSER FAILED → FALLING BACK TO LLM")

    # ---- LLM fallback with retry ----
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

#def parse_query(query: str, candidates=None):
#
#    # ---- Rule-based first ----
#    rule_result = parse_rule_based(query)
#
#    if rule_result:
#        return validate_parsed_query(rule_result)
#
#    # ---- LLM fallback ----
#    prompt = build_prompt(query, candidates)
#    llm_output = call_llm(prompt)
#
#    if not llm_output:
#        return None
#
#    try:
#        parsed = json.loads(llm_output)
#    except Exception:
#        return None
#
#    return validate_parsed_query(parsed)

def execute_nl_query(query: str):

    resolved = resolve_parameter(query)

    if not isinstance(resolved, dict):
        return {"error": "Parameter resolution failed"}

    query = resolved.get("resolved_query", query)
    candidates = resolved.get("candidates", [])

    parsed = parse_query(query, candidates)

    # 🔥 FIRST check this
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

    # 🔥 NEW: detect multiple parameters
    has_multiple_params = len(parsed.get("parameters", [])) > 1

    is_timeseries = any(word in query_lower for word in ["trend", "over time", "history"])
    is_compare = "compare" in query_lower or has_multiple_params

    print("BEFORE CORRECTION:", parsed)

    # 🔥 PRIORITY ORDER

    if len(parsed.get("parameters", [])) > 1:
        parsed["type"] = "compare"

    elif is_timeseries:
        parsed["type"] = "timeseries"

    elif parsed.get("aggregation") in ["avg", "min", "max", "count"]:
        parsed["type"] = "metric"

    print("AFTER CORRECTION:", parsed)

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

    try:
        # ✅ NEW: Parameter grounding
        parsed["parameters"] = map_parameters(
            parsed.get("parameters", []),
            TELEMETRY_COLUMNS
        )

        # Optional: also map filter parameters
        if parsed.get("filters"):
            for f in parsed["filters"]:
                f["parameter"] = map_parameter(
                    f["parameter"],
                    TELEMETRY_COLUMNS
                )

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
        return VisualizationRouter.build_response(df, parsed["type"], parsed.get("parameters"))

    except Exception as e:
        return {"error": str(e)}
