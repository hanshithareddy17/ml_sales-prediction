"""
Note: TensorFlow SavedModel cannot be pickled. 
Instead, we keep the model in SavedModel format and only pickle the scaler.
The backend loads both: SavedModel for the model and the scaler.pkl for predictions.
"""

import joblib
import os

# Import the prediction functions
from predict_lstm import load_scaler, load_metadata


def create_scaler_pickle(model_dir: str, output_pkl: str) -> None:
    """
    Extract scaler and metadata and save as .pkl for lightweight backend.
    
    Args:
        model_dir: Directory containing lstm_saved_model/ and scaler.pkl
        output_pkl: Path to save the scaler wrapper (.pkl)
    """
    print(f"Loading scaler from {model_dir}...")
    
    # Load metadata to get lookback
    metadata = load_metadata(model_dir)
    lookback = int(metadata.get("lookback", 12))
    
    # Load the scaler
    scaler = load_scaler(model_dir)
    
    # Create a wrapper with just the scaler and metadata (no TensorFlow model)
    scaler_wrapper = {
        "scaler": scaler,
        "lookback": lookback,
        "metadata": metadata,
    }
    
    # Save to pickle
    print(f"Saving scaler wrapper to {output_pkl}...")
    joblib.dump(scaler_wrapper, output_pkl, compress=3)
    print(f"✓ Scaler saved successfully! File size: {os.path.getsize(output_pkl) / 1024:.2f} KB")
    print("\nNote: Use SavedModel from models/lstm_saved_model/ for inference.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract scaler and metadata to lightweight pickle."
    )
    parser.add_argument(
        "--model_dir",
        default="models",
        help="Directory with lstm_saved_model/, scaler.pkl, metadata.json",
    )
    parser.add_argument(
        "--output",
        default="models/scaler_wrapper.pkl",
        help="Path to save the scaler .pkl file",
    )
    
    args = parser.parse_args()
    
    create_scaler_pickle(args.model_dir, args.output)
