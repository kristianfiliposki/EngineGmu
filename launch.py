import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
import time
import GMU

# Carica le variabili dall'.env
load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "password": os.getenv("DB_PASSWORD")
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def insert_gmu_5m():
    gmu_value = GMU.GMU()
    if gmu_value is None:
        print("Errore: GMU non calcolato.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gmu_5m (
                    timestamp TIMESTAMP PRIMARY KEY,
                    gmu_value DOUBLE PRECISION
                )
            """)
            cursor.execute("""
                INSERT INTO gmu_5m (timestamp, gmu_value)
                VALUES (%s, %s)
                ON CONFLICT (timestamp) DO UPDATE SET gmu_value = EXCLUDED.gmu_value
            """, (timestamp, gmu_value))
        print(f"[5M] Inserito GMU: {gmu_value} @ {timestamp}")

def insert_gmu_daily_summary():
    today = datetime.now().strftime("%Y-%m-%d")
    start = today + " 00:00:00"
    end = today + " 23:59:59"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gmu_1d (
                    date DATE PRIMARY KEY,
                    average_gmu DOUBLE PRECISION,
                    last_gmu DOUBLE PRECISION
                )
            """)
            cursor.execute("""
                SELECT AVG(gmu_value),
                       MAX(timestamp),
                       (SELECT gmu_value FROM gmu_5m WHERE timestamp = (SELECT MAX(timestamp) FROM gmu_5m WHERE timestamp BETWEEN %s AND %s))
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
            """, (start, end, start, end))
            
            result = cursor.fetchone()
            avg, _, last = result

            if avg is not None:
                cursor.execute("""
                    INSERT INTO gmu_1d (date, average_gmu, last_gmu)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (date) DO UPDATE SET average_gmu = EXCLUDED.average_gmu, last_gmu = EXCLUDED.last_gmu
                """, (today, avg, last))
                print(f"[1D] Salvata media: {avg}, ultimo: {last} per il {today}")
            else:
                print(f"[1D] Nessun dato GMU per il {today}")

def loop_generatore():
    last_day = datetime.now().date()
    while True:
        now = datetime.now()
        insert_gmu_5m()

        if now.date() != last_day:
            insert_gmu_daily_summary()
            last_day = now.date()

        time.sleep(5 * 60)

if __name__ == "__main__":
    loop_generatore()
