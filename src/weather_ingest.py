import os
import psycopg2
from datetime import datetime

# Database connection config
DB_CONFIG = {
    "dbname": "weather_db",
    "user": "postgres", 
    "password": "<Your_Password>",
    "host": "localhost",
    "port": 5432
}
DATA_DIR = "<Your_Path>"

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# -----------------------------------------------------------------------------
# ensure_station(cursor, station_code, state):
#   - Ensures the given weather station exists in weather_station.
#   - Inserts the station_code and state if not present -- > (ON CONFLICT do nothing).
#   - Returns the station_id for use by inserts into weather_record.
# -----------------------------------------------------------------------------

def ensure_station(cursor, station_code, state):
    cursor.execute("""
        INSERT INTO weather_station (station_code, state)
        VALUES (%s, %s)
        ON CONFLICT (station_code) DO NOTHING
    """, (station_code, state))
    cursor.execute("SELECT station_id FROM weather_station WHERE station_code = %s", (station_code,))
    return cursor.fetchone()[0]

# -----------------------------------------------------------------------------
# ingest_file(conn, file_path, station_code, state='OH'):
#   - Reads a single raw data file (tab-separated 4 columns).
#   - Converts -9999 to NULL for all numeric fields.
#   - Inserts rows into weather_record with de-dup via ON CONFLICT.
#   - Logs the run in weather_ingest_log with start/end and row count.
# -----------------------------------------------------------------------------

def ingest_file(conn, file_path, station_code, state='OH'):
    with conn.cursor() as cur:
        station_id = ensure_station(cur, station_code, state)
        start_time = datetime.now()
        count = 0

        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue
                raw_date, max_temp, min_temp, precip = parts
                try:
                    date = datetime.strptime(raw_date, "%Y%m%d").date()
                    max_temp = int(max_temp)
                    min_temp = int(min_temp)
                    precip = int(precip)

                    cur.execute("""
                        INSERT INTO weather_record (station_id, record_date, max_temp, min_temp, precipitation)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (station_id, record_date) DO NOTHING
                    """, (
                        station_id, date,
                        None if max_temp == -9999 else max_temp,
                        None if min_temp == -9999 else min_temp,
                        None if precip == -9999 else precip
                    ))
                    count += cur.rowcount

                except Exception as e:
                    print(f"Skipping line in {file_path}: {line.strip()} | Error: {e}")

        end_time = datetime.now()
        cur.execute("""
            INSERT INTO weather_ingest_log (station_code, start_time, end_time, records_ingested)
            VALUES (%s, %s, %s, %s)
        """, (station_code, start_time, end_time, count))
        print(f"[{station_code}] Ingested {count} records.")

# -----------------------------------------------------------------------------
# compute_statistics(conn):
#   - Aggregates yearly stats per station from weather_record.
#   - AVG ignores NULLs, so missing values (-9999 mapped to NULL) are excluded.
#   - Upserts into weather_statistics via ON CONFLICT (station_id, year).
## -----------------------------------------------------------------------------

def compute_statistics(conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO weather_statistics (station_id, year, avg_max_temp_celsius, avg_min_temp_celsius, total_precipitation_cm)
            SELECT
                station_id,
                EXTRACT(YEAR FROM record_date)::INT AS year,
                ROUND(AVG(max_temp)::NUMERIC / 10.0, 2),
                ROUND(AVG(min_temp)::NUMERIC / 10.0, 2),
                ROUND(SUM(precipitation)::NUMERIC / 100.0, 2)
            FROM weather_record
            GROUP BY station_id, EXTRACT(YEAR FROM record_date)
            ON CONFLICT (station_id, year) DO UPDATE
            SET
                avg_max_temp_celsius = EXCLUDED.avg_max_temp_celsius,
                avg_min_temp_celsius = EXCLUDED.avg_min_temp_celsius,
                total_precipitation_cm = EXCLUDED.total_precipitation_cm;
        """)
        print("[Stats] Yearly weather statistics updated.")

# -----------------------------------------------------------------------------
# main():
#   - Connects to the database.
#   - Iterates through all .txt files in DATA_DIR
# -----------------------------------------------------------------------------

def main():
    conn = connect_db()
    try:
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".txt"):
                station_code = filename.replace(".txt", "")
                file_path = os.path.join(DATA_DIR, filename)
                ingest_file(conn, file_path, station_code)
        compute_statistics(conn)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
