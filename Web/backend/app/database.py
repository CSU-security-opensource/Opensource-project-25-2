from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine 생성
engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600
)

# Session Local 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델의 기반 클래스
Base = declarative_base()

# Dependency Injection을 위한 DB 세션 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()