"""
Profiles a large telemetry CSV column-by-column WITHOUT loading the whole
file into memory. Classifies every column as:
  - numeric   (every non-null value parses as a number)
  - status    (every non-null value is non-numeric text)
  - empty     (no non-null values anywhere in the file)
  - ambiguous (mix of numeric and non-numeric values - needs a decision)

Also checks the Timestamp column for parse errors and ordering.

Usage:
    python3 profile_columns.py /path/to/full_telemetry.csv
"""

import sys
import json
import pandas as pd

CHUNK_SIZE = 2000
TIMESTAMP_COL = "Timestamp"
TIMESTAMP_FORMAT = "%d-%b-%Y %H:%M:%S.%f"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 profile_columns.py /path/to/full_telemetry.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    stats = {}
    columns = None
    total_rows = 0

    ts_parse_failures = 0
    ts_out_of_order = 0
    prev_ts = None

    reader = pd.read_csv(csv_path, dtype=str, chunksize=CHUNK_SIZE)

    for chunk_idx, chunk in enumerate(reader):
        if columns is None:
            columns = [c for c in chunk.columns if c != TIMESTAMP_COL]
            for c in columns:
                stats[c] = {
                    "total": 0,
                    "null": 0,
                    "numeric": 0,
                    "non_numeric": 0,
                    "sample_non_numeric": [],
                }

        total_rows += len(chunk)

        # ---- Timestamp checks ----
        parsed = pd.to_datetime(chunk[TIMESTAMP_COL], format=TIMESTAMP_FORMAT, errors="coerce")
        ts_parse_failures += parsed.isna().sum()
        parsed_valid = parsed.dropna().tolist()
        for ts in parsed_valid:
            if prev_ts is not None and ts < prev_ts:
                ts_out_of_order += 1
            prev_ts = ts

        # ---- Column classification (vectorized) ----
        for c in columns:
            col = chunk[c]
            stripped = col.str.strip()
            null_mask = col.isna() | (stripped == "")
            non_null = stripped[~null_mask]

            s = stats[c]
            s["total"] += len(col)
            s["null"] += int(null_mask.sum())

            if len(non_null) == 0:
                continue

            numeric_coerced = pd.to_numeric(non_null, errors="coerce")
            numeric_count = int(numeric_coerced.notna().sum())
            non_numeric_count = len(non_null) - numeric_count

            s["numeric"] += numeric_count
            s["non_numeric"] += non_numeric_count

            if non_numeric_count > 0 and len(s["sample_non_numeric"]) < 5:
                bad_vals = non_null[numeric_coerced.isna()].unique().tolist()
                for v in bad_vals:
                    if len(s["sample_non_numeric"]) >= 5:
                        break
                    if v not in s["sample_non_numeric"]:
                        s["sample_non_numeric"].append(v)

        print(f"Processed {total_rows} rows...", end="\r", flush=True)

    print()

    numeric_cols, status_cols, empty_cols, ambiguous_cols = [], [], [], []

    for c, s in stats.items():
        non_null = s["total"] - s["null"]
        if non_null == 0:
            empty_cols.append(c)
        elif s["non_numeric"] == 0:
            numeric_cols.append(c)
        elif s["numeric"] == 0:
            status_cols.append(c)
        else:
            ambiguous_cols.append(c)

    result = {
        "total_rows": total_rows,
        "total_columns": len(columns),
        "numeric_columns": numeric_cols,
        "status_columns": status_cols,
        "empty_columns": empty_cols,
        "ambiguous_columns": ambiguous_cols,
        "ambiguous_details": {
            c: stats[c]["sample_non_numeric"] for c in ambiguous_cols
        },
        "timestamp_parse_failures": int(ts_parse_failures),
        "timestamp_out_of_order_count": ts_out_of_order,
    }

    with open("column_profile.json", "w") as f:
        json.dump(result, f, indent=2)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total rows:                {total_rows}")
    print(f"Total columns (excl time): {len(columns)}")
    print(f"Numeric columns:           {len(numeric_cols)}")
    print(f"Status/text columns:       {len(status_cols)}")
    print(f"Fully empty columns:       {len(empty_cols)}")
    print(f"Ambiguous (mixed) columns: {len(ambiguous_cols)}")
    print(f"Timestamp parse failures:  {ts_parse_failures}")
    print(f"Timestamp out-of-order:    {ts_out_of_order}")
    print()
    if ambiguous_cols:
        print("First 10 ambiguous columns and a few bad values each:")
        for c in ambiguous_cols[:10]:
            print(f"  {c}: {stats[c]['sample_non_numeric']}")
    print()
    print("Full details written to column_profile.json")


if __name__ == "__main__":
    main()
