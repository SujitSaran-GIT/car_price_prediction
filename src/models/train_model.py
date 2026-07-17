"""
Train Linear Regression on RAW messy data.
Minimal handling, maximum logging. Tracks the 'useless' baseline.
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.database.db import (
    create_experiment, log_message, save_metrics, save_feature_importance,
    save_predictions, save_data_snapshot, update_experiment_status,
    get_experiment
)
from src.config import settings


def train_raw_model(
    experiment_name: str = "raw_baseline",
    description: str = "Trained on raw messy data without any preprocessing",
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Train a Linear Regression model on the RAW messy dataset.
    Logs EVERYTHING to the experiment tracking database.
    """
    # ─── Step 1: Load Raw Data ───
    print(f"[{datetime.now()}] Loading raw data from {settings.DATA_PATH}")
    df = pd.read_csv(settings.DATA_PATH)

    exp_id = create_experiment(
        name=experiment_name,
        description=description,
        data_path=str(settings.DATA_PATH),
        total_rows=len(df),
        rows_after_drop=0,
        features=[],
        target="listing_price",
        preprocessing={},
        model_type="LinearRegression",
        model_params={"fit_intercept": True, "copy_X": True, "n_jobs": None},
        model_path=str(Path(__file__).parent.parent / "data" / f"model_v{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    )

    log_message(exp_id, "INFO", f"Experiment {exp_id} started: {experiment_name}")
    log_message(exp_id, "INFO", f"Raw dataset loaded: {len(df)} rows, {len(df.columns)} columns")

    # ─── Step 2: Data Snapshot ───
    missing_total = int(df.isnull().sum().sum())
    dup_count = int(df.duplicated().sum())
    price_numeric = pd.to_numeric(df["listing_price"], errors="coerce")
    neg_target = int((price_numeric < 0).sum())
    outlier_target = int((price_numeric > 200000).sum())

    save_data_snapshot(exp_id, {
        "missing_count": missing_total,
        "duplicate_count": dup_count,
        "negative_target_count": neg_target,
        "outlier_count": outlier_target,
        "feature_dtypes": {col: str(df[col].dtype) for col in df.columns}
    })

    log_message(exp_id, "WARNING", f"Data Quality: {missing_total} missing, {dup_count} duplicates, {neg_target} negative prices, {outlier_target} outliers")

    # ─── Step 3: Handle Target ───
    log_message(exp_id, "INFO", "Converting target 'listing_price' to numeric...")
    df["listing_price"] = pd.to_numeric(df["listing_price"], errors="coerce")
    rows_before_drop = len(df)
    df = df.dropna(subset=["listing_price"])
    df = df[df["listing_price"] > 0]
    rows_after = len(df)

    log_message(exp_id, "WARNING", f"Dropped {rows_before_drop - rows_after} rows with invalid target. Remaining: {rows_after}")

    # ─── Step 4: Feature Selection ───
    log_message(exp_id, "INFO", "Selecting features: ONLY numeric columns...")
    
    numeric_features = []
    for col in df.columns:
        if col in ["listing_price", "car_id", "vin"]:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        valid_ratio = coerced.notna().sum() / len(df)
        if valid_ratio > 0.5:
            numeric_features.append(col)
            df[col] = coerced
            log_message(exp_id, "INFO", f"Feature '{col}': {valid_ratio:.1%} numeric, kept")

    log_message(exp_id, "INFO", f"Selected {len(numeric_features)} numeric features: {numeric_features}")

    # ─── Step 5: Handle Missing in Features ───
    X = df[numeric_features].copy()
    X = X.fillna(X.median())
    
    log_message(exp_id, "WARNING", f"Filled missing values with column medians")

    y = df["listing_price"].values

    # ─── Step 6: Train/Test Split WITH ORIGINAL INDICES ───
    indices = np.arange(len(df))
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, indices, test_size=test_size, random_state=random_state
    )
    
    log_message(exp_id, "INFO", f"Train/Test split: {len(X_train)} train, {len(X_test)} test")

    # ─── Step 7: Train Model ───
    log_message(exp_id, "INFO", "Training LinearRegression...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    # ─── Step 8: Predictions ───
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # ─── Step 9: Metrics ───
    metrics = {
        "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
        "train_mae": mean_absolute_error(y_train, y_pred_train),
        "train_r2": r2_score(y_train, y_pred_train),
        "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
        "test_mae": mean_absolute_error(y_test, y_pred_test),
        "test_r2": r2_score(y_test, y_pred_test),
        "test_mape": np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    }

    save_metrics(exp_id, metrics)
    log_message(exp_id, "INFO", f"Test R²: {metrics['test_r2']:.4f}, Test RMSE: ${metrics['test_rmse']:,.2f}")

    # ─── Step 10: Feature Importance ───
    save_feature_importance(exp_id, numeric_features, model.coef_.tolist())

    # ─── Step 11: Save Sample Predictions ───
    # FIX: idx_test contains ORIGINAL DataFrame indices
    sample_size = min(500, len(y_test))
    sample_positions = np.random.choice(len(y_test), sample_size, replace=False)
    
    actuals = y_test[sample_positions].tolist()
    preds = y_pred_test[sample_positions].tolist()
    
    # FIX: Map sample_positions back to original DataFrame indices
    test_indices = idx_test[sample_positions]
    car_ids = df.iloc[test_indices]["car_id"].tolist()
    
    save_predictions(exp_id, actuals, preds, car_ids)

    # ─── Step 12: Save Model ───
    model_path = Path(__file__).parent.parent / "data" / f"model_exp_{exp_id}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "features": numeric_features}, f)

    log_message(exp_id, "SUCCESS", f"Model saved to {model_path}")
    update_experiment_status(exp_id, "completed")

    return {
        "experiment_id": exp_id,
        "experiment_name": experiment_name,
        "metrics": metrics,
        "features_used": numeric_features,
        "model_path": str(model_path),
        "rows_used": rows_after,
        "message": "Raw baseline model trained and logged successfully"
    }


def predict_price(experiment_id: int, features: Dict[str, Any]) -> Dict[str, Any]:
    """Load a trained model and make prediction."""
    exp = get_experiment(experiment_id)
    if not exp:
        raise ValueError(f"Experiment {experiment_id} not found")

    model_path = exp["model_path"]
    with open(model_path, "rb") as f:
        artifact = pickle.load(f)

    model = artifact["model"]
    feature_names = artifact["features"]

    input_vector = []
    for feat in feature_names:
        val = features.get(feat, 0)
        try:
            input_vector.append(float(val))
        except (TypeError, ValueError):
            input_vector.append(0.0)

    prediction = model.predict([input_vector])[0]

    return {
        "experiment_id": experiment_id,
        "predicted_price": round(float(prediction), 2),
        "features_used": feature_names,
        "input_features": features
    }