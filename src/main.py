from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import cars, models
from src.config import settings
from src.services.data_service import data_service
from src.database.db import init_db

init_db()

# Pre-load data on startup
data_service.load_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    Used Car Price Prediction API - Raw Messy Data Edition.
    
    This API serves the uncleaned, raw dataset so you can understand
    the data quality issues before building your Linear Regression model.
    
    ## Endpoints
    
    * **/cars/** - List all cars with pagination & filtering
    * **/cars/{car_id}** - Get a specific car
    * **/cars/stats/summary** - Summary statistics
    * **/cars/stats/quality** - Data quality report (the messiness!)
    * **/cars/columns/{column}/unique** - Unique values per column
    """,
    contact={
        "name": "Your Name",
        "email": "your.email@example.com"
    }
)

# CORS - allow browser requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cars.router)
app.include_router(models.router)

@app.get("/")
async def root():
    return {
        "message": "Used Car Price Prediction API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "total_cars": len(data_service.load_data()),
        "endpoints": {
            "cars": "/cars/",
            "car_detail": "/cars/{car_id}",
            "summary": "/cars/stats/summary",
            "quality": "/cars/stats/quality",
            "unique_values": "/cars/columns/{column_name}/unique",
            "experiments": "/models/",
            "train": "POST /models/train",
            "predict": "POST /models/predict"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "data_loaded": data_service._df is not None}