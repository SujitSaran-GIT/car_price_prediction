"""
SQLite database for tracking every model experiment.
Records the journey from useless → valuable model.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "experiments.db"


def init_db():
    """Create all tables for experiment tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ─── Experiments Table ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            data_path TEXT,
            total_rows INTEGER,
            rows_after_drop INTEGER,
            features_used TEXT,          -- JSON list
            target_column TEXT,
            preprocessing_steps TEXT,    -- JSON dict
            model_type TEXT,
            model_params TEXT,           -- JSON dict
            model_path TEXT,
            status TEXT DEFAULT 'running'  -- running, completed, failed
        )
    """)

    # ─── Metrics Table ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            metric_name TEXT,
            metric_value REAL,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    # ─── Feature Importance (Coefficients) ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feature_importance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            feature_name TEXT,
            coefficient REAL,
            abs_coefficient REAL,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    # ─── Predictions Sample ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            actual REAL,
            predicted REAL,
            residual REAL,
            car_id TEXT,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    # ─── Data Quality Snapshot ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            missing_count INTEGER,
            duplicate_count INTEGER,
            negative_target_count INTEGER,
            outlier_count INTEGER,
            feature_dtypes TEXT,  -- JSON
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    # ─── Training Logs ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            log_level TEXT,
            message TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    """)

    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_experiment(
    name: str,
    description: str,
    data_path: str,
    total_rows: int,
    rows_after_drop: int,
    features: List[str],
    target: str,
    preprocessing: Dict[str, Any],
    model_type: str,
    model_params: Dict[str, Any],
    model_path: str
) -> int:
    """Create a new experiment record. Returns experiment_id."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO experiments 
        (experiment_name, description, data_path, total_rows, rows_after_drop,
         features_used, target_column, preprocessing_steps, model_type, model_params, model_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, description, data_path, total_rows, rows_after_drop,
        json.dumps(features), target, json.dumps(preprocessing),
        model_type, json.dumps(model_params), model_path
    ))
    exp_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exp_id


def log_message(experiment_id: int, level: str, message: str):
    """Log a training message."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO training_logs (experiment_id, log_level, message)
        VALUES (?, ?, ?)
    """, (experiment_id, level, message))
    conn.commit()
    conn.close()


def save_metrics(experiment_id: int, metrics: Dict[str, float]):
    """Save performance metrics."""
    conn = get_db()
    cursor = conn.cursor()
    for name, value in metrics.items():
        cursor.execute("""
            INSERT INTO metrics (experiment_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        """, (experiment_id, name, value))
    conn.commit()
    conn.close()


def save_feature_importance(experiment_id: int, features: List[str], coefficients: List[float]):
    """Save model coefficients."""
    conn = get_db()
    cursor = conn.cursor()
    for feat, coef in zip(features, coefficients):
        cursor.execute("""
            INSERT INTO feature_importance (experiment_id, feature_name, coefficient, abs_coefficient)
            VALUES (?, ?, ?, ?)
        """, (experiment_id, feat, coef, abs(coef)))
    conn.commit()
    conn.close()


def save_predictions(experiment_id: int, actuals: List[float], predictions: List[float], car_ids: List[str]):
    """Save sample predictions."""
    conn = get_db()
    cursor = conn.cursor()
    for act, pred, cid in zip(actuals, predictions, car_ids):
        cursor.execute("""
            INSERT INTO predictions (experiment_id, actual, predicted, residual, car_id)
            VALUES (?, ?, ?, ?, ?)
        """, (experiment_id, act, pred, act - pred, cid))
    conn.commit()
    conn.close()


def save_data_snapshot(experiment_id: int, snapshot: Dict[str, Any]):
    """Save data quality snapshot at training time."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO data_snapshots 
        (experiment_id, missing_count, duplicate_count, negative_target_count, outlier_count, feature_dtypes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        experiment_id,
        snapshot.get("missing_count", 0),
        snapshot.get("duplicate_count", 0),
        snapshot.get("negative_target_count", 0),
        snapshot.get("outlier_count", 0),
        json.dumps(snapshot.get("feature_dtypes", {}))
    ))
    conn.commit()
    conn.close()


def update_experiment_status(experiment_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE experiments SET status = ? WHERE id = ?", (status, experiment_id))
    conn.commit()
    conn.close()


def get_experiment(experiment_id: int) -> Optional[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_all_experiments() -> List[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, 
               GROUP_CONCAT(m.metric_name || ':' || ROUND(m.metric_value, 4), ', ') as metrics_summary
        FROM experiments e
        LEFT JOIN metrics m ON e.id = m.experiment_id
        GROUP BY e.id
        ORDER BY e.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_experiment_metrics(experiment_id: int) -> Dict[str, float]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT metric_name, metric_value FROM metrics WHERE experiment_id = ?", (experiment_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row["metric_name"]: row["metric_value"] for row in rows}


def get_experiment_features(experiment_id: int) -> List[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT feature_name, coefficient, abs_coefficient 
        FROM feature_importance 
        WHERE experiment_id = ?
        ORDER BY abs_coefficient DESC
    """, (experiment_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_experiment_predictions(experiment_id: int, limit: int = 100) -> List[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE experiment_id = ? 
        ORDER BY ABS(residual) DESC
        LIMIT ?
    """, (experiment_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_experiment_logs(experiment_id: int) -> List[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM training_logs 
        WHERE experiment_id = ? 
        ORDER BY logged_at ASC
    """, (experiment_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_experiment_snapshot(experiment_id: int) -> Optional[Dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data_snapshots WHERE experiment_id = ?", (experiment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# Initialize on import
init_db()