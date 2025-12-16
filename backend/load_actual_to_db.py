import os

import pandas as pd
from db import get_connection


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "Assignment-3-ML-Sales_Transactions_Dataset_Weekly.csv")

def load_actual():
    df = pd.read_csv(CSV_PATH)

    weekly_cols = [c for c in df.columns if c.startswith("W")]
    weekly_sum = df[weekly_cols].sum()

    conn = get_connection()
    cur = conn.cursor()

    # Ensure required tables exist (idempotent for dev/first setup)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS actual_sales (
            id SERIAL PRIMARY KEY,
            month INT NOT NULL,
            year INT NOT NULL,
            amount INT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predicted_sales (
            id SERIAL PRIMARY KEY,
            forecast_type VARCHAR(10) NOT NULL,
            forecast_date DATE NOT NULL,
            amount INT NOT NULL
        )
        """
    )

    

    year = 2025
    month = 1

    for value in weekly_sum[:12]:
        cur.execute(
            "INSERT INTO actual_sales (month, year, amount) VALUES (%s,%s,%s)",
            (month, year, int(value))
        )
        month += 1

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_actual()
