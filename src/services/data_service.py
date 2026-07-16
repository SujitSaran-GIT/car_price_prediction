import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from src.config import settings


class DataService:
    _df: Optional[pd.DataFrame] = None
    
    @classmethod
    def load_data(cls) -> pd.DataFrame:
        """Load CSV once and cache it in memory."""
        if cls._df is None:
            cls._df = pd.read_csv(settings.DATA_PATH)
            # Keep original messy data - don't clean yet
            cls._df = cls._df.replace({np.nan: None})
        return cls._df
    
    @classmethod
    def get_all_cars(
        cls,
        page: int = 1,
        page_size: int = 50,
        make: Optional[str] = None,
        model: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        fuel_type: Optional[str] = None,
        condition: Optional[str] = None,
        body_type: Optional[str] = None,
        registration_state: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        df = cls.load_data().copy()
        
        # Apply filters
        if make:
            df = df[df['make'].str.contains(make, case=False, na=False)]
        if model:
            df = df[df['model'].str.contains(model, case=False, na=False)]
        if fuel_type:
            df = df[df['fuel_type'].str.contains(fuel_type, case=False, na=False)]
        if condition:
            df = df[df['condition'].str.contains(condition, case=False, na=False)]
        if body_type:
            df = df[df['body_type'].str.contains(body_type, case=False, na=False)]
        if registration_state:
            df = df[df['registration_state'].str.upper() == registration_state.upper()]
        
        # Price filter (handle messy data - try to coerce)
        if min_price is not None or max_price is not None:
            price_numeric = pd.to_numeric(df['listing_price'], errors='coerce')
            if min_price is not None:
                df = df[price_numeric >= min_price]
            if max_price is not None:
                df = df[price_numeric <= max_price]
        
        # Year filter (handle messy data)
        if min_year is not None or max_year is not None:
            year_numeric = pd.to_numeric(df['year'], errors='coerce')
            if min_year is not None:
                df = df[year_numeric >= min_year]
            if max_year is not None:
                df = df[year_numeric <= max_year]
        
        # Sorting
        if sort_by and sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=(sort_order == "asc"), na_position='last')
        
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = df.iloc[start:end]
        
        return {
            "total_records": total,
            "page": page,
            "page_size": page_size,
            "returned_records": len(paginated),
            "data": paginated.to_dict(orient='records')
        }
    
    @classmethod
    def get_car_by_id(cls, car_id: str) -> Optional[Dict[str, Any]]:
        df = cls.load_data()
        result = df[df['car_id'] == car_id]
        if len(result) == 0:
            return None
        return result.iloc[0].to_dict()
    
    @classmethod
    def get_data_quality_report(cls) -> Dict[str, Any]:
        df = cls.load_data()
        
        # Calculate quality metrics on RAW data
        missing = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        
        price_numeric = pd.to_numeric(df['listing_price'], errors='coerce')
        neg_prices = int((price_numeric < 0).sum())
        price_outliers = int((price_numeric > 200000).sum())
        
        mileage_numeric = pd.to_numeric(df['mileage'], errors='coerce')
        neg_mileage = int((mileage_numeric < 0).sum())
        
        year_numeric = pd.to_numeric(df['year'], errors='coerce')
        invalid_years = int(((year_numeric < 1900) | (year_numeric > 2025)).sum())
        
        dtypes = {col: str(df[col].dtype) for col in df.columns}
        
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": missing,
            "duplicate_rows": int(duplicates),
            "negative_prices": neg_prices,
            "negative_mileage": neg_mileage,
            "invalid_years": invalid_years,
            "price_outliers": price_outliers,
            "data_types": dtypes,
            "sample_records": df.head(3).to_dict(orient='records')
        }
    
    @classmethod
    def get_unique_values(cls, column: str) -> List[Any]:
        df = cls.load_data()
        if column not in df.columns:
            return []
        return df[column].dropna().unique().tolist()
    
    @classmethod
    def get_summary_stats(cls) -> Dict[str, Any]:
        df = cls.load_data()
        
        # Try to get numeric stats where possible
        price_numeric = pd.to_numeric(df['listing_price'], errors='coerce')
        mileage_numeric = pd.to_numeric(df['mileage'], errors='coerce')
        year_numeric = pd.to_numeric(df['year'], errors='coerce')
        
        return {
            "price_stats": {
                "count": int(price_numeric.count()),
                "mean": round(float(price_numeric.mean()), 2) if price_numeric.count() > 0 else None,
                "median": round(float(price_numeric.median()), 2) if price_numeric.count() > 0 else None,
                "min": round(float(price_numeric.min()), 2) if price_numeric.count() > 0 else None,
                "max": round(float(price_numeric.max()), 2) if price_numeric.count() > 0 else None,
                "std": round(float(price_numeric.std()), 2) if price_numeric.count() > 0 else None
            },
            "mileage_stats": {
                "count": int(mileage_numeric.count()),
                "mean": round(float(mileage_numeric.mean()), 2) if mileage_numeric.count() > 0 else None,
                "median": round(float(mileage_numeric.median()), 2) if mileage_numeric.count() > 0 else None,
                "min": round(float(mileage_numeric.min()), 2) if mileage_numeric.count() > 0 else None,
                "max": round(float(mileage_numeric.max()), 2) if mileage_numeric.count() > 0 else None
            },
            "year_stats": {
                "count": int(year_numeric.count()),
                "mean": round(float(year_numeric.mean()), 1) if year_numeric.count() > 0 else None,
                "min": int(year_numeric.min()) if year_numeric.count() > 0 else None,
                "max": int(year_numeric.max()) if year_numeric.count() > 0 else None
            },
            "make_distribution": df['make'].value_counts().head(10).to_dict(),
            "fuel_type_distribution": df['fuel_type'].value_counts().head(10).to_dict(),
            "condition_distribution": df['condition'].value_counts().head(10).to_dict()
        }


data_service = DataService()