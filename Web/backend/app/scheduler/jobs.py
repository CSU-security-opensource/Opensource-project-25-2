from datetime import datetime, timedelta, date
from app.database import SessionLocal
from app import crud
from app.models import RealtimeGeneration

# 서비스 함수 임포트 (경로 확인 필요)
from app.weather_service import get_current_weather, get_weather_forecast_3days
from app.solar_service import get_current_irradiance, get_3day_irradiance_forecast
from app.sevices.prediction import predict_72h_power


# ============================================================
# ⏱ 실시간 예측 Job (매 1시간 마다 실행)
# ============================================================
def realtime_job():
    print(f"🔥 [Realtime Job] Started at {datetime.now()}")
    db = SessionLocal()

    try:
        # 현재 시간 (분, 초 0으로 맞춤)
        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        for plant in crud.get_all_plants(db):
            # 1. 날씨 및 일사량 조회
            try:
                weather = get_current_weather(float(plant.latitude), float(plant.longitude))
                solar = get_current_irradiance(float(plant.latitude), float(plant.longitude))
            except Exception as e:
                print(f"⚠️ API Error for plant {plant.id}: {e}")
                continue

            # 2. 모델 입력 데이터 구성
            weather_fc = [{
                "datetime": now,
                "temperature": weather.get("temperature", 0),
                "cloud_cover": weather.get("cloud", 0),
                "humidity": weather.get("humidity", 0)
            }]
            solar_fc = [{"irradiance": solar.get("ghi", 0)}]

            # 3. 예측 수행
            preds = predict_72h_power(weather_fc, solar_fc)
            if not preds:
                continue

            predicted_power = preds[0]["predicted_power"]

            # 4. 누적 발전량 계산 (핵심 로직)
            last_gen = crud.get_latest_realtime_generation(db, plant.id)
            
            cumulative_power = predicted_power  # 기본값 (오늘 첫 데이터일 경우)

            if last_gen:
                # 마지막 기록이 '오늘' 것인지 확인
                if last_gen.timestamp.date() == now.date():
                    # 같은 날짜면 누적
                    cumulative_power = last_gen.cumulative_power + predicted_power
                else:
                    # 날짜가 바뀌었으면(어제 데이터면) 리셋 후 현재 값만 사용
                    print(f"🔄 Date changed for plant {plant.id}. Resetting cumulative power.")
                    cumulative_power = predicted_power

            # 5. DB 저장 (Upsert)
            crud.insert_realtime_generation(
                db=db,
                plant_id=plant.id,
                timestamp=now,
                predicted_power=predicted_power,
                cumulative_power=cumulative_power,
                model_version="realtime-nhits-v1"
            )

            print(f"✅ Realtime Saved | Plant: {plant.id} | Time: {now.hour}h | Power: {predicted_power:.2f} | Cum: {cumulative_power:.2f}")

        db.commit()

    except Exception as e:
        print(f"❌ Realtime Job Failed: {e}")
        db.rollback()
    finally:
        db.close()


# ============================================================
# 📅 3일 예측 Job (매일 00:00 실행)
# ============================================================
def forecast_3day_job():
    print(f"🔥 [Forecast Job] Started at {datetime.now()}")
    db = SessionLocal()

    try:
        for plant in crud.get_all_plants(db):
            # 1. 3일치 예보 데이터 가져오기
            wf = get_weather_forecast_3days(float(plant.latitude), float(plant.longitude))
            sf = get_3day_irradiance_forecast(float(plant.latitude), float(plant.longitude))

            if "forecast" not in wf or "forecast" not in sf:
                continue

            # 2. 데이터 매핑
            weather_fc, solar_fc = [], []
            for w, s in zip(wf["forecast"], sf["forecast"]):
                dt = datetime.fromisoformat(w["timestamp"]).replace(tzinfo=None)
                weather_fc.append({
                    "datetime": dt,
                    "temperature": w["temperature"],
                    "humidity": w["humidity"],
                    "cloud_cover": w["cloud"],
                })
                solar_fc.append({"irradiance": s["ghi"]})

            if not weather_fc:
                continue

            # 3. 모델 예측
            preds = predict_72h_power(weather_fc, solar_fc)
            if not preds:
                continue

            # 4. 예측 기간 설정 (시작 ~ 끝)
            start_dt = preds[0]["datetime"]
            end_dt = preds[-1]["datetime"] + timedelta(hours=1) # 닫힌 구간 처리를 위해 +1시간

            # 5. 기존 예측 삭제 (중복 방지)
            crud.delete_forecasts_by_date_range(
                db=db,
                plant_id=plant.id,
                start_time=start_dt,
                end_time=end_dt,
                model_version="nhits-v1",
            )

            # 6. 시간별 예측(Forecast) 저장
            for p in preds:
                crud.insert_hourly_forecast(
                    db=db,
                    plant_id=plant.id,
                    forecast_time=p["datetime"],
                    predicted_power=p["predicted_power"],
                    model_version="nhits-v1",
                )
            
            # flush로 ID 생성 등 확정
            db.flush()

            # 7. 일별 트렌드(DailyForecast) 재구축
            crud.rebuild_daily_forecast(
                db=db,
                plant_id=plant.id,
                model_version="nhits-v1",
                start_date=start_dt.date(),
                end_date=(end_dt - timedelta(hours=1)).date(),
            )

            print(f"✅ Forecast Updated | Plant: {plant.id} | Range: {start_dt} ~ {end_dt}")

        db.commit()

    except Exception as e:
        print(f"❌ Forecast Job Failed: {e}")
        db.rollback()
    finally:
        db.close()


# ============================================================
# 🔄 실시간 데이터 초기화 Job (매일 00:00 실행)
# ============================================================
def reset_daily_realtime_job():
    print(f"🔥 [Reset Job] Started at {datetime.now()}")
    db = SessionLocal()
    
    try:
        # 오늘 00:00 이전의 데이터는 모두 삭제 (어제 데이터 삭제)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        deleted_count = db.query(RealtimeGeneration).filter(
            RealtimeGeneration.timestamp < today_start
        ).delete()

        db.commit()
        print(f"🧹 Deleted {deleted_count} old realtime records.")
        
    except Exception as e:
        print(f"❌ Reset Job Failed: {e}")
        db.rollback()
    finally:
        db.close()