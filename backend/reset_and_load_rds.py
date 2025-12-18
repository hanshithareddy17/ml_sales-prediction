import argparse

from db import get_connection


def reset_tables():
	conn = get_connection()
	cur = conn.cursor()
	try:
		# Drop data only (keep schema)
		cur.execute("TRUNCATE TABLE predicted_sales RESTART IDENTITY")
		cur.execute("TRUNCATE TABLE actual_sales RESTART IDENTITY")
		conn.commit()
		print("Truncated predicted_sales and actual_sales")
	finally:
		cur.close()
		conn.close()


def main():
	parser = argparse.ArgumentParser(
		description="Delete existing RDS data and reload actuals + predictions."
	)
	parser.add_argument("--year", type=int, default=2025, help="Year label for actuals")
	parser.add_argument(
		"--months",
		type=int,
		nargs="+",
		default=[12, 24],
		help="Forecast horizons to load (default: 12 24)",
	)
	args = parser.parse_args()

	# Ensure tables exist by importing the loaders (they create tables)
	from load_actual_to_db import load_actual
	from load_predictions_to_db import main as load_preds_main

	# Create tables if missing
	conn = get_connection()
	cur = conn.cursor()
	try:
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
		conn.commit()
	finally:
		cur.close()
		conn.close()

	reset_tables()
	load_actual(year=args.year)
	print("Loaded actual_sales")

	# Call the predictions loader as a script-like function
	import sys

	old_argv = sys.argv
	try:
		sys.argv = [old_argv[0], "--months", *[str(m) for m in args.months]]
		load_preds_main()
	finally:
		sys.argv = old_argv


if __name__ == "__main__":
	main()
