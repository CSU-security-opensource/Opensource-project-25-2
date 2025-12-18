import pandas as pd

# 1. 데이터 불러오기
file_path = "../test_data_fixed.csv"
print(f"📂 파일 로딩 중: {file_path}")
df = pd.read_csv(file_path)

# 2. 날짜 형식으로 변환 (연도 추출을 위해 필수)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 3. 2024년 데이터 제거 (연도가 2024가 아닌 것만 남김)
print(f"전체 데이터 개수: {len(df)}개")
df_filtered = df[df['timestamp'].dt.year != 2024].copy()

# 4. 결과 확인
print(f"2024년 제거 후 개수: {len(df_filtered)}개")
print(f"삭제된 데이터 수: {len(df) - len(df_filtered)}개")
print(f"남은 연도 확인: {df_filtered['timestamp'].dt.year.unique()}")

# 5. 저장하기
save_path = "../test_data_fixed_filtered.csv"  # 덮어쓰려면 "../test_data_fixed.csv"로 수정
df_filtered.to_csv(save_path, index=False)

print(f"✅ 저장 완료! : {save_path}")