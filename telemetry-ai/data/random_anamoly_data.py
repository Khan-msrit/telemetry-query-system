#!/usr/bin/env python3
"""
High-Fidelity Spacecraft Telemetry Simulator

✔ 30,000 entries per day
✔ Jan 15 2026 → Feb 28 2026
✔ Multiple measurements:
      - power
      - attitude
      - navigation
✔ Realistic drift
✔ Anomaly injection
✔ Epoch nanosecond timestamps
"""

import random
import math
from datetime import datetime, timezone, timedelta

# ---------------- CONFIG ----------------

ENTRIES_PER_DAY = 30_000
START_DATE = datetime(2026, 1, 15, tzinfo=timezone.utc)
END_DATE   = datetime(2026, 2, 28, tzinfo=timezone.utc)

NS_PER_SECOND = 1_000_000_000
SECONDS_PER_DAY = 86400

OUTPUT_FILE = "telemetry_realistic.lp"

# anomaly probabilities
VOLTAGE_SPIKE_PROB = 0.0005
NAV_GLITCH_PROB = 0.0003
THRUSTER_BURST_PROB = 0.0004

# ----------------------------------------


def to_ns(dt):
    return int(dt.timestamp() * NS_PER_SECOND)


# ==============================
# POWER MODEL
# ==============================

def power_model(t_day_fraction):
    # Simulate orbital solar charging sinusoidal pattern
    base_voltage = 28.0 + 0.4 * math.sin(2 * math.pi * t_day_fraction)
    bus_voltage = 28.0 + random.gauss(0, 0.05)

    battery_current = 2.0 + 0.8 * math.sin(2 * math.pi * t_day_fraction)

    # anomaly injection
    if random.random() < VOLTAGE_SPIKE_PROB:
        base_voltage += random.uniform(2.0, 5.0)

    return {
        "BUS_VOL": round(bus_voltage, 3),
        "BAT_VOL_M_FINE": round(base_voltage, 3),
        "BAT-1_CUR_FINE_M": round(battery_current + random.gauss(0, 0.1), 3),
    }


# ==============================
# ATTITUDE MODEL
# ==============================

def attitude_model():
    guid_state = random.choices(
        population=[1, 2, 3],
        weights=[0.8, 0.15, 0.05]
    )[0]

    thr_fire = 0
    if random.random() < THRUSTER_BURST_PROB:
        thr_fire = 1

    return {
        "RCSL": random.randint(0, 1),
        "GUID_SEQR_STATE": guid_state,
        "AD1_THR_FIRE_STS": thr_fire,
        "HP_RAD_AXIS_PWPFM": random.randint(0, 1),
    }


# ==============================
# NAVIGATION MODEL
# ==============================

def navigation_model(step):
    drift_x = 7000 + step * 0.00001
    drift_y = 0 + step * 0.00002
    drift_z = 0 + step * 0.000015

    if random.random() < NAV_GLITCH_PROB:
        drift_x += random.uniform(50, 200)

    return {
        "NAV_POS_X": round(drift_x + random.gauss(0, 0.5), 3),
        "NAV_POS_Y": round(drift_y + random.gauss(0, 0.5), 3),
        "NAV_POS_Z": round(drift_z + random.gauss(0, 0.5), 3),
    }


# ==============================
# GENERATOR
# ==============================

def generate():

    current_day = START_DATE
    total_rows = 0

    with open(OUTPUT_FILE, "w") as f:

        while current_day <= END_DATE:

            day_start_ns = to_ns(current_day)
            step_ns = (SECONDS_PER_DAY * NS_PER_SECOND) // ENTRIES_PER_DAY

            for i in range(ENTRIES_PER_DAY):

                timestamp = day_start_ns + i * step_ns
                t_fraction = i / ENTRIES_PER_DAY

                # ----- POWER -----
                power_fields = power_model(t_fraction)
                line = "power " + ",".join(
                    f"{k}={v}" for k, v in power_fields.items()
                ) + f" {timestamp}"
                f.write(line + "\n")

                # ----- ATTITUDE -----
                attitude_fields = attitude_model()
                line = "attitude " + ",".join(
                    f"{k}={v}i" for k, v in attitude_fields.items()
                ) + f" {timestamp}"
                f.write(line + "\n")

                # ----- NAVIGATION -----
                nav_fields = navigation_model(total_rows)
                line = "navigation " + ",".join(
                    f"{k}={v}" for k, v in nav_fields.items()
                ) + f" {timestamp}"
                f.write(line + "\n")

                total_rows += 1

            current_day += timedelta(days=1)

    print("Simulation Complete")
    print(f"Total logical time points: {total_rows}")
    print(f"Actual rows written (3 measurements each): {total_rows * 3}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate()
