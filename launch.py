from fastapi import FastAPI
import workingDates
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import psycopg2
import os
import GMU
import workingDates.mediaTassi

app = FastAPI()
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


@app.get("/")
def get_last_price():
    return GMU.GMU()

@app.get("/avgWorldValue")
def ratingList():
    return workingDates.mediaTassi.mediaTassi()

@app.get("/5m")
def get_gmu_today():
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT timestamp, gmu_value
                FROM gmu_5m
                WHERE timestamp::date = %s
                ORDER BY timestamp ASC;
            """, (today,))
            rows = cur.fetchall()
            return [{"timestamp": row[0], "gmu_value": row[1]} for row in rows]


@app.get("/1d")
def get_daily_summary():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT date, average_gmu, last_gmu
                FROM gmu_1d
                ORDER BY date ASC;
            """)
            rows = cur.fetchall()
            return [
                {"date": row[0], "average_gmu": row[1], "last_gmu": row[2]}
                for row in rows
            ]


@app.get("/insert5m")
def insert_gmu_5m():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

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
            """, (timestamp, GMU.GMU()))

    return {"message": "Inserito GMU", "value": GMU.GMU(), "timestamp": timestamp}


@app.get("/insert1h")
def insert_hourly_summary():
    now = datetime.now(timezone.utc)
    end = now.replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(hours=1)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gmu_1h (
                    hour TIMESTAMP PRIMARY KEY,
                    average_gmu DOUBLE PRECISION,
                    max_gmu DOUBLE PRECISION,
                    min_gmu DOUBLE PRECISION
                )
            """)
            cursor.execute("""
                SELECT AVG(gmu_value), MAX(gmu_value), MIN(gmu_value)
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
            """, (start, end))
            avg, max_val, min_val = cursor.fetchone()

            if avg is not None:
                cursor.execute("""
                    INSERT INTO gmu_1h (hour, average_gmu, max_gmu, min_gmu)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (hour) DO UPDATE
                    SET average_gmu = EXCLUDED.average_gmu,
                        max_gmu = EXCLUDED.max_gmu,
                        min_gmu = EXCLUDED.min_gmu
                """, (start, avg, max_val, min_val))

                return {
                    "message": "Dati orari salvati",
                    "start": str(start),
                    "average": avg,
                    "max": max_val,
                    "min": min_val
                }
            else:
                return {"message": "Nessun dato GMU disponibile per quest'ora"}


@app.get("/insert1d")
def insert_gmu_daily_summary():
    today_utc = datetime.now(timezone.utc).date()
    start = f"{today_utc} 00:00:00"
    end = f"{today_utc} 23:59:59"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gmu_1d (
                    date DATE PRIMARY KEY,
                    average_gmu DOUBLE PRECISION,
                    max_gmu DOUBLE PRECISION,
                    min_gmu DOUBLE PRECISION,
                    last_gmu DOUBLE PRECISION
                )
            """)

            cursor.execute("""
                SELECT 
                    AVG(gmu_value),
                    MAX(gmu_value),
                    MIN(gmu_value),
                    (SELECT gmu_value FROM gmu_5m WHERE timestamp = (
                        SELECT MAX(timestamp)
                        FROM gmu_5m
                        WHERE timestamp BETWEEN %s AND %s
                    ))
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
            """, (start, end, start, end))

            result = cursor.fetchone()
            avg, max_val, min_val, last = result

            if avg is not None:
                cursor.execute("""
                    INSERT INTO gmu_1d (date, average_gmu, max_gmu, min_gmu, last_gmu)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE
                        SET average_gmu = EXCLUDED.average_gmu,
                            max_gmu = EXCLUDED.max_gmu,
                            min_gmu = EXCLUDED.min_gmu,
                            last_gmu = EXCLUDED.last_gmu
                """, (today_utc, avg, max_val, min_val, last))
                
                return {
                    "message": "Media giornaliera salvata",
                    "average": avg,
                    "max": max_val,
                    "min": min_val,
                    "last": last,
                    "date": str(today_utc)
                }
            else:
                return {"message": "Nessun dato GMU disponibile per oggi"}


