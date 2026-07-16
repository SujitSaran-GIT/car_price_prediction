from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from src.services.data_service import data_service
from src.models import CarListResponse, DataQualityReport
from src.config import settings

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/", response_model=CarListResponse)
async def get_cars(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE, 
        ge=1, 
        le=settings.MAX_PAGE_SIZE, 
        description="Records per page"
    ),
    make: Optional[str] = Query(None, description="Filter by make (partial match)"),
    model: Optional[str] = Query(None, description="Filter by model (partial match)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_year: Optional[int] = Query(None, ge=1900, le=2025, description="Minimum year"),
    max_year: Optional[int] = Query(None, ge=1900, le=2025, description="Maximum year"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    body_type: Optional[str] = Query(None, description="Filter by body type"),
    registration_state: Optional[str] = Query(None, description="Filter by state (e.g., CA, TX)"),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order")
):
    """
    Get paginated list of used cars with optional filtering.
    Returns raw messy data as-is so you can see the data quality issues.
    """
    result = data_service.get_all_cars(
        page=page,
        page_size=page_size,
        make=make,
        model=model,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        fuel_type=fuel_type,
        condition=condition,
        body_type=body_type,
        registration_state=registration_state,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return result


@router.get("/{car_id}")
async def get_car(car_id: str):
    """
    Get a single car by its car_id.
    """
    car = data_service.get_car_by_id(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail=f"Car with id '{car_id}' not found")
    return car


@router.get("/stats/summary")
async def get_summary():
    """
    Get summary statistics about the dataset.
    Shows numeric stats despite messy data.
    """
    return data_service.get_summary_stats()


@router.get("/stats/quality", response_model=DataQualityReport)
async def get_quality_report():
    """
    Get a data quality report showing all the messiness in the raw data.
    This is your starting point for understanding what needs cleaning.
    """
    return data_service.get_data_quality_report()


@router.get("/columns/{column_name}/unique")
async def get_unique_values(column_name: str):
    """
    Get all unique values for a specific column.
    Useful for understanding categorical messiness (typos, inconsistencies).
    """
    if column_name not in data_service.load_data().columns:
        raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found")
    values = data_service.get_unique_values(column_name)
    return {"column": column_name, "unique_count": len(values), "values": values[:100]}