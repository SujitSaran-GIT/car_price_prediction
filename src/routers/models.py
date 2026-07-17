"""
Model Training & Experiment Tracking API Router
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from src.models.train_model import train_raw_model, predict_price
from src.database.db import (
    get_all_experiments, get_experiment, get_experiment_metrics,
    get_experiment_features, get_experiment_predictions, get_experiment_logs,
    get_experiment_snapshot
)

router = APIRouter(prefix="/models", tags=["Model Training & Experiments"])


class TrainRequest(BaseModel):
    experiment_name: str = Field(default="raw_baseline_v1", description="Name for this experiment")
    description: str = Field(default="Raw messy data baseline", description="What this experiment tests")
    test_size: float = Field(default=0.2, ge=0.1, le=0.5, description="Test split ratio")
    random_state: int = Field(default=42, description="Random seed for reproducibility")


class PredictRequest(BaseModel):
    experiment_id: int = Field(..., description="Which experiment/model to use")
    features: Dict[str, Any] = Field(..., description="Feature values for prediction")


class ExperimentResponse(BaseModel):
    id: int
    experiment_name: str
    created_at: str
    description: str
    status: str
    total_rows: int
    rows_after_drop: int
    model_type: str
    metrics_summary: Optional[str] = None


# ─── Endpoints ───

@router.post("/train")
async def train_model(request: TrainRequest):
    """
    Train a Linear Regression model on RAW data.
    Logs everything to the experiment tracking database.
    """
    try:
        result = train_raw_model(
            experiment_name=request.experiment_name,
            description=request.description,
            test_size=request.test_size,
            random_state=request.random_state
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ExperimentResponse])
async def list_experiments():
    """
    Get all experiments ordered by newest first.
    See your journey from useless → valuable model.
    """
    experiments = get_all_experiments()
    return experiments


@router.get("/{experiment_id}")
async def get_experiment_details(experiment_id: int):
    """
    Get full details of a specific experiment.
    """
    exp = get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
    
    # Enrich with related data
    exp = dict(exp)
    exp["metrics"] = get_experiment_metrics(experiment_id)
    exp["features"] = get_experiment_features(experiment_id)
    exp["snapshot"] = get_experiment_snapshot(experiment_id)
    exp["logs"] = get_experiment_logs(experiment_id)[-20:]  # Last 20 logs
    
    return exp


@router.get("/{experiment_id}/metrics")
async def get_metrics(experiment_id: int):
    """
    Get all metrics for an experiment.
    """
    metrics = get_experiment_metrics(experiment_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found")
    return {
        "experiment_id": experiment_id,
        "metrics": metrics
    }


@router.get("/{experiment_id}/features")
async def get_features(experiment_id: int):
    """
    Get feature coefficients (importance) for an experiment.
    """
    features = get_experiment_features(experiment_id)
    return {
        "experiment_id": experiment_id,
        "feature_count": len(features),
        "features": features
    }


@router.get("/{experiment_id}/predictions")
async def get_predictions(
    experiment_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Number of predictions to return")
):
    """
    Get worst predictions (highest residuals) for analysis.
    """
    preds = get_experiment_predictions(experiment_id, limit)
    return {
        "experiment_id": experiment_id,
        "returned": len(preds),
        "predictions": preds
    }


@router.get("/{experiment_id}/logs")
async def get_logs(experiment_id: int):
    """
    Get training logs to see what the model had to deal with.
    """
    logs = get_experiment_logs(experiment_id)
    return {
        "experiment_id": experiment_id,
        "log_count": len(logs),
        "logs": logs
    }


@router.post("/predict")
async def make_prediction(request: PredictRequest):
    """
    Make a price prediction using a trained experiment model.
    """
    try:
        result = predict_price(request.experiment_id, request.features)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{exp_id_1}/{exp_id_2}")
async def compare_experiments(exp_id_1: int, exp_id_2: int):
    """
    Compare two experiments side-by-side.
    """
    exp1 = get_experiment(exp_id_1)
    exp2 = get_experiment(exp_id_2)
    
    if not exp1 or not exp2:
        raise HTTPException(status_code=404, detail="One or both experiments not found")
    
    m1 = get_experiment_metrics(exp_id_1)
    m2 = get_experiment_metrics(exp_id_2)
    
    return {
        "experiment_1": {"id": exp_id_1, "name": exp1["experiment_name"], "metrics": m1},
        "experiment_2": {"id": exp_id_2, "name": exp2["experiment_name"], "metrics": m2},
        "winner": exp_id_1 if m1.get("test_r2", -999) > m2.get("test_r2", -999) else exp_id_2
    }