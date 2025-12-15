# ============================================================
# weather_service.py - 기상청 API 서비스 (최종 안정화 버전)
# ============================================================
import requests
import os
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from urllib.parse import quote
from zoneinfo import ZoneInfo

load_dotenv()
KMA_API_KEY = os.getenv("KMA_API_KEY")
logger = logging.getLogger(__name__)

# 공통 헤더 (타임아웃/지연 발생률 줄이는 데 매우 효과적)
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SolarDashboard/2.0)"
}


# ============================================================
# 위경도 → 기상청 격자 변환
# ============================================================
def convert_to_grid(lat: float, lon: float):
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136

    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn_val = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn_val)

    sf = (math.tan(math.pi * 0.25 + slat1 * 0.5)**sn * math.cos(slat1)) / sn
    ro = re * sf / (math.tan(math.pi * 0.25 + olat * 0.5)**sn)

    ra = re * sf / (math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)**sn)
    theta = lon * DEGRAD - olon

    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi

    theta *= sn
    x = math.floor(ra * math.sin(theta) + XO + 0.5)
    y = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    return int(x), int(y)


# ============================================================
# 초단기예보 base_time
# ============================================================
def get_ultra_short_forecast_base_time():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    if now.minute < 45:
        base_dt = now.replace(minute=30) - timedelta(hours=1)
    else:
        base_dt = now.replace(minute=30)
    return base_dt.strftime("%Y%m%d"), base_dt.strftime("%H%M")


