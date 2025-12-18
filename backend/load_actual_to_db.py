import os
import argparse

import pandas as pd
from db import get_connection


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "Assignment-3-ML-Sales_Transactions_Dataset_Weekly.csv")


def _ensure_tables(cur):
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


def load_actual(year: int = 2025, csv_path: str = CSV_PATH):
    df = pd.read_csv(CSV_PATH)

    weekly_cols = [c for c in df.columns if isinstance(c, str) and c.strip().upper().startswith("W")]
    weekly_sum = df[weekly_cols].sum(axis=0).astype(float).values

    # Map weekly totals onto real-ish dates for the requested calendar year.
    start = pd.Timestamp(year=year, month=1, day=1)
    start_monday = start + pd.Timedelta(days=(7 - start.weekday()) % 7)
    weekly_dates = pd.date_range(start=start_monday, periods=len(weekly_sum), freq="W-MON")
    weekly_series = pd.Series(weekly_sum, index=weekly_dates)
    monthly = weekly_series.resample("MS").sum()

    conn = get_connection()
    cur = conn.cursor()

    _ensure_tables(cur)

    # Replace actuals for the given year (idempotent)
    cur.execute("DELETE FROM actual_sales WHERE year = %s", (int(year),))

    for d, v in monthly.items():
        cur.execute(
            "INSERT INTO actual_sales (month, year, amount) VALUES (%s,%s,%s)",
            (int(d.month), int(d.year), int(round(float(v)))),
        )

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load monthly actuals into actual_sales table.")
    parser.add_argument("--year", type=int, default=2025, help="Calendar year to label actuals")
    parser.add_argument("--csv", default=CSV_PATH, help="Path to the assignment CSV")
    args = parser.parse_args()
    load_actual(year=args.year, csv_path=args.csv)
