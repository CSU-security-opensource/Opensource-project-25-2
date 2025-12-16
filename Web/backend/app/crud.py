from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.orm import Session

# SQLAlchemy 모델 임포트
from .models import Plant, Weather, Generation, Forecast, DailyForecast


# ----------------------------------------------------
# 🌱 PLANT CRUD
# ----------------------------------------------------
def get_all_plants(db: Session) -> List[Plant]:
    """모든 발전소 정보를 ID 순서대로 조회"""
    return db.query(Plant).order_by(Plant.id.asc()).all()


def get_plant_by_id(db: Session, plant_id: int) -> Optional[Plant]:
    """특정 발전소를 ID로 조회"""
    return db.query(Plant).filter(Plant.id == plant_id).first()


# ----------------------------------------------------
# ☀️ WEATHER CRUD
# ----------------------------------------------------
def get_latest_weather(db: Session, plant_id: int) -> Optional[Weather]:
    """특정 발전소의 가장 최근 기상 정보 조회"""
    return (
        db.query(Weather)
        .filter(Weather.plant_id == plant_id)
        .order_by(Weather.timestamp.desc())
        .first()
    )


def get_weather_history(
    db: Session, plant_id: int, start_time: datetime, end_time: datetime
) -> List[Weather]:
    """특정 발전소의 기간별 기상 데이터 조회"""
    return (
        db.query(Weather)
        .filter(
            Weather.plant_id == plant_id,
            Weather.timestamp >= start_time,
            Weather.timestamp <= end_time,
        )
        .order_by(Weather.timestamp.asc())
        .all()
    )


# ----------------------------------------------------
# ⚡ GENERATION CRUD
# ----------------------------------------------------
def get_latest_generation(db: Session, plant_id: int) -> Optional[Generation]:
    """특정 발전소의 가장 최근 실제 발전량 조회"""
    return (
        db.query(Generation)
        .filter(Generation.plant_id == plant_id)
        .order_by(Generation.timestamp.desc())
        .first()
    )


def get_generation_history(
    db: Session, plant_id: int, start_time: datetime, end_time: datetime
) -> List[Generation]:
    """특정 발전소의 기간별 실제 발전량 기록 조회"""
    return (
        db.query(Generation)
        .filter(
            Generation.plant_id == plant_id,
            Generation.timestamp >= start_time,
            Generation.timestamp <= end_time,
        )
        .order_by(Generation.timestamp.asc())
        .all()
    )


# ----------------------------------------------------
# 🔮 FORECAST CRUD
# ----------------------------------------------------
def get_forecasts(
    db: Session, plant_id: int, start_time: datetime, end_time: datetime
) -> List[Forecast]:
    """특정 발전소의 시간대별 예측 발전량 조회"""
    return (
        db.query(Forecast)
        .filter(
            Forecast.plant_id == plant_id,
            Forecast.timestamp >= start_time,
            Forecast.timestamp <= end_time,
        )
        .order_by(Forecast.timestamp.asc())
        .all()
    )


# ----------------------------------------------------
# 📅 DAILY FORECAST CRUD
# ----------------------------------------------------
def get_daily_forecasts(
    db: Session,
    plant_id: int,
    start_date: date,
    end_date: date,
    model_version: Optional[str] = None,
) -> List[DailyForecast]:
    """특정 발전소의 일별 예측 합산 데이터를 조회"""
    query = db.query(DailyForecast).filter(
        DailyForecast.plant_id == plant_id,
        DailyForecast.date >= start_date,
        DailyForecast.date <= end_date,
    )

    if model_version is not None:
        query = query.filter(DailyForecast.model_version == model_version)

    return query.order_by(DailyForecast.date.asc()).all()
