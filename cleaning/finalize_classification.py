"""
Finalizes column classification: folds the "still_uncertain" hex/checksum/
sync-word columns into status_columns (safe default - preserves the raw
value as text, never fabricates a misleading number).

Usage:
    python3 finalize_classification.py final_classification.json
"""

import sys
import json


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 finalize_classification.py final_classification.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    uncertain_cols = [item["column"] for item in data.get("still_uncertain", [])]

    numeric_columns = sorted(data["numeric_columns"])
    status_columns = sorted(set(data["status_columns"]) | set(uncertain_cols))

    result = {
        "total_rows": data["total_rows"],
        "numeric_columns": numeric_columns,
        "status_columns": status_columns,
        "empty_columns": data["empty_columns"],
    }

    with open("load_classification.json", "w") as f:
        json.dump(result, f, indent=2)

    total_classified = len(numeric_columns) + len(status_columns) + len(result["empty_columns"])

    print(f"Numeric columns: {len(numeric_columns)}")
    print(f"Status columns:  {len(status_columns)}  (includes {len(uncertain_cols)} reclassified hex/checksum words)")
    print(f"Empty columns (excluded): {len(result['empty_columns'])}")
    print(f"Total accounted for: {total_classified}")
    print()
    print("Written to load_classification.json - this is the file the loader script will use.")


if __name__ == "__main__":
    main()
