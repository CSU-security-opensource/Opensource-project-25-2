from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional
import logging

# Custom modules
from . import schemas, crud
from .models import Base, Plant
from .weather_service import get_current_weather, get_weather_forecast_3days
from .solar_service import get_current_irradiance, get_3day_irradiance_forecast

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB 설정
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되어 있지 않습니다.")

engine = create_engine(DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """요청마다 DB 세션 생성 및 종료"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI 앱
app = FastAPI(
    title="신재생 에너지 발전량 예측 플랫폼 API",
    description="태양광 발전소의 실시간 데이터 및 예측을 제공합니다.",
    version="2.0.0"
)


# ============================================================
# API 엔드포인트
# ============================================================

@app.get("/", tags=["Health"])
def health_check():
    """API 상태 확인"""
    return {
        "status": "healthy",
        "service": "Solar Power Prediction API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ---------------- 발전소 정보 ----------------
@app.get("/plants", response_model=List[schemas.Plant], tags=["발전소"])
def read_plants(db: Session = Depends(get_db)):
    """모든 발전소 정보 조회"""
    return crud.get_all_plants(db)


@app.get("/plants/{plant_id}", response_model=schemas.Plant, tags=["발전소"])
def read_plant(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소 정보 조회"""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


# ---------------- 실시간 날씨 ----------------
@app.get("/weather/current/{plant_id}", tags=["날씨"])
def get_plant_current_weather(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 실시간 날씨 조회"""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    lat = float(plant.latitude)
    lon = float(plant.longitude)
    
    weather = get_current_weather(lat, lon)
    if weather.get("error"):
        raise HTTPException(status_code=503, detail=weather.get("message"))
    
    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "weather": weather
    }


# ---------------- 3일 예보 (DB 저장 없이 바로 반환) ----------------
@app.get("/weather/forecast/{plant_id}", tags=["날씨"])
def get_plant_forecast(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 3일 예보 조회: 외부 API에서 직접 가져와 반환합니다."""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    forecast_resp = get_weather_forecast_3days(lat, lon)
    if forecast_resp.get("error"):
        raise HTTPException(status_code=503, detail=forecast_resp.get("message"))

    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "forecast_count": len(forecast_resp.get("forecast", [])),
        "forecast": forecast_resp
    }
#---------------- 일사량 조회 ------------------
@app.get("/solar/realtime/{plant_id}", tags=["일사량"])
def api_get_realtime_solar(plant_id: int, db: Session = Depends(get_db)):
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    return get_current_irradiance(lat, lon)

@app.get("/solar/forecast/{plant_id}", tags=["일사량"])
def api_get_solar_forecast(plant_id: int, db: Session = Depends(get_db)):
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    return get_3day_irradiance_forecast(lat, lon)


# ---------------- 모델 입력 데이터 (72시간 예보) ----------------
@app.get("/model-input/{plant_id}", tags=["모델 입력"])
def get_model_input(plant_id: int, db: Session = Depends(get_db)):
    """모델에 넣을 72시간 단기예보 INPUT 데이터 반환"""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    # 3일치 forecast 가져오기
    forecast_resp = get_weather_forecast_3days(lat, lon)
    if forecast_resp.get("error"):
        raise HTTPException(status_code=503, detail=forecast_resp.get("message"))

    forecasts = forecast_resp.get("forecast", [])

    # LSTM 입력 포맷으로 변환
    input_vector = []
    for f in forecasts:
        vector = [
            f.get("temperature"),
            f.get("humidity"),
            f.get("wind_speed"),
            f.get("sky_condition_code"),
            f.get("precipitation_type_code"),
            f.get("precipitation_probability"),
        ]
        input_vector.append(vector)

    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "input_length": len(input_vector),
        "input_vector": input_vector
    }


# ---------------- 발전량(실제) 조회 ----------------
@app.get("/generation/latest/{plant_id}", response_model=schemas.Generation, tags=["발전량"])
def api_get_latest_generation(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 가장 최근 실제 발전량 조회"""
    gen = crud.get_latest_generation(db, plant_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return gen


@app.get("/generation/history/{plant_id}", response_model=List[schemas.Generation], tags=["발전량"])
def api_get_generation_history(
    plant_id: int,
    start: datetime = Query(..., description="시작 시각 (ISO format)"),
    end: datetime = Query(..., description="종료 시각 (ISO format)"),
    db: Session = Depends(get_db),
):
    """특정 발전소의 기간별 실제 발전량 기록 조회"""
    if start > end:
        raise HTTPException(status_code=400, detail="start must be before end")
    return crud.get_generation_history(db, plant_id, start, end)


# ---------------- 시간별 예측 조회 ----------------
@app.get("/forecast/hourly/{plant_id}", response_model=List[schemas.Forecast], tags=["예측"])
def api_get_hourly_forecast(
    plant_id: int,
    start: datetime = Query(..., description="시작 시각 (ISO format)"),
    end: datetime = Query(..., description="종료 시각 (ISO format)"),
    db: Session = Depends(get_db),
):
    """특정 발전소의 시간별 발전 예측 조회"""
    if start > end:
        raise HTTPException(status_code=400, detail="start must be before end")
    return crud.get_forecasts(db, plant_id, start, end)


# ---------------- 일별 예측 합산 조회 ----------------
@app.get("/forecast/daily/{plant_id}", response_model=List[schemas.DailyForecast], tags=["예측"])
def api_get_daily_forecast(
    plant_id: int,
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    model_version: Optional[str] = Query(None, description="모델 버전 필터 (옵션)"),
    db: Session = Depends(get_db),
):
    """특정 발전소의 일별 예측 합산 데이터를 조회"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    return crud.get_daily_forecasts(db, plant_id, start_date, end_date, model_version)


# ============================================================
# 앱 시작 이벤트
# ============================================================
@app.on_event("startup")
def startup_event():
    """앱 시작"""
    logger.info("🚀 Solar Power Prediction API started")


@app.on_event("shutdown")
def shutdown_event():
    """앱 종료"""
    logger.info("🛑 Solar Power Prediction API stopped")