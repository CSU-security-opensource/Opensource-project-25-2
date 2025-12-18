import requests
from datetime import datetime, timedelta


def fetch_open_meteo(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "shortwave_radiation",       # GHI
            "direct_radiation",          # DNI
            "diffuse_radiation",         # DHI
            "sunshine_duration"          # 일조시간 태양이 실제로 비친 시간 
        ]),
        "timezone": "Asia/Seoul"
    }

    res = requests.get(url, params=params)
    data = res.json()

    return data["hourly"]


def get_current_irradiance(lat: float, lon: float):
    hourly = fetch_open_meteo(lat, lon)

    times = hourly["time"]
    ghi = hourly["shortwave_radiation"]

    # 현재 시간과 가장 가까운 값 찾기
    now = datetime.now()
    min_diff = None
    current_value = None

    for i, t in enumerate(times):
        t_dt = datetime.fromisoformat(t)
        diff = abs((now - t_dt).total_seconds())

        if (min_diff is None) or (diff < min_diff):
            min_diff = diff
            current_value = ghi[i]

    return {
        "timestamp": now.isoformat(),
        "ghi": current_value,
        "unit": "W/m²",
        "source": "Open-Meteo"
    }
    
def get_3day_irradiance_forecast(lat: float, lon: float):
    hourly = fetch_open_meteo(lat, lon)

    times = hourly["time"][:72]  # 72시간
    ghi = hourly["shortwave_radiation"][:72]
    dni = hourly["direct_radiation"][:72]
    dhi = hourly["diffuse_radiation"][:72]
    sunshine = hourly["sunshine_duration"][:72]

    forecast = []
    for i in range(72):
        forecast.append({
            "time": times[i],
            "ghi": ghi[i],
            "dni": dni[i],
            "dhi": dhi[i],
            "sunshine": sunshine[i]
        })

    return {
        "count": 72,
        "forecast": forecast,
        "source": "Open-Meteo"
    }
