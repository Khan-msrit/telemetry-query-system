"""
Cleans, reshapes, and loads the telemetry CSV into InfluxDB3 using the
narrow (tag+field) schema:

    telemetry_numeric: time, parameter (tag), value (float field)
    telemetry_status:  time, parameter (tag), value (string field)

Uses load_classification.json (from finalize_classification.py) to know
which columns are numeric vs status. Skips empty columns entirely.
Connection settings (INFLUX_HOST / INFLUX_TOKEN / INFLUX_DATABASE) are set
as constants near the top of this file - fill them in before running.

Line-protocol text is built with vectorized pandas string ops (not a
Python for-loop) since looping row-by-row over hundreds of thousands of
lines is the dominant cost at this scale.

Usage (ALWAYS test small first, against a scratch database):
    python3 load_telemetry.py --csv /path/to/full.csv --classification load_classification.json --database telemetry_test --max-rows 200

To find malformed lines WITHOUT writing anything to InfluxDB:
    python3 load_telemetry.py --csv /path/to/full.csv --classification load_classification.json --max-rows 200 --dry-run

Then, once verified, load into the real database:
    python3 load_telemetry.py --csv /path/to/full.csv --classification load_classification.json
"""

import argparse
import json
import re
import sys
import time
import numpy as np
import pandas as pd
import requests

# ---- InfluxDB3 connection (fill these in) ----
INFLUX_HOST = "http://localhost:8181"       # e.g. http://localhost:8181
INFLUX_TOKEN = "apiv3_M6UNbhN9twlGCYvS-SKBnu5Q7JtXJPLNBDyFH2y18M3pOOA-xftKrIYXIVxS8iswbZRx7xfPU15B1hTX935cnw"
INFLUX_DATABASE = "telemetry_test"               # default database; override with --database

TIMESTAMP_COL = "Timestamp"
TIMESTAMP_FORMAT = "%d-%b-%Y %H:%M:%S.%f"

CHUNK_SIZE = 1000         # rows read from CSV per pass
BATCH_SIZE = 20000        # line-protocol lines per HTTP write request

NUMERIC_LINE_RE = re.compile(r"^telemetry_numeric,parameter=.+ value=-?[0-9.eE+\-]+ \d+$")
STATUS_LINE_RE = re.compile(r'^telemetry_status,parameter=.+ value=".*" \d+$')


def escape_tag_series(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace("\\", "\\\\", regex=False)
        .str.replace(",", "\\,", regex=False)
        .str.replace(" ", "\\ ", regex=False)
        .str.replace("=", "\\=", regex=False)
    )


def escape_field_string_series(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace("\\", "\\\\", regex=False)
        .str.replace('"', '\\"', regex=False)
    )


def build_lines_numeric(df_long: pd.DataFrame) -> list:
    if df_long.empty:
        return []
    param_esc = escape_tag_series(df_long["parameter"])
    value_str = df_long["value"].astype(str)
    time_str = df_long["time_ns"].astype(str)
    lines = "telemetry_numeric,parameter=" + param_esc + " value=" + value_str + " " + time_str
    return lines.tolist()


def build_lines_status(df_long: pd.DataFrame) -> list:
    if df_long.empty:
        return []
    param_esc = escape_tag_series(df_long["parameter"])
    val_esc = escape_field_string_series(df_long["value"])
    time_str = df_long["time_ns"].astype(str)
    lines = 'telemetry_status,parameter=' + param_esc + ' value="' + val_esc + '" ' + time_str
    return lines.tolist()


def validate_lines(lines, pattern, label, max_report=20):
    bad_count = 0
    reported = 0
    for i, line in enumerate(lines):
        if "\n" in line or "\r" in line:
            bad_count += 1
            if reported < max_report:
                print(f"[{label}] line {i}: EMBEDDED NEWLINE/CR -> {repr(line)}")
                reported += 1
            continue
        if not pattern.match(line):
            bad_count += 1
            if reported < max_report:
                print(f"[{label}] line {i}: DOES NOT MATCH EXPECTED PATTERN -> {repr(line)}")
                reported += 1
    print(f"[{label}] checked {len(lines)} lines, {bad_count} invalid"
          + (f" (showing first {max_report})" if bad_count > max_report else ""))
    return bad_count


