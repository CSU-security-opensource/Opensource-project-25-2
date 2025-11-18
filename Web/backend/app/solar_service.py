# backend/app/solar_service.py

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# .env 파일에 'KIER_API_KEY'와 'KIER_API_URL'을 꼭 넣어주세요!
# 공공데이터포털 예시 URL (실제 사용하시는 API URL로 변경 필요)
KIER_API_KEY = os.getenv("KIER_API_KEY")
KIER_API_URL = os.getenv("KIER_API_URL", "http://apis.data.go.kr/B551172/getSolarEnergyInfo/getSolarIrradiance")

def get_kier_solar(lat: float, lon: float):
    """
    한국에너지기술연구원 API를 통해 실시간 일사량(solar) 및 일조시간(sunshine) 조회
    입력: 위도(lat), 경도(lon) -> main.py에서 DB 조회 후 넘겨줌
    """
    
    # API 요청 파라미터 (이미지의 포맷과 일반적인 공공데이터 규격 반영)
    params = {
        "serviceKey": KIER_API_KEY,
        "lat": lat,
        "lng": lon,  # API에 따라 'lon' 또는 'lng' 확인 필요
        "date": datetime.now().strftime("%Y%m%d"), # 오늘 날짜
        "type": "json" # JSON 응답 요청
    }

    try:
        # 1. API 호출
        response = requests.get(KIER_API_URL, params=params, timeout=10)
        
        # 응답 확인
        if response.status_code != 200:
            return {"error": True, "message": f"API Call Error: {response.status_code}"}
            
        data = response.json()

        # 2. 응답 데이터 파싱 (제공해주신 이미지 구조 기반)
        # 보통 리스트 형태로 오므로, 현재 시간(Hour)과 일치하는 데이터를 찾습니다.
        current_hour = datetime.now().strftime("%H") # 예: "14"
        
        target_item = None
        
        # 데이터 구조가 { "response": { "body": { "items": [...] } } } 형태라고 가정
        # 만약 이미지가 보여준 그대로 바로 리스트가 온다면 items = data 라고 수정하면 됨
        items = data.get("items", []) # 혹은 data.get("response", {}).get("body", {}).get("items", [])
        
        for item in items:
            # 이미지의 "time" 필드가 "12", "13" 형식이라고 가정
            if str(item.get("time")).zfill(2) == current_hour:
                target_item = item
                break
        
        # 만약 현재 시간 데이터가 없으면 가장 마지막 데이터를 쓰거나 0 처리
        if not target_item and items:
            target_item = items[-1]

        if target_item:
            return {
                "solar_radiation": float(target_item.get("solar", 0.0)),    # 일사량
                "sunshine_duration": float(target_item.get("sunshine", 0.0)), # 일조시간
                "check_time": f"{target_item.get('date')} {target_item.get('time')}:00"
            }
        else:
            return {"solar_radiation": 0.0, "sunshine_duration": 0.0, "message": "No data found"}

    except Exception as e:
        return {"error": True, "message": f"Solar API Error: {str(e)}"}