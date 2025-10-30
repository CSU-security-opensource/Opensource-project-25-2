from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class Config:
    # SQLAlchemy 모델 객체를 Pydantic 객체로 변환할 수 있도록 설정
    from_attributes = True

# --- Base Schemas ---
class PlantBase(BaseModel):
    name: str
    place: str
    capacity_mw: float
    start_date: date
    latitude: float
    longitude: float

class WeatherBase(BaseModel):
    plant_id: int
    timestamp: datetime
    temperature: float
    insolation: float
    humidity: Optional[float] = None
    cloud_cover: Optional[float] = None
    snowfall: Optional[float] = None

class GenerationBase(BaseModel):
    plant_id: int
    timestamp: datetime
    actual_power_mwh: float

class ForecastBase(BaseModel):
    plant_id: int
    timestamp: datetime
    predicted_power_mwh: float
    model_version: str

class DailyForecastBase(BaseModel):
    plant_id: int
    date: date
    total_predicted_power_mwh: float
    model_version: str

# --- Read/Response Schemas ---
# API 응답 시 id를 포함합니다.
class Plant(PlantBase):
    id: int
    class Config(Config):
        pass

class Weather(WeatherBase):
    id: int
    class Config(Config):
        pass

class Generation(GenerationBase):
    id: int
    class Config(Config):
        pass

class Forecast(ForecastBase):
    id: int
    class Config(Config):
        pass

class DailyForecast(DailyForecastBase):
    id: int
    class Config(Config):
        pass