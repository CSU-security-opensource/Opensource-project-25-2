# app/services/prediction.py
from neuralforecast import NeuralForecast
import pandas as pd
import pickle, json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta, date

MODELS_DIR = Path("../../Model/Models")

# 서버 시작 시 1회 로드
nf = NeuralForecast.load(path=str(MODELS_DIR))

with open(MODELS_DIR / "best_model_info.json") as f:
    best_info = json.load(f)

FEATURES = best_info["features"]   # ['insolation','temp','cloud','humidity']


def predict_72h_power(
    weather_forecast: List[Dict], 
    solar_forecast: List[Dict],   
    current_weather: Dict = None, 
):
    # ==========================================
    # 1️⃣ [미래 방] 3일치 미래 날씨 데이터 준비
    # ==========================================
    future_rows = []
    for w, s in zip(weather_forecast, solar_forecast):
        future_rows.append({
            "unique_id": "plant_1",
            "ds": w["datetime"],        
            "insolation": s["irradiance"],
            "temp": w["temperature"],
            "cloud": w["cloud_cover"],
            "humidity": w["humidity"],
            "y": 0.0 # 형식 맞추기용 (실제로는 무시됨)
        })
    futr_exog_df = pd.DataFrame(future_rows)

    # ==========================================
    # 2️⃣ [현재 방] 예측 시작 기준점 (Anchor)
    # ==========================================
    start_time = weather_forecast[0]["datetime"]
    anchor_time = start_time - timedelta(hours=1)

    input_rows = [{
        "unique_id": "plant_1",
        "ds": anchor_time,
        "y": 0.0,  
        "insolation": 0.0, 
        "temp": 0.0,      
        "cloud": 0.0,
        "humidity": 0.0,
    }]
    input_df = pd.DataFrame(input_rows)

    # ==========================================
    # 3️⃣ 모델 예측 실행 (시점 밀림 방지 로직)
    # ==========================================
    forecast_df = None
    
    # [시도 1] 최신 버전 표준 방식 (futr_exog_df)
    try:
        forecast_df = nf.predict(df=input_df, futr_exog_df=futr_exog_df)
    except TypeError:
        pass # 실패하면 다음 방법 시도

    # [시도 2] 구버전 방식 (future_df)
    # 일부 구버전에서는 futr_exog_df 대신 future_df라는 이름을 썼습니다.
    if forecast_df is None:
        try:
            forecast_df = nf.predict(df=input_df, future_df=futr_exog_df)
        except TypeError:
            pass

    # [시도 3] 최후의 수단 (날씨 정보 없이 예측)
    # 라이브러리가 너무 구버전이라 미래 변수를 못 받는 경우입니다.
    # 날씨 반영은 안 되지만, 최소한 "오늘 날짜"로 예측값은 나옵니다.
    if forecast_df is None:
        print("⚠️ [Warning] 미래 날씨 데이터를 적용할 수 없는 라이브러리 버전입니다. 패턴 예측만 수행합니다.")
        try:
            forecast_df = nf.predict(df=input_df)
        except Exception as e:
            print(f"❌ Prediction Failed: {e}")
            return []

    # ==========================================
    # 4️⃣ 결과 정리
    # ==========================================
    results = []
    
    # 예측값 컬럼 찾기
    target_col = [c for c in forecast_df.columns if "NHITS" in c]
    target_col = target_col[0] if target_col else "NHITS"

    for _, row in forecast_df.iterrows():
        # anchor_time(기준점) 이후의 데이터만 가져옴 -> 즉, 오늘 00시부터 3일간
        if row["ds"] > anchor_time:
            val = float(row[target_col])
            results.append({
                "datetime": row["ds"],
                "predicted_power": max(0.0, val) 
            })

    return results