from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from .database import Base  # database.py에서 정의한 Base를 사용한다고 가정

# 1. Plant (발전소 고유 정보)
class Plant(Base):
    __tablename__ = "PLANT"

    # SQLAlchemy에서는 기본 키를 명시해야 합니다. (Django의 id 필드에 해당)
    id = Column(Integer, primary_key=True, index=True) 
    
    name = Column(String(100), index=True)
    place = Column(String(255))
    capacity_mw = Column(Float)
    start_date = Column(Date)
    # DecimalField(max_digits=9, decimal_places=6)는 Numeric(9, 6)으로 변환
    latitude = Column(Numeric(9, 6)) 
    longitude = Column(Numeric(9, 6))

    # Relationship 정의 (외래 키가 Plant를 참조하는 테이블들)
    weathers = relationship("Weather", back_populates="plant")
    generations = relationship("Generation", back_populates="plant")
    forecasts = relationship("Forecast", back_populates="plant")
    daily_forecasts = relationship("DailyForecast", back_populates="plant")


# 2. Weather (시간별 기상 데이터)
class Weather(Base):
    __tablename__ = "WEATHER"

    id = Column(Integer, primary_key=True, index=True)
    
    # plant_id (FK): Plant 모델을 참조
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float)
    insolation = Column(Float)
    
    # 추가된 필드들
    humidity = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    snowfall = Column(Float, nullable=True)
    
    # UniqueConstraint: Django의 unique_together = ('plant', 'timestamp')에 해당
    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', name='_plant_timestamp_uc'),
    )

    # Relationship 정의 (Plant 모델과의 관계)
    plant = relationship("Plant", back_populates="weathers")


# 3. Generation (시간별 실제 발전량)
class Generation(Base):
    __tablename__ = "GENERATION"

    id = Column(Integer, primary_key=True, index=True)
    
    # plant_id (FK)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    actual_power_mwh = Column(Float)

    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', name='_gen_plant_timestamp_uc'),
    )

    plant = relationship("Plant", back_populates="generations")


# 4. Forecast (시간별 예측 결과)
class Forecast(Base):
    __tablename__ = "FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    
    # plant_id (FK)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    timestamp = Column(DateTime, index=True)
    predicted_power_mwh = Column(Float)
    model_version = Column(String(50))

    # UniqueConstraint: ('plant', 'timestamp', 'model_version')에 해당
    __table_args__ = (
        UniqueConstraint('plant_id', 'timestamp', 'model_version', name='_fc_plant_ts_ver_uc'),
    )

    plant = relationship("Plant", back_populates="forecasts")


# 5. DailyForecast (일별 예측 합산 결과)
class DailyForecast(Base):
    __tablename__ = "DAILY_FORECAST"

    id = Column(Integer, primary_key=True, index=True)
    
    # plant_id (FK)
    plant_id = Column(Integer, ForeignKey("PLANT.id"))
    date = Column(Date, index=True)
    total_predicted_power_mwh = Column(Float)
    model_version = Column(String(50))

    # UniqueConstraint: ('plant', 'date', 'model_version')에 해당
    __table_args__ = (
        UniqueConstraint('plant_id', 'date', 'model_version', name='_dfc_plant_date_ver_uc'),
    )

    plant = relationship("Plant", back_populates="daily_forecasts")