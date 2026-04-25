import psycopg2
import uuid
import random
import time
from datetime import datetime, UTC
from psycopg2.extras import Json

print("🚀 FINAL DATA GENERATOR RUNNING")

# =========================
# DB CONFIG
# =========================
DB_CONFIG = {
    "host": "mxsense-db-updated.cfwsawyco4p4.ap-south-1.rds.amazonaws.com",  # 🔴 replace
    "database": "postgres",
    "user": "mxsense_admin",
    "password": "mxsense123",
    "port": 5432
}

# =========================
# HELPERS
# =========================
def gen_uuid():
    return str(uuid.uuid4())

def now():
    return datetime.now(UTC)

# =========================
# LOAD DATA
# =========================
def load_devices(cur):
    cur.execute("""
        SELECT id FROM devices
        WHERE device_uid IN ('device_01','device_02','device_03','device_04','device_05')
    """)
    return [r[0] for r in cur.fetchall()]

def load_sensors(cur):
    cur.execute("SELECT id, sensor_code FROM sensors")
    return [{"id": r[0], "code": r[1]} for r in cur.fetchall()]

# =========================
# SENSOR VALUE GENERATION
# =========================
def generate_sensor_value(sensor_code):

    # 🎯 ONLY REQUIRED GAS SENSORS
    GAS_SENSORS = {
        "CH2_ZE07_CO",
        "CH2_ME3_NH3",
        "CH2_ME3_SO2",
        "CH2_ME3_H2S",
        "CH2_ME3_NO2"
    }

    # ✅ GAS
    if sensor_code in GAS_SENSORS:
        return {
            "gas_ppm": round(random.uniform(10, 300), 2),
            "confidence": round(random.uniform(0.85, 1.0), 2)
        }

    # ❌ Skip other CH2 sensors completely
    elif sensor_code.startswith("CH2"):
        return None

    # VOC (CH1)
    elif sensor_code.startswith("CH1"):
        return {
            "voc_index": round(random.uniform(50, 400), 2),
            "resistance": round(random.uniform(1000, 100000), 2)
        }

    # ENV (CH0)
    elif sensor_code.startswith("CH0"):
        return {
            "temperature_c": round(random.uniform(20, 35), 2),
            "humidity_pct": round(random.uniform(30, 80), 2),
            "pressure_pa": round(random.uniform(95000, 105000), 2)
        }

    # PM (CH4)
    elif sensor_code.startswith("CH4"):
        return {
            "pm1": round(random.uniform(5, 80), 2),
            "pm2_5": round(random.uniform(10, 150), 2),
            "pm10": round(random.uniform(20, 250), 2)
        }

    # THERMAL (CH5)
    elif sensor_code.startswith("CH5"):
        return {
            "temperature": round(random.uniform(25, 45), 2)
        }

    # SPECTRAL (CH6)
    elif sensor_code.startswith("CH6"):
        return {
            "intensity": round(random.uniform(0.1, 1.0), 3)
        }

    # DISTANCE (CH8)
    elif sensor_code.startswith("CH8"):
        return {
            "distance_mm": round(random.uniform(100, 1500), 2)
        }

    # DEFAULT
    return {
        "value": round(random.uniform(10, 100), 2)
    }

# =========================
# INSERT DATA
# =========================
def insert_data(cur, devices, sensors):

    for device_id in devices:

        # ✅ SAME timestamp per batch
        sample_time = now()

        for sensor in sensors:

            value = generate_sensor_value(sensor["code"])

            # 🚨 Skip unwanted sensors
            if value is None:
                continue

            cur.execute("""
                INSERT INTO raw_sensor_data
                (id, device_id, sensor_id, timestamp_utc, raw_value_json, quality_flags_json)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                gen_uuid(),
                device_id,
                sensor["id"],
                sample_time,
                Json(value),
                Json({"quality": "good"})
            ))

# =========================
# MAIN
# =========================
def main():

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print("🔄 Loading devices...")
    devices = load_devices(cur)

    print("🔄 Loading sensors...")
    sensors = load_sensors(cur)

    print("🚀 Running 50 batches...\n")

    for i in range(50):
        insert_data(cur, devices, sensors)
        print(f"✅ Batch {i+1} inserted")
        time.sleep(2)

    print("\n🎯 DATA GENERATION COMPLETE")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
