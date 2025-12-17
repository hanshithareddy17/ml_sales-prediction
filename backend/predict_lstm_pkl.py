"""
Lightweight inference using TensorFlow SavedModel + loaded scaler.
Keeps TensorFlow but skips unnecessary overhead.
"""

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from datetime import datetime, timedelta


def load_inference_components(model_dir: str) -> tuple:
    """Load SavedModel and scaler from model_dir."""
    saved_model_path = Path(model_dir) / "lstm_saved_model"
    scaler_path = Path(model_dir) / "scaler.pkl"
    
    model = tf.keras.models.load_model(str(saved_model_path))
    scaler = joblib.load(str(scaler_path))
    
    return model, scaler


def forecast_with_pkl(
    model_dir: str,
    history_path: str,
    predict_months: int = 12,
) -> pd.DataFrame:
    """
    Generate forecasts using SavedModel and scaler.
    
    Args:
        model_dir: Path to models directory with lstm_saved_model/ and scaler.pkl
        history_path: Path to CSV with historical sales data
        predict_months: Number of months to forecast
        
    Returns:
        DataFrame with 'date' and 'forecast' columns
    """
    # Load model and scaler
    model, scaler = load_inference_components(model_dir)
    lookback = 12  # Default lookback from training
    
    # Load history
    df_history = pd.read_csv(history_path)
    df_history["date"] = pd.to_datetime(df_history["date"])
    
    # Get the 'sales' column (or first numeric column if 'sales' doesn't exist)
    if "total_sales" in df_history.columns:
        sales_col = "total_sales"
    elif "sales" in df_history.columns:
        sales_col = "sales"
    else:
        # Find first numeric column
        numeric_cols = df_history.select_dtypes(include=[np.number]).columns
        sales_col = numeric_cols[0] if len(numeric_cols) > 0 else None
    
    if sales_col is None:
        raise ValueError("Could not find sales column in history file")
    
    # Prepare last lookback values for forecasting
    last_values = df_history[sales_col].tail(lookback).values.reshape(-1, 1)
    last_values_scaled = scaler.transform(last_values).flatten()
    
    forecasts = []
    current_date = df_history["date"].max()
    
    # Generate multi-step forecast
    for step in range(predict_months):
        # Prepare input with correct shape
        x_input = last_values_scaled[-lookback:].reshape(1, lookback, 1)
        
        # Predict next value
        y_pred = model.predict(x_input, verbose=0)
        y_pred_value = y_pred[0, 0]
        
        # Inverse transform to get actual sales value
        y_pred_actual = scaler.inverse_transform(np.array([[y_pred_value]]))[0, 0]
        
        # Store forecast
        current_date += timedelta(days=30)  # Approximate month
        forecasts.append({"date": current_date, "forecast": max(0, y_pred_actual)})
        
        # Update sequence for next prediction
        last_values_scaled = np.append(last_values_scaled[1:], y_pred_value)
    
    return pd.DataFrame(forecasts)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Lightweight inference using SavedModel + scaler."
    )
    parser.add_argument(
        "--model_dir",
        default="models",
        help="Path to models directory (with lstm_saved_model/ and scaler.pkl)",
    )
    parser.add_argument(
        "--history",
        required=True,
        help="Path to CSV with historical data",
    )
    parser.add_argument(
        "--predict_months",
        type=int,
        default=12,
        help="Number of months to forecast",
    )
    parser.add_argument(
        "--output",
        help="Optional: save forecasts to JSON",
    )
    
    args = parser.parse_args()
    
    # Generate forecast
    df = forecast_with_pkl(args.model_dir, args.history, args.predict_months)
    
    print("\nForecast (first 5 rows):")
    print(df.head().to_string(index=False))
    
    # Save if requested
    if args.output:
        df.to_json(args.output, orient="records", date_format="iso")
        print(f"\n✓ Forecasts saved to {args.output}")
