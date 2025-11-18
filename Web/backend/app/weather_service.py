# backend/app/weather_service.py

import requests
import os
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
KMA_API_KEY = os.getenv("KMA_API_KEY")

# --- [좌표 변환 함수] ---
def convert_to_grid(lat: float, lon: float):
    """위경도(Lat, Lon) -> 기상청 격자(NX, NY) 변환"""
    RE = 6371.00877; GRID = 5.0; SLAT1 = 30.0; SLAT2 = 60.0; OLON = 126.0; OLAT = 38.0; XO = 43; YO = 136
    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD; slat2 = SLAT2 * DEGRAD; olon = OLON * DEGRAD; olat = OLAT * DEGRAD
    sn = math.tan(math.pi*0.25 + slat2*0.5) / math.tan(math.pi*0.25 + slat1*0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi*0.25 + slat1*0.5); sf = (sf**sn * math.cos(slat1)) / sn
    ro = math.tan(math.pi*0.25 + olat*0.5); ro = re * sf / (ro**sn)
    ra = math.tan(math.pi*0.25 + lat*DEGRAD*0.5); ra = re * sf / (ra**sn)
    theta = lon*DEGRAD - olon
    if theta > math.pi: theta -= 2.0*math.pi
    if theta < -math.pi: theta += 2.0*math.pi
    theta *= sn
    x = ra * math.sin(theta) + XO; y = ro - ra * math.cos(theta) + YO
    return int(x + 1.5), int(y + 1.5)

def get_base_time_ncst():
    """초단기실황(실시간)용 Base Time 계산 (매시 40분 생성)"""
    now = datetime.now()
    if now.minute < 45:
        now = now - timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H00")

def get_base_time_fcst():
    """초단기예보(구름용)용 Base Time 계산 (매시 45분 생성)"""
    now = datetime.now()
    if now.minute < 45:
        now = now - timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H30")

# --- [핵심 함수: 날씨 + 구름 통합 조회] ---
def get_current_weather(lat: float, lon: float):
    """
    [실시간 날씨 통합 함수]
    1. 초단기실황 API -> 기온, 습도, 강수량, 바람
    2. 초단기예보 API -> 하늘상태(구름)
    """
    nx, ny = convert_to_grid(lat, lon)
    
    # 결과 담을 딕셔너리 초기화
    result = {
        "temperature": None, "humidity": None, "rainfall_1h": 0,
        "wind_speed": None, "sky_condition": None, # 1:맑음, 3:구름많음, 4:흐림
        "base_time": None
    }

    # 1. 초단기 실황 (Real-time) 호출
    base_date, base_time = get_base_time_ncst()
    result["base_time"] = f"{base_date} {base_time}"
    
    url_ncst = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params_ncst = {
        "serviceKey": KMA_API_KEY, "pageNo": 1, "numOfRows": 10, "dataType": "JSON",
        "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny
    }
    
    try:
        res = requests.get(url_ncst, params=params_ncst, timeout=5)
        items = res.json()["response"]["body"]["items"]["item"]
        for item in items:
            cat = item["category"]; val = float(item["obsrValue"])
            if cat == "T1H": result["temperature"] = val
            elif cat == "REH": result["humidity"] = val
            elif cat == "RN1": result["rainfall_1h"] = val
            elif cat == "WSD": result["wind_speed"] = val
    except Exception as e:
        print(f"NCST Error: {e}")

    # 2. 초단기 예보 (Forecast) 호출 -> 오직 구름(SKY) 확인용
    base_date_fc, base_time_fc = get_base_time_fcst()
    url_fcst = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    params_fcst = {
        "serviceKey": KMA_API_KEY, "pageNo": 1, "numOfRows": 60, "dataType": "JSON",
        "base_date": base_date_fc, "base_time": base_time_fc, "nx": nx, "ny": ny
    }

    try:
        res = requests.get(url_fcst, params=params_fcst, timeout=5)
        items = res.json()["response"]["body"]["items"]["item"]
        # 가장 빠른 시간의 SKY 값 찾기
        for item in items:
            if item["category"] == "SKY":
                result["sky_condition"] = int(item["fcstValue"]) # 1, 3, 4
                break
    except Exception as e:
        print(f"FCST Error: {e}")

    return result

# --- [기존 유지: 단기 예보 조회] ---
def get_weather_forecast_short(lat: float, lon: float):
    # (이전에 작성해드린 코드가 있다면 그대로 두시면 됩니다.)
    # 필요하다면 다시 작성해 드립니다.
    pass