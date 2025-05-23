from fastapi import FastAPI
import workingDates
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import psycopg2
import os
import GMU
import workingDates.mediaTassi
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "password": os.getenv("DB_PASSWORD")
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Per test puoi mettere "*", in produzione specifica i domini
    allow_credentials=False,
    allow_methods=["*"],  # Permetti tutti i metodi (GET, POST, etc.)
    allow_headers=["*"],  # Permetti tutti gli headers
)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.get("/")
def get_last_price():
    return GMU.GMU()

@app.get("/avgWorldValue")
def ratingList():
    import effects
    tassi=effects.tassodicambio.media_tassi_cambio()
    old, new = effects.history_dates.scarica_dati_storici()
    mediaValValutari=workingDates.mediaTassi.mediaTassi(tassi,old,new)
    return  mediaValValutari

@app.get("/5m")
def get_all_gmu():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT timestamp, gmu_value
                FROM gmu_5m
                ORDER BY timestamp ASC;
            """)
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
    try:
        value = GMU.GMU()
        print(f"Inserendo GMU: {value} al timestamp {timestamp}")
        
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
                """, (timestamp, value))

        return {"message": "Inserito GMU", "value": value, "timestamp": timestamp}

    except Exception as e:
        print("Errore durante l'inserimento GMU:", str(e))
        return {"error": str(e)}


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
def insert_daily_summary():
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

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
                SELECT AVG(gmu_value), MAX(gmu_value), MIN(gmu_value)
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
            """, (start, end))

            avg, max_val, min_val = cursor.fetchone()

            # Recupero dell'ultimo valore GMU della giornata
            cursor.execute("""
                SELECT gmu_value
                FROM gmu_5m
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (start, end))
            last_row = cursor.fetchone()
            last_val = last_row[0] if last_row else None

            if avg is not None and last_val is not None:
                cursor.execute("""
                    INSERT INTO gmu_1d (date, average_gmu, max_gmu, min_gmu, last_gmu)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE
                    SET average_gmu = EXCLUDED.average_gmu,
                        max_gmu = EXCLUDED.max_gmu,
                        min_gmu = EXCLUDED.min_gmu,
                        last_gmu = EXCLUDED.last_gmu
                """, (start.date(), avg, max_val, min_val, last_val))

                return {
                    "message": "Media giornaliera salvata",
                    "date": str(start.date()),
                    "average": avg,
                    "max": max_val,
                    "min": min_val,
                    "last": last_val
                }

            return {"message": "Nessun dato GMU disponibile per oggi"}