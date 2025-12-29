from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime,
    ForeignKey, UniqueConstraint, Numeric
)
from sqlalchemy.orm import relationship
from .database import Base


# ============================================================
# 1. PLANT
# ============================================================
class Plant(Base):
    __tablename__ = "PLANT"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    place = Column(String(255), nullable=True)
    capacity_mw = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)

    # 관계 (CRUD에서 실제로 사용하는 것만)
    weathers = relationship("Weather", back_populates="plant")
    generations = relationship("Generation", back_populates="plant")
    forecasts = relationship("Forecast", back_populates="plant")
    daily_forecasts = relationship("DailyForecast", back_populates="plant")
    realtime_generations = relationship("RealtimeGeneration", back_populates="plant")


# ============================================================
# 2. WEATHER
# ============================================================
class Weather(Base):
    __tablename__ = "WEATHER"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)
    timestamp = Column(DateTime, index=True)

    temperature = Column(Float, nullable=True)
    insolation = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("plant_id", "timestamp", name="_weather_uc"),
    )

    plant = relationship("Plant", back_populates="weathers")


# ============================================================
# 3. GENERATION (실제 발전량)  ← CRUD에서 사용 중
# ============================================================
class Generation(Base):
    __tablename__ = "GENERATION"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)
    timestamp = Column(DateTime, index=True)

    actual_power = Column(Float)   # CRUD에서 actual_power_mwh 안 씀

    __table_args__ = (
        UniqueConstraint("plant_id", "timestamp", name="_generation_uc"),
    )

    plant = relationship("Plant", back_populates="generations")


# ============================================================
# 4. FORECAST (시간별 예측) ← CRUD 핵심
# ============================================================
class Forecast(Base):
    __tablename__ = "FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)

    # ⚠️ CRUD 기준 필드명
    forecast_time = Column(DateTime, index=True)
    predicted_power = Column(Float)
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint(
            "plant_id", "forecast_time", "model_version",
            name="_forecast_uc"
        ),
    )

    plant = relationship("Plant", back_populates="forecasts")


# ============================================================
# 5. DAILY_FORECAST (일별 예측 합산)
# ============================================================
class DailyForecast(Base):
    __tablename__ = "DAILY_FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)

    # ⚠️ CRUD 기준 필드명
    forecast_date = Column(Date, index=True)
    total_power = Column(Float)
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint(
            "plant_id", "forecast_date", "model_version",
            name="_daily_forecast_uc"
        ),
    )

    plant = relationship("Plant", back_populates="daily_forecasts")


# ============================================================
# 6. REALTIME_GENERATION (실시간 예측 + 누적)
# ============================================================
class RealtimeGeneration(Base):
    __tablename__ = "REALTIME_GENERATION"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("PLANT.id"), index=True)

    timestamp = Column(DateTime, index=True)          # 매 정시
    predicted_power = Column(Float)                   # 해당 시간 예측
    cumulative_power = Column(Float)                  # 당일 누적
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint(
            "plant_id", "timestamp", "model_version",
            name="_realtime_generation_uc"
        ),
    )

    plant = relationship("Plant", back_populates="realtime_generations")
