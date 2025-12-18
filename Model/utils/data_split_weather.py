import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("📊 여러 연도 데이터(전력 + 날씨) 통합 및 분할 - 최종 수정")
print("="*70)

# ========================================
# 1. 데이터 로드 및 전처리 (날씨 컬럼 추가)
# ========================================
print("\n📂 연도별 CSV 파일 로딩 중...")

# 경로 확인
data_folder = "/home/kwy00/nakyung/Opensource-project-25-2/Data/연도별_데이터"
file_pattern = "제주_기상_태양광_데이터_{year}.csv"
years = range(2018, 2025)

dfs = []

# 컬럼 매핑 정의 (데이터에 있는 가능한 이름들)
required_columns = {
    'timestamp': ['일시', '일시.1', '일시.2'], 
    'y': ['태양광 발전량(MWh)', '전력수요량'],   
    'temp': ['기온(°C)', '기온'],
    'rain': ['강수량(mm)', '강수량'],
    'humidity': ['습도(%)', '습도'],
    'insolation': ['일사(MJ/m2)', '일사량', '일사'],
    'cloud': ['전운량(10분위)', '전운량']
}

print(f"\n연도별 파일 로딩 및 컬럼 매핑:")
for year in years:
    filename = file_pattern.format(year=year)
    filepath = os.path.join(data_folder, filename)
    
    try:
        # 인코딩 자동 감지
        try:
            df_year = pd.read_csv(filepath, encoding='utf-8')
            encoding_used = 'utf-8'
        except UnicodeDecodeError:
            df_year = pd.read_csv(filepath, encoding='cp949')
            encoding_used = 'cp949'
            
        print(f"  📄 {year}년 로드 성공 ({encoding_used}): {len(df_year):,}개")
        
        # 1) timestamp 컬럼 찾기 및 이름 변경 ({'기존이름': 'timestamp'})
        ts_col = next((c for c in required_columns['timestamp'] if c in df_year.columns), None)
        if ts_col:
            df_year.rename(columns={ts_col: 'timestamp'}, inplace=True)
        else:
            df_year.rename(columns={df_year.columns[0]: 'timestamp'}, inplace=True)

        # 2) 전력량(y) 컬럼 찾기 및 이름 변경
        y_col = next((c for c in required_columns['y'] if c in df_year.columns), None)
        if y_col:
            df_year.rename(columns={y_col: '전력수요량'}, inplace=True)
        else:
            numeric_cols = df_year.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df_year.rename(columns={numeric_cols[0]: '전력수요량'}, inplace=True)

        # 3) 날씨 컬럼 매핑 (⭐ 이 부분이 수정되었습니다!)
        rename_map = {} # { '기온': 'temp', ... } 형태로 저장
        found_weather_cols = [] # 실제로 찾은 영문 컬럼명 저장

        for eng_name, kor_candidates in required_columns.items():
            if eng_name in ['timestamp', 'y']: continue
            
            # 데이터에 있는 한글 이름 찾기
            found_col = next((c for c in kor_candidates if c in df_year.columns), None)
            if found_col:
                rename_map[found_col] = eng_name # ⭐ {한글: 영문} 순서로 저장
                found_weather_cols.append(eng_name)
        
        # 컬럼명 변경 적용
        df_year.rename(columns=rename_map, inplace=True)

        # 필요한 컬럼만 선택
        # (이미 이름이 바뀐 'temp', 'rain' 등을 선택합니다)
        final_cols = ['timestamp', '전력수요량'] + found_weather_cols
        df_year = df_year[final_cols].copy()
        
        dfs.append(df_year)
        
    except FileNotFoundError:
        print(f"  ⚠️ {year}년: 파일 없음 (건너뜀)")
    except Exception as e:
        print(f"  ❌ {year}년: 로드 중 오류 - {e}")

if len(dfs) == 0:
    print("\n❌ 오류: 로드된 파일이 없습니다!")
    exit()

# ========================================
# 2. 데이터 통합 및 결측치 처리
# ========================================
print("\n" + "="*70)
print("🔗 데이터 통합 및 결측치 처리...")
print("="*70)

df = pd.concat(dfs, ignore_index=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').drop_duplicates('timestamp').reset_index(drop=True)

# 결측치 처리
if 'rain' in df.columns:
    df['rain'] = df['rain'].fillna(0)
if 'insolation' in df.columns:
    df['insolation'] = df['insolation'].fillna(0)

# 나머지 보간
df = df.interpolate(method='linear').fillna(method='ffill').fillna(method='bfill')

print(f"✅ 통합 완료! 총 {len(df):,}개 데이터")
print(f"   컬럼 목록: {list(df.columns)}")

# ========================================
# 3. 데이터 분할
# ========================================
print("\n" + "="*70)
print("✂️ 데이터 분할 (Train/Val/Test)")
print("="*70)

df['연도'] = df['timestamp'].dt.year

# Train: 2018~2021년
train_df = df[(df['연도'] >= 2018) & (df['연도'] <= 2021)].copy()

# Validation: 2022년
val_df = df[df['연도'] == 2022].copy()

# Test: 2023~2024년
test_df = df[df['연도'] >= 2023].copy()

# 연도 컬럼 제거
for d in [train_df, val_df, test_df, df]:
    d.drop(columns=['연도'], inplace=True)

print(f"분할 완료:")
print(f"  Train: {len(train_df):,}개")
print(f"  Val:   {len(val_df):,}개")
print(f"  Test:  {len(test_df):,}개")

# ========================================
# 4. CSV 저장
# ========================================
print("\n💾 저장 중...")

train_df.to_csv('train_data_fixed.csv', index=False, encoding='utf-8-sig')
val_df.to_csv('validation_data_fixed.csv', index=False, encoding='utf-8-sig')
test_df.to_csv('test_data_fixed_filtered.csv', index=False, encoding='utf-8-sig')
df.to_csv('전체_데이터_통합_날씨포함.csv', index=False, encoding='utf-8-sig')

print("✅ 모든 파일 저장 완료!")