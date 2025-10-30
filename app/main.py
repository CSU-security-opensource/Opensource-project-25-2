from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date # date 타입 임포트
from typing import List, Optional 

# ⭐ Import custom modules
from . import schemas
from . import crud 
from .models import Base, Plant, Generation, Forecast, Weather, DailyForecast 

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

# Engine 생성 (MySQL + PyMySQL 드라이버 사용 가정)
engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency Injection: DB 세션을 요청마다 생성하고 종료합니다."""
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
    description="데이터 조회 서비스입니다."
)

# ----------------------------------------------------
# API ENDPOINTS (라우터)
# ----------------------------------------------------

@app.get("/plants", response_model=List[schemas.Plant], tags=["발전소 정보"])
def read_plants(db: Session = Depends(get_db)):
    """모든 발전소 정보를 조회합니다."""
    plants = crud.get_all_plants(db) 
    return plants

@app.get("/weather/latest/{plant_id}", response_model=schemas.Weather, tags=["기상 정보"])
def read_latest_weather(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 가장 최근 기상 관측 정보를 조회합니다."""
    weather = crud.get_latest_weather(db, plant_id=plant_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found for this plant.")
    return weather

@app.get("/generation/latest/{plant_id}", response_model=schemas.Generation, tags=["현재 발전량"])
def read_latest_generation_power(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 가장 최근 실제 발전량 기록을 조회합니다."""
    latest_gen = crud.get_latest_generation(db, plant_id=plant_id)
    if not latest_gen:
        raise HTTPException(status_code=404, detail="Generation data not found for this plant.")
    return latest_gen

@app.get("/generation/history/{plant_id}", response_model=List[schemas.Generation], tags=["시간별 발전량"])
def read_generation_history(
    plant_id: int,
    db: Session = Depends(get_db),
    start_time: datetime = Query(datetime.now() - timedelta(hours=24), description="조회 시작 시간 (YYYY-MM-DDTHH:MM:SS)"),
    end_time: datetime = Query(datetime.now(), description="조회 종료 시간 (YYYY-MM-DDTHH:MM:SS)")
):
    """특정 발전소의 지정된 기간 동안의 시간별 실제 발전량 기록을 조회합니다."""
    history = crud.get_generation_history(db, plant_id, start_time, end_time)
    if not history:
        raise HTTPException(status_code=404, detail="Generation history not found for this period.")
    return history

@app.get("/forecast/{plant_id}", response_model=List[schemas.Forecast], tags=["예측 발전량"])
def read_forecast_power(
    plant_id: int,
    db: Session = Depends(get_db),
    start_time: datetime = Query(datetime.now(), description="예측 조회 시작 시간 (YYYY-MM-DDTHH:MM:SS)"),
    end_time: datetime = Query(datetime.now() + timedelta(hours=24), description="예측 조회 종료 시간 (YYYY-MM-DDTHH:MM:SS)")
):
    """특정 발전소의 지정된 기간 동안의 시간별 예측 발전량을 조회합니다."""
    forecasts = crud.get_forecasts(db, plant_id, start_time, end_time)
    if not forecasts:
        raise HTTPException(status_code=404, detail="Forecast data not found for this period.")
    return forecasts

@app.get("/daily-forecast/{plant_id}", response_model=List[schemas.DailyForecast], tags=["예측 발전량"])
def read_daily_forecast_power(
    plant_id: int,
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    model_version: Optional[str] = Query(None, description="특정 모델 버전 필터링")
):
    """특정 발전소의 지정된 기간 동안의 일별 예측 합산 결과를 조회합니다."""
    
    # 기본값 설정
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1)).date()
    if end_date is None:
        end_date = (datetime.now() + timedelta(days=7)).date()

    daily_forecasts = crud.get_daily_forecasts(db, plant_id, start_date, end_date, model_version)
    
    if not daily_forecasts:
        raise HTTPException(status_code=404, detail="Daily forecast data not found for this period.")
    return daily_forecasts