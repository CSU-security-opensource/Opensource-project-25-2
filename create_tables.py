# create_tables.py
from app.models import Base
from app.main import engine # main.py에서 정의된 engine을 가져옴

# 테이블 생성 함수
def create_db_tables():
    print("MySQL 테이블 생성을 시작합니다...")
    # Base에 정의된 모든 메타데이터를 사용하여 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성이 완료되었습니다.")

if __name__ == "__main__":
    create_db_tables()