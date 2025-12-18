from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# models 파일 경로에 맞게 수정 (같은 폴더면 .models)
from .models import (
    Plant,
    Weather,
    Forecast,
    DailyForecast,
    RealtimeGeneration,
)

# ----------------------------------------------------
# 🌱 PLANT CRUD
# ----------------------------------------------------
def get_all_plants(db: Session) -> List[Plant]:
    """모든 발전소 정보 조회"""
    return db.query(Plant).order_by(Plant.id.asc()).all()


def get_plant_by_id(db: Session, plant_id: int) -> Optional[Plant]:
    """특정 발전소 정보 조회"""
    return db.query(Plant).filter(Plant.id == plant_id).first()


# ----------------------------------------------------
# ☀️ WEATHER CRUD
# ----------------------------------------------------
def get_latest_weather(db: Session, plant_id: int) -> Optional[Weather]:
    """특정 발전소의 가장 최근 날씨 조회"""
    return (
        db.query(Weather)
        .filter(Weather.plant_id == plant_id)
        .order_by(Weather.timestamp.desc())
        .first()
    )


def get_weather_history(
    db: Session,
    plant_id: int,
    start_time: datetime,
    end_time: datetime,
) -> List[Weather]:
    """특정 기간의 날씨 기록 조회"""
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
# ⚡ REALTIME GENERATION CRUD
# ----------------------------------------------------
def get_latest_realtime_generation(
    db: Session, plant_id: int
) -> Optional[RealtimeGeneration]:
    """
    가장 최근에 저장된 실시간 발전량 데이터를 조회.
    (누적 발전량 계산 시 직전 데이터를 찾기 위해 사용)
    """
    return (
        db.query(RealtimeGeneration)
        .filter(RealtimeGeneration.plant_id == plant_id)
        .order_by(RealtimeGeneration.timestamp.desc())
        .first()
    )


def insert_realtime_generation(
    db: Session,
    plant_id: int,
    timestamp: datetime,
    predicted_power: float,
    cumulative_power: float,
    model_version: str
):
    """
    실시간 발전량 및 누적 발전량 저장.
    [수정됨]: 이미 같은 시간/발전소/모델의 데이터가 존재하면 UPDATE하고, 없으면 INSERT합니다.
    (Upsert 로직 구현)
    """
    # 1. 기존 데이터 확인
    existing = db.query(RealtimeGeneration).filter(
        RealtimeGeneration.plant_id == plant_id,
        RealtimeGeneration.timestamp == timestamp,
        RealtimeGeneration.model_version == model_version
    ).first()

    if existing:
        # 2. 존재하면 값 업데이트
        existing.predicted_power = predicted_power
        existing.cumulative_power = cumulative_power
        # (commit은 호출하는 쪽에서 수행)
    else:
        # 3. 없으면 새로 생성
        new_obj = RealtimeGeneration(
            plant_id=plant_id,
            timestamp=timestamp,
            predicted_power=predicted_power,
            cumulative_power=cumulative_power,
            model_version=model_version
        )
        db.add(new_obj)


# ----------------------------------------------------
# 🔮 FORECAST CRUD (시간별 예측 - 3일치)
# ----------------------------------------------------
def get_forecasts(
    db: Session,
    plant_id: int,
    start_time: datetime,
    end_time: datetime,
    model_version: Optional[str] = None,
) -> List[Forecast]:
    """특정 기간의 시간별 예측 데이터 조회"""
    query = db.query(Forecast).filter(
        Forecast.plant_id == plant_id,
        Forecast.forecast_time >= start_time,
        Forecast.forecast_time <= end_time,
    )

    if model_version:
        query = query.filter(Forecast.model_version == model_version)

    return query.order_by(Forecast.forecast_time.asc()).all()


