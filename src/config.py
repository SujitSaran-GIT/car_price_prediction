from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Car Price Prediction"
    PROJECT_VERSION: str = "0.1.0"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_PATH: Path = Path(__file__).parent.parent / "data" / "generated_data.csv"
    MODEL_DIR: Path = BASE_DIR / "models"
    LOG_DIR: Path = BASE_DIR / "logs"
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()