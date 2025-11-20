from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Custom modules
from . import schemas, crud
from .models import Base, Plant, WeatherForecast
from .weather_service import get_current_weather, get_weather_forecast_3days
from .solar_service import get_solar_irradiance, get_kier_solar

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
# 스케줄러 함수들
# ============================================================
def save_weather_forecast(db: Session, plant_id: int, forecast_data: list):
    """일기예보 데이터 DB 저장"""
    saved = 0
    for item in forecast_data:
        forecast = WeatherForecast(
            plant_id=plant_id,
            forecast_datetime=datetime.fromisoformat(item["timestamp"]),
            temperature=item.get("temperature"),
            humidity=item.get("humidity"),
            sky_condition=item.get("sky_condition"),
            precipitation_type=item.get("precipitation_type"),
            precipitation_probability=item.get("precipitation_probability"),
            rainfall=item.get("rainfall"),
            wind_speed=item.get("wind_speed"),
            wind_direction=item.get("wind_direction"),
            created_at=datetime.now()
        )
        db.merge(forecast)
        saved += 1
    db.commit()
    return saved


def cleanup_old_forecasts(db: Session):
    """3일 이전 예보 데이터 삭제"""
    three_days_ago = datetime.now() - timedelta(days=3)
    deleted = db.query(WeatherForecast).filter(
        WeatherForecast.forecast_datetime < three_days_ago
    ).delete()
    db.commit()
    return deleted


def update_weather_forecasts():
    """모든 발전소의 3일 예보 업데이트"""
    db = SessionLocal()
    try:
        plants = crud.get_all_plants(db)
        
        for plant in plants:
            lat = float(plant.latitude)
            lon = float(plant.longitude)
            
            forecast = get_weather_forecast_3days(lat, lon)
            if not forecast.get("error"):
                save_weather_forecast(db, plant.id, forecast["forecast"])
                logger.info(f"✅ Updated forecast for Plant {plant.id}: {plant.name}")
            else:
                logger.error(f"❌ Failed to update forecast for Plant {plant.id}: {forecast.get('message')}")
        
        deleted = cleanup_old_forecasts(db)
        logger.info(f"🗑️ Cleaned up {deleted} old forecast records")
    
    finally:
        db.close()


# 스케줄러 시작
scheduler = BackgroundScheduler()
scheduler.add_job(update_weather_forecasts, 'cron', hour='2,5,8,11,14,17,20,23', minute=10)


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



# ---------------- 3일 예보 ----------------
@app.get("/weather/forecast/{plant_id}", tags=["날씨"])
def get_plant_forecast(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 3일 예보 조회: 외부 API로 가져와 DB에 저장한 뒤 요약을 반환합니다."""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    lat = float(plant.latitude)
    lon = float(plant.longitude)

    forecast_resp = get_weather_forecast_3days(lat, lon)
    if forecast_resp.get("error"):
        raise HTTPException(status_code=503, detail=forecast_resp.get("message"))

    items = forecast_resp.get("forecast", [])
    saved_count = 0
    if items:
        saved_count = save_weather_forecast(db, plant_id, items)

    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "saved_count": saved_count,
        "forecast_count": len(items),
        "forecast": forecast_resp
    }
    


@app.get("/model-input/{plant_id}", tags=["모델 입력"])
def get_model_input(plant_id: int, db: Session = Depends(get_db)):
    """모델에 넣을 72시간 단기예보 INPUT 데이터 반환"""

    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    now = datetime.now()
    end = now + timedelta(days=3)

    # 3일치 forecast 가져오기
    forecasts = crud.get_forecasts_by_date_range(db, plant_id, now, end)

    # LSTM 입력 포맷으로 변환
    input_vector = []
    for f in forecasts:
        vector = [
            f.temperature,
            f.humidity,
            f.wind_speed,
            f.sky_condition,
            f.precipitation_type,
            f.precipitation_probability,
        ]
        input_vector.append(vector)

    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "input_length": len(input_vector),
        "input_vector": input_vector
    }






# ---------------- 일사량 ----------------
@app.get("/solar/current/{plant_id}", tags=["일사량"])
def get_plant_solar(plant_id: int, db: Session = Depends(get_db)):
    """특정 발전소의 일사량 조회 (KIER + 추정)"""
    plant = crud.get_plant_by_id(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    lat = float(plant.latitude)
    lon = float(plant.longitude)
    
    # 현재 날씨 정보 가져오기
    weather = get_current_weather(lat, lon)
    if weather.get("error"):
        weather_data = {"cloud": 3, "humidity": 60}  # 기본값
    else:
        weather_data = {
            "cloud": weather.get("sky_condition", 3),
            "humidity": weather.get("humidity", 60),
            "temperature": weather.get("temperature", 20)
        }
    
    # 일사량 계산
    solar = get_solar_irradiance(lat, lon, weather_data)
    
    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "solar": solar
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
# 앱 시작/종료 이벤트
# ============================================================
@app.on_event("startup")
def startup_event():
    """앱 시작 시 스케줄러 실행"""
    scheduler.start()
    logger.info("📅 Weather forecast scheduler started")
    logger.info("⏰ Scheduled updates: 02:10, 05:10, 08:10, 11:10, 14:10, 17:10, 20:10, 23:10")


@app.on_event("shutdown")
def shutdown_event():
    """앱 종료 시 스케줄러 정리"""
    scheduler.shutdown()
    logger.info