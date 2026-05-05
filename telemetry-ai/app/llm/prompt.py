def build_prompt(user_query: str, candidates=None):

    candidate_text = ""

    if candidates:
        candidate_text = "\nAvailable telemetry parameters:\n"
        for c in candidates:
            candidate_text += f"""
Name: {c.get('parameter')}
Description: {c.get('description', '')}
Subsystem: {c.get('subsystem', '')}
Category: {c.get('category', '')}
---
"""

    return f"""
You are a telemetry query assistant.

Respond ONLY in valid JSON. No explanation. No extra text.

JSON structure:

{{
  "type": "metric | timeseries | compare",
  "aggregation": "avg | min | max | count",
  "parameters": ["COLUMN_NAME"],
  "filters": [
      {{
          "parameter": "COLUMN_NAME",
          "operator": "= | > | < | >= | <=",
          "value": number
      }}
  ]
}}

STRICT RULES:

- Use ONLY parameters from the provided list
- DO NOT invent parameter names
- If user asks for "average" or "avg" → type MUST be "metric"
- If user asks for "max", "min", "count" → type MUST be "metric"
- If user asks for "trend", "over time", "history" → type MUST be "timeseries"
- If user asks to compare → type MUST be "compare"
- If query contains "trend", "over time", "history" → type MUST be "timeseries"

---

EXAMPLES:

User: avg battery voltage
Output:
{{
  "type": "metric",
  "aggregation": "avg",
  "parameters": ["BAT_VOL_M_FINE"],
  "filters": []
}}

User: show battery voltage trend
Output:
{{
  "type": "timeseries",
  "aggregation": "avg",
  "parameters": ["BAT_VOL_M_FINE"],
  "filters": []
}}

User: max battery voltage
Output:
{{
  "type": "metric",
  "aggregation": "max",
  "parameters": ["BAT_VOL_M_FINE"],
  "filters": []
}}

---

{candidate_text}

User Query:
{user_query}
"""
