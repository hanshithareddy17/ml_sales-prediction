import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST") or os.getenv("DB_HOST") or "localhost",
        database=os.getenv("POSTGRES_DB") or os.getenv("DB_NAME") or "sales_forecast_db",
        user=os.getenv("POSTGRES_USER") or os.getenv("DB_USER") or "postgres",
        password=os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD") or "project",
        port=os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT") or "5432",
    )
