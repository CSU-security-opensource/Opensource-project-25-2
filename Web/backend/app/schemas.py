from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class Config:
    # SQLAlchemy 모델 객체를 Pydantic 객체로 변환할 수 있도록 설정
    from_attributes = True


# --- Base Schemas ---
class PlantBase(BaseModel):
    name: str
    place: Optional[str] = None
    capacity_mw: Optional[float] = None
    start_date: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WeatherBase(BaseModel):
    plant_id: int
    timestamp: datetime
    temperature: Optional[float] = None
    insolation: Optional[float] = None
    humidity: Optional[float] = None
    cloud_cover: Optional[float] = None
    # ❌ snowfall 제거됨 (DB에 없음)


class GenerationBase(BaseModel):
    plant_id: int
    timestamp: datetime
    actual_power_mwh: Optional[float] = None


class ForecastBase(BaseModel):
    plant_id: int
    timestamp: datetime
    predicted_power_mwh: Optional[float] = None
    model_version: Optional[str] = None


class DailyForecastBase(BaseModel):
    plant_id: int
    date: date
    total_predicted_power_mwh: Optional[float] = None
    model_version: Optional[str] = None


# --- Read/Response Schemas ---
# API 응답 시 id ss포함
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
