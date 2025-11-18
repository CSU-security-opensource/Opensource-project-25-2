from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional

# Custom modules
from . import schemas
from . import crud
from .models import Base, Plant, Generation, Forecast, Weather, DailyForecast
from .weather_service import get_current_weather
from .solar_service import get_kier_solar   # ✅ 올바른 import만 유지!

# ----------------------------------------------------
# DB CONNECTION SETUP
# ----------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되어 있지 않습니다.")

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """요청마다 DB 세션 생성 및 종료"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------
# APPLICATION INSTANCE
# ----------------------------------------------------
app = FastAPI(
    title="신재생 에너지 발전량 예측 플랫폼 API",
    description="태양광 발전소의 실시간 데이터 및 예측을 제공합니다."
)


# ----------------------------------------------------
# ROUTES (API Endpoints)
# ----------------------------------------------------

@app.get("/plants", response_model=List[schemas.Plant], tags=["발전소 정보"])
def read_plants(db: Session = Depends(get_db)):
    """모든 발전소 정보를 조회"""
    plants = crud.get_all_plants(db)
    return plants


@app.get("/weather/latest/{plant_id}", response_model=schemas.Weather, tags=["기상 정보"])
def read_latest_weather(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 최신 기상 정보 조회"""
    weather = crud.get_latest_weather(db, plant_id=plant_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found for this plant.")
    return weather


@app.get("/generation/latest/{plant_id}", response_model=schemas.Generation, tags=["현재 발전량"])
def read_latest_generation_power(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 최신 발전량 조회"""
    latest_gen = crud.get_latest_generation(db, plant_id=plant_id)
    if not latest_gen:
        raise HTTPException(status_code=404, detail="Generation data not found for this plant.")
    return latest_gen


@app.get("/generation/history/{plant_id}", response_model=List[schemas.Generation], tags=["시간별 발전량"])
def read_generation_history(
    plant_id: int,
    db: Session = Depends(get_db),
    start_time: datetime = Query(datetime.now() - timedelta(hours=24), description="조회 시작 시간"),
    end_time: datetime = Query(datetime.now(), description="조회 종료 시간")
):
    """특정 발전소의 시간별 발전량 이력 조회"""
    history = crud.get_generation_history(db, plant_id, start_time, end_time)
    if not history:
        raise HTTPException(status_code=404, detail="Generation history not found for this period.")
    return history


@app.get("/forecast/{plant_id}", response_model=List[schemas.Forecast], tags=["예측 발전량"])
def read_forecast_power(
    plant_id: int,
    db: Session = Depends(get_db),
    start_time: datetime = Query(datetime.now(), description="예측 시작 시간"),
    end_time: datetime = Query(datetime.now() + timedelta(hours=24), description="예측 종료 시간")
):
    """특정 발전소의 시간별 예측 발전량 조회"""
    forecasts = crud.get_forecasts(db, plant_id, start_time, end_time)
    if not forecasts:
        raise HTTPException(status_code=404, detail="Forecast data not found for this period.")
    return forecasts


@app.get("/daily-forecast/{plant_id}", response_model=List[schemas.DailyForecast], tags=["일별 예측"])
def read_daily_forecast_power(
    plant_id: int,
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    model_version: Optional[str] = Query(None)
):
    """특정 발전소의 일별 예측 발전량 조회"""
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1)).date()
    if end_date is None:
        end_date = (datetime.now() + timedelta(days=7)).date()

    daily_forecasts = crud.get_daily_forecasts(db, plant_id, start_date, end_date, model_version)

    if not daily_forecasts:
        raise HTTPException(status_code=404, detail="Daily forecast data not found for this period.")
    return daily_forecasts


# ===============================================
# 1️⃣ 기상청 기반 실시간 날씨 엔드포인트
# ===============================================
@app.get("/weather/live/{plant_id}", tags=["기상청 날씨"])
def get_live_weather(plant_id: int, db: Session = Depends(get_db)):

    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    # 기상청 날씨 정보 가져오기
    weather = get_kma_weather(lat, lon)

    return {
        "plant_id": plant_id,
        "location": {"lat": lat, "lon": lon},
        "weather": weather
    }


# ===============================================
# 2️⃣ 일사량(GHI) 엔드포인트 (KIER API + fallback)
# ===============================================
@app.get("/solar/irradiance/{plant_id}", tags=["일사량(GHI)"])
def get_kier_solar(plant_id: int, db: Session = Depends(get_db)):

    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    # 기상청 데이터 가져오기 (fallback 계산에 필요)
    weather = get_kma_weather(lat, lon)

    solar = get_solar_irradiance(lat, lon, {
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "cloud": weather["cloud"]
    })

    return {
        "plant_id": plant_id,
        "location": {"lat": lat, "lon": lon},
        "solar": solar
    }