def write_batch(session, host, token, database, lines):
    if not lines:
        return 0.0
    url = f"{host.rstrip('/')}/api/v3/write_lp"
    params = {"db": database, "precision": "ns", "accept_partial": "true"}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/plain"}
    body = "\n".join(lines)

    t0 = time.time()
    resp = session.post(url, params=params, headers=headers, data=body, timeout=120)
    write_time = time.time() - t0

    if resp.status_code not in (200, 204):
        print(f"\nWRITE ERROR ({resp.status_code}): {resp.text[:2000]}")
        raise RuntimeError("Write failed - stopping so nothing is silently lost.")
    return write_time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--max-rows", type=int, default=None, help="Only load the first N rows (for testing)")
    parser.add_argument("--database", default=None, help="Override INFLUX_DATABASE (e.g. a scratch/test db)")
    parser.add_argument("--dry-run", action="store_true", help="Validate generated lines but do NOT write to InfluxDB")
    args = parser.parse_args()

    host = INFLUX_HOST
    token = INFLUX_TOKEN
    database = args.database or INFLUX_DATABASE

    if not args.dry_run and (not token or token == "PASTE_YOUR_TOKEN_HERE"):
        print("Set INFLUX_TOKEN at the top of this file before running (or use --dry-run).")
        sys.exit(1)

    with open(args.classification) as f:
        cls = json.load(f)

    numeric_cols = cls["numeric_columns"]
    status_cols = cls["status_columns"]
    usecols = [TIMESTAMP_COL] + numeric_cols + status_cols

    print(f"Numeric columns: {len(numeric_cols)}, Status columns: {len(status_cols)}")
    if args.dry_run:
        print("DRY RUN: validating only, nothing will be written to InfluxDB")
    else:
        print(f"Target: {host}  db={database}")
    if args.max_rows:
        print(f"TEST MODE: loading only the first {args.max_rows} rows")

    session = requests.Session() if not args.dry_run else None

    total_numeric_points = 0
    total_status_points = 0
    rows_processed = 0
    start_time = time.time()

    build_time_total = 0.0
    write_time_total = 0.0

    reader = pd.read_csv(args.csv, dtype=str, usecols=usecols, chunksize=CHUNK_SIZE)

    numeric_buffer = []
    status_buffer = []
    total_bad = 0

    for chunk in reader:
        if args.max_rows is not None and rows_processed >= args.max_rows:
            break

        if args.max_rows is not None:
            remaining = args.max_rows - rows_processed
            if len(chunk) > remaining:
                chunk = chunk.iloc[:remaining]

        t_build_start = time.time()

        # ---- Parse timestamp to nanosecond epoch ----
        ts = pd.to_datetime(chunk[TIMESTAMP_COL], format=TIMESTAMP_FORMAT, errors="coerce")
        chunk = chunk.assign(time_ns=ts.astype("int64"))
        chunk = chunk.dropna(subset=["time_ns"])

        # ---- Numeric columns: melt to long format ----
        num_long = chunk.melt(
            id_vars=["time_ns"], value_vars=numeric_cols, var_name="parameter", value_name="value"
        )
        num_long["value"] = num_long["value"].str.strip()
        num_long = num_long[num_long["value"].notna() & (num_long["value"] != "")]
        num_long["value"] = pd.to_numeric(num_long["value"], errors="coerce")
        num_long = num_long.dropna(subset=["value"])
        num_long = num_long[np.isfinite(num_long["value"])]

        # ---- Status columns: melt to long format ----
        stat_long = chunk.melt(
            id_vars=["time_ns"], value_vars=status_cols, var_name="parameter", value_name="value"
        )
        stat_long["value"] = stat_long["value"].str.strip()
        stat_long = stat_long[stat_long["value"].notna() & (stat_long["value"] != "")]

        new_numeric_lines = build_lines_numeric(num_long)
        new_status_lines = build_lines_status(stat_long)

        build_time_total += time.time() - t_build_start

        numeric_buffer.extend(new_numeric_lines)
        status_buffer.extend(new_status_lines)

        total_numeric_points += len(num_long)
        total_status_points += len(stat_long)
        rows_processed += len(chunk)

        if args.dry_run:
            total_bad += validate_lines(new_numeric_lines, NUMERIC_LINE_RE, "numeric")
            total_bad += validate_lines(new_status_lines, STATUS_LINE_RE, "status")
            numeric_buffer = []
            status_buffer = []
            continue

        # ---- Flush batches (live mode only) ----
        while len(numeric_buffer) >= BATCH_SIZE:
            write_time_total += write_batch(session, host, token, database, numeric_buffer[:BATCH_SIZE])
            numeric_buffer = numeric_buffer[BATCH_SIZE:]
        while len(status_buffer) >= BATCH_SIZE:
            write_time_total += write_batch(session, host, token, database, status_buffer[:BATCH_SIZE])
            status_buffer = status_buffer[BATCH_SIZE:]

        elapsed = time.time() - start_time
        print(
            f"\rRows: {rows_processed} | numeric pts: {total_numeric_points} | "
            f"status pts: {total_status_points} | elapsed: {elapsed:.0f}s "
            f"(build: {build_time_total:.0f}s, write: {write_time_total:.0f}s)",
            end="", flush=True,
        )

    if args.dry_run:
        print()
        print("=" * 60)
        print("DRY RUN COMPLETE")
        print(f"Rows checked:      {rows_processed}")
        print(f"Total bad lines:   {total_bad}")
        print(f"Build time:        {build_time_total:.1f}s")
        print("=" * 60)
        return

    # ---- Flush remaining ----
    write_time_total += write_batch(session, host, token, database, numeric_buffer)
    write_time_total += write_batch(session, host, token, database, status_buffer)

    total_elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print("DONE")
    print(f"Rows processed:         {rows_processed}")
    print(f"Numeric points written: {total_numeric_points}")
    print(f"Status points written:  {total_status_points}")
    print(f"Total time:             {total_elapsed:.0f}s")
    print(f"  - line building:      {build_time_total:.0f}s")
    print(f"  - network writes:     {write_time_total:.0f}s")
    if rows_processed:
        print(f"Rate: {rows_processed / total_elapsed:.2f} rows/sec")
        est_full_hours = (30508 / max(rows_processed / total_elapsed, 0.001)) / 3600
        print(f"Estimated time for full 30,508-row file at this rate: {est_full_hours:.2f} hours")


if __name__ == "__main__":
    main()