# ============================================================
# 초단기예보 (fallback)
# ============================================================
def get_ultra_short_forecast(lat: float, lon: float, retry_count=2):
    nx, ny = convert_to_grid(lat, lon)
    base_date, base_time = get_ultra_short_forecast_base_time()

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    params = {
        "serviceKey": quote(KMA_API_KEY, safe=""),
        "numOfRows": 100,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    last_error = None

    for attempt in range(retry_count + 1):
        try:
            timeout_value = 15 + (attempt * 5)
            response = requests.get(
                url, params=params, headers=COMMON_HEADERS, timeout=timeout_value
            )
            data = response.json()

            if data["response"]["header"]["resultCode"] != "00":
                last_error = data["response"]["header"]["resultMsg"]
                continue

            items = data["response"]["body"]["items"]["item"]

            # fcstTime 가장 최신값만 사용
            ts_map = {}
            for item in items:
                fcst_time = item["fcstTime"]
                if fcst_time not in ts_map:
                    ts_map[fcst_time] = {}
                ts_map[fcst_time][item["category"]] = item["fcstValue"]

            # 최신 fcstTime
            latest_time = sorted(ts_map.keys())[-1]
            info = ts_map[latest_time]

            def safe_float(v):
                try:
                    return float(v)
                except:
                    return None

            return {
                "type": "ultra_short_forecast",
                "base_date": base_date,
                "base_time": base_time,
                "forecast_time": latest_time,
                "temperature": safe_float(info.get("T1H")),
                "humidity": safe_float(info.get("REH")),
                "wind_speed": safe_float(info.get("WSD")),
                "wind_direction": safe_float(info.get("VEC")),
                "precipitation_type": int(info.get("PTY", 0)),
                "rainfall_1h": safe_float(info.get("RN1")),
                "sky_code": int(info.get("SKY", 0)),
                "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
                "data_source": "ultra_short_forecast"
            }

        except Exception as e:
            last_error = e
            continue

    return {
        "error": True,
        "message": f"ultra_short_forecast failed: {last_error}"
    }


# ============================================================
# 초단기실황 (main)
# ============================================================
def get_current_weather(lat: float, lon: float):
    if not KMA_API_KEY:
        return {"error": True, "message": "KMA_API_KEY missing"}

    nx, ny = convert_to_grid(lat, lon)
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # 초단기실황 base_time (10분 전 rule)
    if now.minute < 10:
        base_dt = now.replace(minute=0) - timedelta(hours=1)
    else:
        base_dt = now.replace(minute=0)

    base_date = base_dt.strftime("%Y%m%d")
    base_time = base_dt.strftime("%H%M")

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "serviceKey": quote(KMA_API_KEY, safe=""),
        "numOfRows": 100,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    try:
        response = requests.get(url, params=params, headers=COMMON_HEADERS, timeout=8)
        data = response.json()

        if data["response"]["header"]["resultCode"] != "00":
            return get_ultra_short_forecast(lat, lon)

        items = data["response"]["body"]["items"]["item"]

        result = {
            "type": "current_weather",
            "timestamp": now.isoformat(),
            "base_date": base_date,
            "base_time": base_time,
            "location": {"lat": lat, "lon": lon, "nx": nx, "ny": ny},
            "data_source": "ultra_short_observation"
        }

        def safe_float(v):
            try:
                return float(v)
            except:
                return None

        pty_map = {0: "none", 1: "rain", 2: "rain/snow", 3: "snow", 5: "drizzle", 6: "rain/snow", 7: "snow shower"}

        for item in items:
            cat, v = item["category"], item["obsrValue"]

            match cat:
                case "T1H": result["temperature"] = safe_float(v)
                case "REH": result["humidity"] = safe_float(v)
                case "WSD": result["wind_speed"] = safe_float(v)
                case "VEC": result["wind_direction"] = safe_float(v)
                case "RN1": result["rainfall_1h"] = 0.0 if v == "강수없음" else safe_float(v)
                case "PTY":
                    pt = int(v) if v.isdigit() else 0
                    result["precipitation_type"] = pt
                    result["precipitation_label"] = pty_map.get(pt, "unknown")

        return result

    except Exception:
        return get_ultra_short_forecast(lat, lon)


# ============================================================
# 3일 예보 (모델 학습용)
# ============================================================

def get_short_forecast_base_time():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    hour = now.hour

    # 단기예보는 3시간 간격 base_time 사용
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    valid_hours = [h for h in base_hours if h <= hour]
    
    if valid_hours:
        # 현재 시간 이하의 가장 최근 base_time
        base_hour = max(valid_hours)
        base_dt = now.replace(hour=base_hour, minute=0, second=0, microsecond=0)
    else:
        # 새벽 0~1시: 전날 23시 사용
        base_dt = (now - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
    
    return base_dt.strftime("%Y%m%d"), base_dt.strftime("%H%M")




def get_weather_forecast_3days(lat: float, lon: float):
    nx, ny = convert_to_grid(lat, lon)

    # ★ 단기예보 전용 base_time 사용
    base_date, base_time = get_short_forecast_base_time()

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": quote(KMA_API_KEY, safe=""),
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    try:
        res = requests.get(url, params=params, headers=COMMON_HEADERS, timeout=15)
        data = res.json()

        if data["response"]["header"]["resultCode"] != "00":
            return {"error": True, "message": data["response"]["header"]["resultMsg"]}

        items = data["response"]["body"]["items"]["item"]

        rows = {}
        for item in items:
            key = f"{item['fcstDate']}{item['fcstTime']}"
            if key not in rows:
                rows[key] = {}
            rows[key][item["category"]] = item["fcstValue"]

        now = datetime.now(ZoneInfo("Asia/Seoul"))
        end = now + timedelta(days=3)

        result_rows = []
        for key, v in rows.items():
            ts = datetime.strptime(key, "%Y%m%d%H%M").replace(tzinfo=ZoneInfo("Asia/Seoul"))
            if now <= ts <= end:
                result_rows.append({
                    "timestamp": ts.isoformat(),
                    "temperature": float(v["TMP"]) if "TMP" in v else None,
                    "humidity": float(v["REH"]) if "REH" in v else None,
                    "wind_speed": float(v["WSD"]) if "WSD" in v else None,
                    "precipitation_probability": int(v["POP"]) if "POP" in v else None,
                    "sky_condition_code": int(v["SKY"]) if "SKY" in v else None,
                    "precipitation_type_code": int(v["PTY"]) if "PTY" in v else None,
                })

        return {
            "type": "3day_forecast",
            "count": len(result_rows),
            "forecast": result_rows,
            "location": {"lat": lat, "lon": lon, "nx": nx, "ny": ny},
            "data_source": "short_term_forecast"
        }
        


    except Exception as e:
        return {"error": True, "message": str(e)}
    
