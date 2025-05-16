from fastapi import FastAPI
from datetime import datetime, timezone
from dotenv import load_dotenv
import psycopg2
import os
import GMU

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
    

    return {"message": "Inserito GMU", "value":GMU.GMU() , "timestamp": timestamp}

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
                    last_gmu DOUBLE PRECISION
                )
            """)
            cursor.execute("""
                SELECT AVG(gmu_value),
                       MAX(timestamp),
                       (SELECT gmu_value FROM gmu_5m WHERE timestamp = (
                           SELECT MAX(timestamp)
                           FROM gmu_5m
                           WHERE timestamp BETWEEN %s AND %s
                       ))
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
            """, (start, end, start, end))

            result = cursor.fetchone()
            avg, _, last = result

            if avg is not None:
                cursor.execute("""
                    INSERT INTO gmu_1d (date, average_gmu, last_gmu)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (date) DO UPDATE
                        SET average_gmu = EXCLUDED.average_gmu,
                            last_gmu = EXCLUDED.last_gmu
                """, (today_utc, avg, last))
                return {
                    "message": "Media salvata",
                    "average": avg,
                    "last": last,
                    "date": str(today_utc)
                }
            else:
                return {"message": "Nessun dato GMU disponibile per oggi"}