def insert_hourly_forecast(
    db: Session,
    plant_id: int,
    forecast_time: datetime,
    predicted_power: float,
    model_version: str,
):
    """시간별 예측 데이터 1건 저장"""
    db.add(
        Forecast(
            plant_id=plant_id,
            forecast_time=forecast_time,
            predicted_power=predicted_power,
            model_version=model_version,
        )
    )


def delete_future_forecasts(
    db: Session,
    plant_id: int,
    from_time: datetime,
    model_version: Optional[str] = None,
):
    """특정 시점 이후의 모든 예측 데이터 삭제 (초기화용)"""
    query = db.query(Forecast).filter(
        Forecast.plant_id == plant_id,
        Forecast.forecast_time >= from_time,
    )

    if model_version:
        query = query.filter(Forecast.model_version == model_version)

    query.delete(synchronize_session=False)


def delete_forecasts_by_date_range(
    db: Session,
    plant_id: int,
    start_time: datetime,
    end_time: datetime,
    model_version: str,
):
    """
    [NEW] 특정 발전소의 특정 기간 예측 데이터를 삭제.
    (3일치 예측 갱신 시 기존 데이터를 지우기 위해 사용)
    """
    db.query(Forecast).filter(
        Forecast.plant_id == plant_id,
        Forecast.model_version == model_version,
        Forecast.forecast_time >= start_time,
        Forecast.forecast_time < end_time,
    ).delete(synchronize_session=False)


# ----------------------------------------------------
# 📅 DAILY FORECAST CRUD (일별 예측 - 3일치)
# ----------------------------------------------------
def get_daily_forecasts(
    db: Session,
    plant_id: int,
    start_date: date,
    end_date: date,
    model_version: Optional[str] = None,
) -> List[DailyForecast]:
    """특정 기간의 일별 예측 데이터 조회"""
    query = db.query(DailyForecast).filter(
        DailyForecast.plant_id == plant_id,
        DailyForecast.forecast_date >= start_date,
        DailyForecast.forecast_date <= end_date,
    )

    if model_version:
        query = query.filter(DailyForecast.model_version == model_version)

    return query.order_by(DailyForecast.forecast_date.asc()).all()


def rebuild_daily_forecast(
    db: Session,
    plant_id: int,
    model_version: str,
    start_date: date,
    end_date: date,
):
    """
    [NEW] 시간별 예측 데이터를 기반으로 일별 예측(DailyForecast) 테이블을 재구축합니다.
    1. 해당 기간의 기존 일별 예측 삭제
    2. 시간별 예측 데이터를 조회하여 날짜별로 합산
    3. 새로운 일별 예측 데이터 저장
    """

    # 1️⃣ 기존 일별 예측 삭제
    db.query(DailyForecast).filter(
        DailyForecast.plant_id == plant_id,
        DailyForecast.model_version == model_version,
        DailyForecast.forecast_date >= start_date,
        DailyForecast.forecast_date <= end_date,
    ).delete(synchronize_session=False)

    # 2️⃣ 시간별 예측 조회 (해당 기간 전체)
    # datetime.combine을 사용하여 date -> datetime 변환 (00:00:00 기준)
    query_start = datetime.combine(start_date, datetime.min.time())
    query_end = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

    rows = db.query(
        Forecast.forecast_time,
        Forecast.predicted_power,
    ).filter(
        Forecast.plant_id == plant_id,
        Forecast.model_version == model_version,
        Forecast.forecast_time >= query_start,
        Forecast.forecast_time < query_end,
    ).all()

    if not rows:
        print(f"⚠️ rebuild_daily_forecast: No forecast rows found for {start_date} ~ {end_date}")
        return

    # 3️⃣ 날짜별 합산 로직
    daily_sum = {}
    for ts, power in rows:
        d = ts.date()
        daily_sum[d] = daily_sum.get(d, 0.0) + float(power)

    # 4️⃣ 저장
    for d, total in daily_sum.items():
        db.add(DailyForecast(
            plant_id=plant_id,
            forecast_date=d,
            total_power=total,
            model_version=model_version,
        ))