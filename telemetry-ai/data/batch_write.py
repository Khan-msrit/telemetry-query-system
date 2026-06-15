#!/usr/bin/env python3

"""
Batch write large LP file to InfluxDB 3
Avoids 10MB request limit
"""

from influxdb_client_3 import InfluxDBClient3

# ------------ CONFIG -------------
INFLUX_HOST = "http://localhost:8181"
DATABASE = "telemetry"
TOKEN = "apiv3_M6UNbhN9twlGCYvS-SKBnu5Q7JtXJPLNBDyFH2y18M3pOOA-xftKrIYXIVxS8iswbZRx7xfPU15B1hTX935cnw"   # or use os.environ

LP_FILE = "telemetry.lp"
BATCH_SIZE = 5000
# ---------------------------------


def batch_writer():

    client = InfluxDBClient3(
        host=INFLUX_HOST,
        database=DATABASE,
        token=TOKEN
    )

    batch = []
    total = 0

    with open(LP_FILE, "r") as f:
        for line in f:
            batch.append(line.strip())

            if len(batch) >= BATCH_SIZE:
                client.write("\n".join(batch))
                total += len(batch)
                print(f"Wrote {total} rows")
                batch.clear()

        # write remaining
        if batch:
            client.write("\n".join(batch))
            total += len(batch)
            print(f"Wrote {total} rows")

    print("Finished writing.")


if __name__ == "__main__":
    batch_writer()
