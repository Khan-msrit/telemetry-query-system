#!/usr/bin/env python3
"""
Generate an InfluxDB Line Protocol (.lp) file

Specifications:
- 10,000 entries per day
- From 2026-01-15 to 2026-02-28 (inclusive)
- Evenly spaced timestamps per day
- Uses epoch nanoseconds (InfluxDB native)
"""

import random
from datetime import datetime, timezone, timedelta

MEASUREMENT = "telemetry"
OUTPUT_FILE = "telemetry.lp"

ENTRIES_PER_DAY = 10_000

START_DATE = datetime(2026, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
END_DATE   = datetime(2026, 2, 28, 23, 59, 59, tzinfo=timezone.utc)

SECONDS_PER_DAY = 86400
NS_PER_SECOND = 1_000_000_000

PARAMETERS = [
    "RSP_RCSL_PRIORITY-1","RSP_TCSL_PRIORITY-1","RSP_RCSL_PRIORITY-2","RSP_TCSL_PRIORITY-2",
    "RSP_RCSL_PRIORITY-3","RSP_TCSL_PRIORITY-3","RSP_RCSL_PRIORITY-4","RSP_TCSL_PRIORITY-4",
    "BKG_SRC_SEL_FOR_ACC_DV_IN_AUX","SS_PUR_SEL_FOR_TM","EST-1_BKGND_CONV_FLG",
    "EST-1_BKGND_OP_WITH_SENS_AVAIL","EST-1_BKGND_EST_EXEC","EST-1_BKGND_YET_TO_INIT",
    "EST-1_BKGND_INIT_FRM_SENS","EST-1_BKGND_SENS_SEL","EST-2_BKGND_CONV_FLG",
    "EST-2_BKGND_OP_WITH_SENS_AVAIL","EST-2_BKGND_EST_EXEC","EST-2_BKGND_YET_TO_INIT",
    "EST-2_BKGND_INIT_FRM_SENS","EST-2_BKGND_SENS_SEL","RN-2_SENS_SEL","RCSL",
    "ARDUS_STATE","PDS_POS_FOR_CODK","PDS_POS_FOR_UNCODK","CODK_SUN_POINTING",
    "SC_RETRACT","SC_RGDZ","SC_DERGDZ","SC_EXTN","SC_CAPTURE_RELEASE","SC_CAPTURE",
    "AOC_ERR_LOG","TCR&ACO_FAIL","SV_USAGE_FOR_SELF","SV_USAGE_FOR_OTHER",
    "DV_SEL_FOR_TM","PUR_THR_P_THR_FAIL","TCSL_LOGIC_STORT","RCSL_LOGIC_STORT",
    "GUID_SEQR_STATE","MAG_BIAS_EST_UPDT","THR_FDI_ACT","ABORT_FIN_POS_PREV/GRND",
    "PUR_CUR_FD","ATT_CONV_REQ_FLG","AUX_RAM_RD","EST-1_SNSR_SEL","EST-2_SNSR_SEL",
    "EST_SNSR_SEL_FOR_CNTRL","MANUAL_HW_TMR_THR_PATTERN","HP_MEAS_DATA_AVAIL_FOR_POS_VEL",
    "LRF_DATA_VALIDITY","PDS_DATA_VALIDITY","RS_DATA_VALIDITY","SPS_PKT_RX_THRU_ISL",
    "AOCS_PKT_RX_THRU_ISL","GUID_SEQR_EXECUTION","ACC_ANGLE_TM_RESLN",
    "GTD_TEMP_COMPSN_MODE_STS","GTD_TEMP_COMPUTATION","NEG_YAW_THR_USE_FOR_GUID",
    "SC_RGDZ_LOGIC","SC_EXTENSION_LOGIC","LAME_TEMP_COMPSN_FINE","LAME_TEMP_COMPSN_COARSE",
    "HP_GUID_INTGD_FOR_POS_VEL_COMP","PWPFM_4_HP_PULSE_EXTEND_LOGIC",
    "HP_RAD_AXIS_PWPFM","HP_TRAN_AXIS_PWPFM","HP_NOR_AXIS_PWPFM","GTP_5V_MON",
    "RN-1_OP_WITH_SENS_AVAIL","RN-2_OP_WITH_SENS_AVAIL","LAME_ACCLM_INIT",
    "VAL_D_DELTA_T_CORR_LI_MSB","AD1_THR_FIRE_STS","AD2_THR_FIRE_STS",
    "AD3_THR_FIRE_STS","AD4_THR_FIRE_STS","AD5_THR_FIRE_STS",
    "RW-1_DFC_STS_OBC","RW-2_DFC_STS_OBC","RW-3_DFC_STS_OBC","RW-4_DFC_STS_OBC",
    "BUS_VOL","BAT_VOL_M_COARSE","BAT_VOL_M_FINE",
    "BAT-1_CUR_FINE_M","BAT-1_CUR_FINE_R","BAT-1_CUR_COARSE_M","BAT-1_CUR_COARSE_R"
]

def random_value(name: str):
    if "VOL" in name or "5V" in name:
        return round(random.uniform(4.8, 30.0), 2)
    if "CUR" in name:
        return round(random.uniform(0.5, 5.0), 2)
    if "PRIORITY" in name:
        return random.randint(1, 4)
    if any(k in name for k in ["STS", "FLG", "LOGIC"]):
        return random.randint(0, 1)
    return random.randint(0, 5)

def to_epoch_ns(dt: datetime) -> int:
    return int(dt.timestamp() * NS_PER_SECOND)

def generate_lp():
    current_day = START_DATE
    total_rows = 0

    with open(OUTPUT_FILE, "w") as f:
        while current_day.date() <= END_DATE.date():

            day_start_ns = to_epoch_ns(current_day)
            step_ns = (SECONDS_PER_DAY * NS_PER_SECOND) // ENTRIES_PER_DAY

            for i in range(ENTRIES_PER_DAY):

                fields = []
                for p in PARAMETERS:
                    v = random_value(p)
                    if isinstance(v, float):
                        fields.append(f"{p}={v}")
                    else:
                        fields.append(f"{p}={v}i")

                ts = day_start_ns + i * step_ns
                line = f"{MEASUREMENT} " + ",".join(fields) + f" {ts}"
                f.write(line + "\n")

                total_rows += 1

            current_day += timedelta(days=1)

    print(f"Generated {total_rows} entries")
    print(f"Output file: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_lp()
