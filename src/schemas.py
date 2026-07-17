from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date


class CarResponse(BaseModel):
    """Raw response model - accepts ANY type since data is intentionally messy."""
    car_id: Optional[Any] = None
    vin: Optional[Any] = None
    make: Optional[Any] = None
    model: Optional[Any] = None
    year: Optional[Any] = None
    mileage: Optional[Any] = None
    fuel_type: Optional[Any] = None
    transmission: Optional[Any] = None
    engine_size: Optional[Any] = None          # float, "2.5L", "392 cu in", None
    horsepower: Optional[Any] = None             # int, "635 hp", None
    color: Optional[Any] = None
    body_type: Optional[Any] = None
    condition: Optional[Any] = None
    owners: Optional[Any] = None
    accident_history: Optional[Any] = None
    title_status: Optional[Any] = None
    registration_state: Optional[Any] = None
    city: Optional[Any] = None
    zip_code: Optional[Any] = None             # string or float from pandas
    listing_date: Optional[Any] = None
    days_on_market: Optional[Any] = None
    seller_type: Optional[Any] = None
    has_navigation: Optional[Any] = None     # bool, "Yes", "1", 0, None
    has_leather_seats: Optional[Any] = None
    listing_price: Optional[Any] = None        # float, "$12,345.67", -5000, None
    
    class Config:
        from_attributes = True


class CarListResponse(BaseModel):
    total_records: int
    page: int
    page_size: int
    returned_records: int
    data: List[CarResponse]


class DataQualityReport(BaseModel):
    """Shows the messiness of the raw data."""
    total_rows: int
    total_columns: int
    missing_values: dict
    duplicate_rows: int
    negative_prices: int
    negative_mileage: int
    invalid_years: int
    price_outliers: int
    data_types: dict
    sample_records: List[dict]