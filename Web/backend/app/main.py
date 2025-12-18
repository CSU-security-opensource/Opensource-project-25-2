from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional
import logging
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .sevices.prediction import predict_72h_power
from .scheduler.jobs import realtime_job, forecast_3day_job, reset_daily_realtime_job


# Custom modules
from . import schemas, crud
from .models import Base, Plant, Forecast, DailyForecast, RealtimeGeneration
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
# CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # 허용할 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, OPTIONS 등 모두 허용
    allow_headers=["*"],       # 모든 헤더 허용
)
scheduler = BackgroundScheduler(timezone="Asia/Seoul")

# ============================================================
# API 엔드포인트
# ============================================================
@app.on_event("startup")
def startup():
    # 1. 스케줄러 등록 (기존 로직 유지)
    scheduler.add_job(realtime_job, "cron", minute=0)  # 매시 정각
    scheduler.add_job(forecast_3day_job, "cron", hour=0, minute=5) # 매일 00:05
    scheduler.add_job(reset_daily_realtime_job, "cron", hour=0, minute=1) # 매일 00:01

    scheduler.start()
    logger.info("🚀 Scheduler Started")

    # ==========================================================
    # [추가] 서버 시작 시 테스트를 위해 즉시 1회 실행!
    # ==========================================================
    logger.info("⚡ Executing jobs immediately for testing...")
    
    # 여기서 바로 함수를 호출해서 DB에 들어가는지 확인합니다.
    # (스케줄러와 별개로 메인 스레드에서 한 번 실행됨)
    try:
        realtime_job()       # 실시간 발전량 저장 테스트
        forecast_3day_job() # 필요하면 3일치 예보도 주석 해제해서 테스트
    except Exception as e:
        logger.error(f"❌ Initial execution failed: {e}")

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
@app.get("/prediction/realtime/{plant_id}", tags=["예측"])
def get_realtime_prediction_today(
    plant_id: int,
    db: Session = Depends(get_db)
):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    rows = db.query(RealtimeGeneration).filter(
        RealtimeGeneration.plant_id == plant_id,
        RealtimeGeneration.timestamp >= today_start,
        RealtimeGeneration.timestamp < today_end
    ).order_by(RealtimeGeneration.timestamp.asc()).all()

    return {
        "plant_id": plant_id,
        "date": today_start.date(),
        "count": len(rows),
        "data": rows
    }


@app.get("/prediction/hourly/today/{plant_id}", tags=["예측"])
def get_today_hourly_forecast(
    plant_id: int,
    db: Session = Depends(get_db)
):
    """오늘 하루(00:00 ~ 23:00)의 시간별 예측 데이터 조회"""
    # 오늘 00:00 시작
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 내일 00:00 전까지 (오늘 23:59까지 포함)
    today_end = today_start + timedelta(days=1)

    rows = db.query(Forecast).filter(
        Forecast.plant_id == plant_id,
        Forecast.forecast_time >= today_start,
        Forecast.forecast_time < today_end,
        Forecast.model_version == "nhits-v1"
    ).order_by(Forecast.forecast_time.asc()).all()

    return {
        "plant_id": plant_id,
        "count": len(rows),
        "data": rows
    }

@app.get("/prediction/daily/3days/{plant_id}", tags=["예측"])
def get_3day_daily_forecast(
    plant_id: int,
    db: Session = Depends(get_db)
):
    today = date.today()
    end = today + timedelta(days=30)

    rows = db.query(DailyForecast).filter(
        DailyForecast.plant_id == plant_id,
        DailyForecast.forecast_date >= today,
        DailyForecast.forecast_date < end,
        DailyForecast.model_version == "nhits-v1"
    ).order_by(DailyForecast.forecast_date.asc()).all()

    return {
        "plant_id": plant_id,
        "from": today,
        "to": end,
        "count": len(rows),
        "data": rows
    }


# ============================================================
# 앱 시작 이벤트
# ============================================================