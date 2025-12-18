import argparse
import os

from db import get_connection
from predict_lstm import run_prediction


def _ensure_tables(cur):
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


def _write_predictions(cur, forecast_type: str, predictions: list[dict]):
	cur.execute(
		"DELETE FROM predicted_sales WHERE forecast_type = %s",
		(forecast_type,),
	)

	for p in predictions:
		# Store as INT to match existing schema.
		cur.execute(
			"""
			INSERT INTO predicted_sales (forecast_type, forecast_date, amount)
			VALUES (%s, %s, %s)
			""",
			(
				forecast_type,
				p["date"],
				int(round(float(p["forecast"]))),
			),
		)


def main():
	parser = argparse.ArgumentParser(
		description="Generate ML forecasts and load them into predicted_sales table."
	)
	parser.add_argument(
		"--months",
		type=int,
		nargs="+",
		default=[12, 24],
		help="Forecast horizons to generate (default: 12 24)",
	)
	parser.add_argument(
		"--model_dir",
		default=None,
		help="Model dir (default: project_root/models)",
	)
	parser.add_argument(
		"--history",
		default=None,
		help="History dataset path (default: project_root/Assignment-3-ML-Sales_Transactions_Dataset_Weekly.csv)",
	)
	args = parser.parse_args()

	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	model_dir = args.model_dir or os.path.join(base_dir, "models")
	history_path = args.history or os.path.join(
		base_dir, "Assignment-3-ML-Sales_Transactions_Dataset_Weekly.csv"
	)

	conn = get_connection()
	cur = conn.cursor()
	try:
		_ensure_tables(cur)

		for m in args.months:
			forecast_type = "1year" if int(m) == 12 else "2year"
			result = run_prediction(
				model_dir=model_dir,
				history_path=history_path,
				predict_months=int(m),
			)
			_write_predictions(cur, forecast_type=forecast_type, predictions=result["predictions"])
			print(f"Loaded {len(result['predictions'])} rows for {forecast_type}")

		conn.commit()
	finally:
		cur.close()
		conn.close()


if __name__ == "__main__":
	main()
