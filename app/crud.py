from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

# SQLAlchemy 모델 임포트
from .models import Plant, Weather, Generation, Forecast, DailyForecast

# ----------------------------------------------------
# Plant CRUD
# ----------------------------------------------------
def get_all_plants(db: Session) -> List[Plant]:
    """모든 발전소 정보를 조회합니다."""
    return db.query(Plant).all()

# ----------------------------------------------------
# Weather CRUD
# ----------------------------------------------------
def get_latest_weather(db: Session, plant_id: int) -> Optional[Weather]:
    """특정 발전소의 가장 최근 기상 정보를 조회합니다."""
    return db.query(Weather).filter(
        Weather.plant_id == plant_id
    ).order_by(
        Weather.timestamp.desc()
    ).first()

# ----------------------------------------------------
# Generation CRUD
# ----------------------------------------------------
def get_latest_generation(db: Session, plant_id: int) -> Optional[Generation]:
    """특정 발전소의 가장 최근 실제 발전량을 조회합니다."""
    return db.query(Generation).filter(
        Generation.plant_id == plant_id
    ).order_by(
        Generation.timestamp.desc()
    ).first()

def get_generation_history(db: Session, plant_id: int, start_time: datetime, end_time: datetime) -> List[Generation]:
    """특정 발전소의 기간별 실제 발전량 기록을 조회합니다."""
    return db.query(Generation).filter(
        Generation.plant_id == plant_id,
        Generation.timestamp >= start_time,
        Generation.timestamp <= end_time
    ).order_by(
        Generation.timestamp.asc()
    ).all()

# ----------------------------------------------------
# Forecast CRUD
# ----------------------------------------------------
def get_forecasts(db: Session, plant_id: int, start_time: datetime, end_time: datetime) -> List[Forecast]:
    """특정 발전소의 기간별 시간별 예측 발전량을 조회합니다."""
    return db.query(Forecast).filter(
        Forecast.plant_id == plant_id,
        Forecast.timestamp >= start_time,
        Forecast.timestamp <= end_time
    ).order_by(
        Forecast.timestamp.asc()
    ).all()

def get_daily_forecasts(
    db: Session, 
    plant_id: int, 
    start_date: date, 
    end_date: date, 
    model_version: Optional[str] = None
) -> List[DailyForecast]:
    """특정 발전소의 일별 예측 합산 결과를 조회합니다."""
    query = db.query(DailyForecast).filter(
        DailyForecast.plant_id == plant_id,
        DailyForecast.date >= start_date,
        DailyForecast.date <= end_date
    )
    if model_version:
        query = query.filter(DailyForecast.model_version == model_version)
        
    return query.order_by(
        DailyForecast.date.asc()
    ).all()