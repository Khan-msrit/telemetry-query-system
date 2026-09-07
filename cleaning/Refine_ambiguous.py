"""
Re-scans only the "ambiguous" columns identified by profile_columns.py to
decide whether each one is really numeric (with a few junk/sentinel values
to drop) or really a status/hex code column (where a few values just
coincidentally look like decimal numbers).

Usage:
    python3 refine_ambiguous.py /path/to/full_telemetry.csv column_profile.json
"""

import sys
import json
import pandas as pd

CHUNK_SIZE = 2000

# If >= this fraction of a column's non-null values are numeric, treat the
# whole column as numeric (junk values become null/dropped at load time).
NUMERIC_THRESHOLD = 0.95

# If <= this fraction is numeric, treat the whole column as status/text
# (the rare numeric-looking values are just kept as text, no data loss).
STATUS_THRESHOLD = 0.05


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 refine_ambiguous.py /path/to/full_telemetry.csv column_profile.json")
        sys.exit(1)

    csv_path = sys.argv[1]
    profile_path = sys.argv[2]

    with open(profile_path) as f:
        profile = json.load(f)

    ambiguous_cols = profile["ambiguous_columns"]
    print(f"Re-scanning {len(ambiguous_cols)} ambiguous columns...")

    counts = {c: {"numeric": 0, "non_numeric": 0} for c in ambiguous_cols}

    reader = pd.read_csv(
        csv_path,
        dtype=str,
        usecols=ambiguous_cols,
        chunksize=CHUNK_SIZE,
    )

    rows_done = 0
    for chunk in reader:
        rows_done += len(chunk)
        for c in ambiguous_cols:
            col = chunk[c]
            stripped = col.str.strip()
            non_null = stripped[~(col.isna() | (stripped == ""))]
            if len(non_null) == 0:
                continue
            numeric_coerced = pd.to_numeric(non_null, errors="coerce")
            counts[c]["numeric"] += int(numeric_coerced.notna().sum())
            counts[c]["non_numeric"] += int(numeric_coerced.isna().sum())
        print(f"  processed {rows_done} rows...", end="\r", flush=True)

    print()

    promoted_numeric = []
    demoted_status = []
    still_uncertain = []

    for c, cnt in counts.items():
        total = cnt["numeric"] + cnt["non_numeric"]
        if total == 0:
            continue
        frac_numeric = cnt["numeric"] / total
        if frac_numeric >= NUMERIC_THRESHOLD:
            promoted_numeric.append(c)
        elif frac_numeric <= STATUS_THRESHOLD:
            demoted_status.append(c)
        else:
            still_uncertain.append({"column": c, "fraction_numeric": round(frac_numeric, 3)})

    final_numeric = sorted(set(profile["numeric_columns"]) | set(promoted_numeric))
    final_status = sorted(set(profile["status_columns"]) | set(demoted_status))

    result = {
        "total_rows": profile["total_rows"],
        "numeric_columns": final_numeric,
        "status_columns": final_status,
        "empty_columns": profile["empty_columns"],
        "still_uncertain": still_uncertain,
    }

    with open("final_classification.json", "w") as f:
        json.dump(result, f, indent=2)

    print("=" * 60)
    print("REFINEMENT SUMMARY")
    print("=" * 60)
    print(f"Promoted to numeric (>= {NUMERIC_THRESHOLD*100:.0f}% numeric values): {len(promoted_numeric)}")
    print(f"Demoted to status  (<= {STATUS_THRESHOLD*100:.0f}% numeric values):  {len(demoted_status)}")
    print(f"Still uncertain (needs manual review):                    {len(still_uncertain)}")
    print()
    print(f"FINAL numeric columns: {len(final_numeric)}")
    print(f"FINAL status columns:  {len(final_status)}")
    print()
    if still_uncertain:
        print("Columns needing manual review:")
        for item in still_uncertain:
            print(f"  {item['column']}: {item['fraction_numeric']*100:.1f}% numeric")
    print()
    print("Full details written to final_classification.json")


if __name__ == "__main__":
    main()
