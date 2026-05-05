from typing import List
from rag.parameter_search import search_parameter


CONFIDENCE_THRESHOLD = 0.6


def map_parameter(param: str, valid_columns: List[str]) -> str:
    """
    Maps a parameter to the closest valid telemetry column.
    Uses FAISS semantic search as fallback.
    """

    if not param:
        return param

    p = param.strip()

    # ✅ Step 1: Exact match
    if p in valid_columns:
        return p

    # ✅ Step 2: Case-insensitive match
    for col in valid_columns:
        if col.lower() == p.lower():
            return col

    # ✅ Step 3: Semantic mapping using FAISS
    try:
        results = search_parameter(p, top_k=1)

        if results:
            best = results[0]

            if best["score"] >= CONFIDENCE_THRESHOLD:
                return best["parameter"]

    except Exception:
        pass

    # ⚠️ Soft fallback: return original (will be caught later if invalid)
    return p


def map_parameters(params: List[str], valid_columns: List[str]) -> List[str]:
    return [map_parameter(p, valid_columns) for p in params]
