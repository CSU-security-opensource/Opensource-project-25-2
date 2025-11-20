from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime,
    ForeignKey, UniqueConstraint, Numeric
)
from sqlalchemy.orm import relationship
from .database import Base


# 1. PLANT (발전소 고유 정보)
class Plant(Base):
    __tablename__ = "PLANT"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    place = Column(String(255), nullable=True)           # ✅ 위치명 유지
    capacity_mw = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)      # ✅ 위도 추가
    longitude = Column(Numeric(9, 6), nullable=True)     # ✅ 경도 추가

    # 관계 정의
    weathers = relationship("Weather", back_populates="plant")
    generations = relationship("Generation", back_populates="plant")
    forecasts = relationship("Forecast", back_populates="plant")
    daily_forecasts = relationship("DailyForecast", back_populates="plant")


# 2. WEATHER (시간별 기상 데이터)
class Weather(Base):
    __tablename__ = "WEATHER"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float, nullable=True)
    insolation = Column(Float, nullable=True)             # ☀️ 일사량
    humidity = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)            # ☁️ 구름량
    # ❌ snowfall 제거됨

    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', name='_plant_timestamp_uc'),
    )

    plant = relationship("Plant", back_populates="weathers")


# 3. GENERATION (실제 발전량)
class Generation(Base):
    __tablename__ = "GENERATION"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    actual_power_mwh = Column(Float)

    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', name='_gen_plant_timestamp_uc'),
    )

    plant = relationship("Plant", back_populates="generations")


# 4. FORECAST (시간별 발전 예측)
class Forecast(Base):
    __tablename__ = "FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    predicted_power_mwh = Column(Float)
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', 'model_version', name='_fc_plant_ts_ver_uc'),
    )

    plant = relationship("Plant", back_populates="forecasts")


# 5. DAILY_FORECAST (일별 예측 합산)
class DailyForecast(Base):
    __tablename__ = "DAILY_FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    date = Column(Date, index=True)
    total_predicted_power_mwh = Column(Float)
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint('plant_id', 'date', 'model_version', name='_dfc_plant_date_ver_uc'),
    )

    plant = relationship("Plant", back_populates="daily_forecasts")


# 6. WEATHER_FORECAST (예보 데이터 저장용 - main.py에서 사용)
class WeatherForecast(Base):
    __tablename__ = "WEATHER_FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)
    forecast_datetime = Column(DateTime, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    sky_condition = Column(String(50), nullable=True)
    precipitation_type = Column(String(50), nullable=True)
    precipitation_probability = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=True)

    plant = relationship("Plant")
