# create_tables.py
from app.database import engine
from app.models import Base

def create_db_tables():
    print("MySQL 테이블 생성을 시작합니다...")
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성이 완료되었습니다.")

if __name__ == "__main__":
    create_db_tables()
