import pandas as pd

print("="*70)
print("🔧 결측 시간 수정 스크립트")
print("="*70)

# ========================================
# 1. Train 데이터 수정
# ========================================
print("\n📂 Train 데이터 처리 중...")

train_df = pd.read_csv("../Data/train_data.csv")
train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
train_df = train_df.sort_values('timestamp').reset_index(drop=True)

print(f"원본 데이터: {len(train_df)}개")

# 중복 제거
train_df = train_df.drop_duplicates(subset=['timestamp'], keep='first')

# 전체 시간 범위 생성
full_range = pd.date_range(
    start=train_df['timestamp'].min(),
    end=train_df['timestamp'].max(),
    freq='H'
)

# 결측 시간 확인
missing_times = sorted(set(full_range) - set(train_df['timestamp']))
print(f"결측 시간: {len(missing_times)}개")

if len(missing_times) > 0:
    print("\n결측 시간 목록:")
    for t in missing_times:
        print(f"  - {t}")

# 인덱스 설정 후 재샘플링
train_df = train_df.set_index('timestamp')
train_df = train_df.reindex(full_range)

# 결측값 보간 (선형 보간)
print(f"\n보간 전 NaN: {train_df['전력수요량'].isnull().sum()}개")
train_df['전력수요량'] = train_df['전력수요량'].interpolate(method='linear')
train_df['전력수요량'] = train_df['전력수요량'].fillna(0)  # 앞뒤 끝 0으로
print(f"보간 후 NaN: {train_df['전력수요량'].isnull().sum()}개")

train_df = train_df.reset_index()
train_df.columns = ['timestamp', '전력수요량']

print(f"수정 후 데이터: {len(train_df)}개")

# 저장
train_df.to_csv("train_data_fixed.csv", index=False, encoding='utf-8-sig')
print("✅ 'train_data_fixed.csv' 저장 완료!")

# ========================================
# 2. Validation 데이터 수정
# ========================================
print("\n" + "="*70)
print("📂 Validation 데이터 처리 중...")

val_df = pd.read_csv("../Data/validation_data.csv")
val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
val_df = val_df.sort_values('timestamp').reset_index(drop=True)

print(f"원본 데이터: {len(val_df)}개")

val_df = val_df.drop_duplicates(subset=['timestamp'], keep='first')

full_range_val = pd.date_range(
    start=val_df['timestamp'].min(),
    end=val_df['timestamp'].max(),
    freq='H'
)

missing_val = len(full_range_val) - len(val_df)
print(f"결측 시간: {missing_val}개")

val_df = val_df.set_index('timestamp')
val_df = val_df.reindex(full_range_val)
val_df['전력수요량'] = val_df['전력수요량'].interpolate(method='linear')
val_df['전력수요량'] = val_df['전력수요량'].fillna(0)
val_df = val_df.reset_index()
val_df.columns = ['timestamp', '전력수요량']

print(f"수정 후 데이터: {len(val_df)}개")

val_df.to_csv("validation_data_fixed.csv", index=False, encoding='utf-8-sig')
print("✅ 'validation_data_fixed.csv' 저장 완료!")

# ========================================
# 3. Test 데이터 수정
# ========================================
print("\n" + "="*70)
print("📂 Test 데이터 처리 중...")

test_df = pd.read_csv("../Data/test_data.csv")
test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])
test_df = test_df.sort_values('timestamp').reset_index(drop=True)

print(f"원본 데이터: {len(test_df)}개")

test_df = test_df.drop_duplicates(subset=['timestamp'], keep='first')

full_range_test = pd.date_range(
    start=test_df['timestamp'].min(),
    end=test_df['timestamp'].max(),
    freq='H'
)

missing_test = len(full_range_test) - len(test_df)
print(f"결측 시간: {missing_test}개")

test_df = test_df.set_index('timestamp')
test_df = test_df.reindex(full_range_test)
test_df['전력수요량'] = test_df['전력수요량'].interpolate(method='linear')
test_df['전력수요량'] = test_df['전력수요량'].fillna(0)
test_df = test_df.reset_index()
test_df.columns = ['timestamp', '전력수요량']

print(f"수정 후 데이터: {len(test_df)}개")

test_df.to_csv("test_data_fixed.csv", index=False, encoding='utf-8-sig')
print("✅ 'test_data_fixed.csv' 저장 완료!")

# ========================================
# 4. 검증
# ========================================
print("\n" + "="*70)
print("🔍 수정 결과 검증")
print("="*70)

train_fixed = pd.read_csv("train_data_fixed.csv")
train_fixed['timestamp'] = pd.to_datetime(train_fixed['timestamp'])

time_diff = train_fixed['timestamp'].diff()
print(f"\nTrain 시간 간격:")
print(time_diff.value_counts())

expected = int((train_fixed['timestamp'].max() - train_fixed['timestamp'].min()).total_seconds() / 3600) + 1
print(f"\n예상 개수: {expected}")
print(f"실제 개수: {len(train_fixed)}")
print(f"결측: {expected - len(train_fixed)}개")

if expected == len(train_fixed):
    print("\n✅ 완벽! 결측 시간 없음!")
else:
    print(f"\n⚠️ 여전히 {expected - len(train_fixed)}개 결측")

print("\n" + "="*70)
print("✅ 모든 데이터 수정 완료!")
print("="*70)
print("\n생성된 파일:")
print("  📄 train_data_fixed.csv")
print("  📄 validation_data_fixed.csv")
print("  📄 test_data_fixed.csv")
print("\n다음 단계:")
print("  1. train.py에서 파일명 변경:")
print("     train_data.csv → train_data_fixed.csv")
print("  2. python train.py 실행")
print("="*70)