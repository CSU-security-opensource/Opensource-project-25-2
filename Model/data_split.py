import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

"""
=============================================================================
여러 연도별 CSV 파일 통합 및 Train/Validation/Test 분할
=============================================================================
입력: 제주_기상_태양광_데이터_2018.csv ~ 2024.csv
출력: train_data.csv, validation_data.csv, test_data.csv
=============================================================================
"""

print("="*70)
print("📊 여러 연도 데이터 통합 및 분할")
print("="*70)
print("\n📂 연도별 CSV 파일 로딩 중...")

data_folder = "/home/kwy00/nakyung/Opensource-project-25-2/Data/연도별_데이터"  # ⭐ 폴더명에 맞게 수정
file_pattern = "제주_기상_태양광_데이터_{year}.csv"
years = range(2018, 2024) 

# 데이터프레임 리스트
dfs = []

print(f"\n연도별 파일 로딩:")
for year in years:
    filename = file_pattern.format(year=year)
    filepath = os.path.join(data_folder, filename)
    
    try:
        df_year = pd.read_csv(filepath)
        
        # 첫 번째 컬럼을 timestamp로 (일시 또는 날짜/시간 컬럼)
        if '일시' in df_year.columns:
            df_year.rename(columns={'일시': 'timestamp'}, inplace=True)
        else:
            # 첫 번째 컬럼을 timestamp로 가정
            df_year.rename(columns={df_year.columns[0]: 'timestamp'}, inplace=True)
        
        # 발전량 컬럼 찾기
        power_cols = [col for col in df_year.columns if '발전량' in col or 'MWh' in col]
        if len(power_cols) > 0:
            df_year.rename(columns={power_cols[0]: '전력수요량'}, inplace=True)
        else:
            # 숫자 데이터가 있는 두 번째 컬럼을 발전량으로 가정
            numeric_cols = df_year.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df_year.rename(columns={numeric_cols[0]: '전력수요량'}, inplace=True)
        
        # 필요한 컬럼만 선택
        df_year = df_year[['timestamp', '전력수요량']].copy()
        
        dfs.append(df_year)
        print(f"  ✅ {year}년: {len(df_year):,}개 시간 로드 완료")
        
    except FileNotFoundError:
        print(f"  ⚠️ {year}년: 파일 없음 (건너뜀)")
    except Exception as e:
        print(f"  ❌ {year}년: 오류 발생 - {e}")

if len(dfs) == 0:
    print("\n❌ 오류: 로드된 파일이 없습니다!")
    print(f"경로 확인: {data_folder}")
    print(f"파일명 패턴: {file_pattern}")
    exit()

# ========================================
# 2. 데이터 통합
# ========================================
print("\n" + "="*70)
print("🔗 데이터 통합 중...")
print("="*70)

df = pd.concat(dfs, ignore_index=True)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)
df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)

print(f"\n✅ 통합 완료!")
print(f"  - 총 데이터: {len(df):,}개 시간")
print(f"  - 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
print(f"  - 기간: {(df['timestamp'].max() - df['timestamp'].min()).days}일")

print(f"\n통합된 데이터 샘플:")
print(df.head(10))
print("\n...")
print(df.tail(10))

# 결측값 확인
missing = df.isnull().sum()
if missing.sum() > 0:
    print(f"\n⚠️ 결측값 발견:")
    print(missing)
    print(f"\n결측값을 선형 보간으로 채웁니다...")
    df['전력수요량'] = df['전력수요량'].interpolate(method='linear')
    print(f"✅ 결측값 처리 완료!")

# ========================================
# 3. 연도별 데이터 분석
# ========================================
print("\n" + "="*70)
print("📅 연도별 데이터 분석")
print("="*70)

df['연도'] = df['timestamp'].dt.year
df['월'] = df['timestamp'].dt.month

yearly_counts = df.groupby('연도').size()
print(f"\n연도별 데이터 개수:")
for year, count in yearly_counts.items():
    print(f"  - {year}년: {count:,}개 시간 ({count/24:.1f}일)")

# 2024년 월별 확인
if 2024 in yearly_counts.index:
    monthly_2024 = df[df['연도'] == 2024].groupby('월').size()
    print(f"\n2024년 월별 데이터:")
    for month, count in monthly_2024.items():
        print(f"  - {month}월: {count:,}개 시간 ({count/24:.1f}일)")

# ========================================
# 4. 데이터 분할
# ========================================
print("\n" + "="*70)
print("✂️ 데이터 분할 전략")
print("="*70)

# Train: 2019~2021년 (2018년은 데이터 적을 수 있어서 제외 가능)
train_df = df[(df['연도'] >= 2019) & (df['연도'] <= 2021)].copy()

# Validation: 2022년
val_df = df[df['연도'] == 2022].copy()

# Test: 2023년 전체 + 2024년 1~5월
test_df = df[((df['연도'] == 2023) | 
              ((df['연도'] == 2024) & (df['월'] <= 5)))].copy()

print(f"\n분할 전략:")
print(f"  📚 Train:      2019~2021년 (3년, Fine-tuning용)")
print(f"  🔍 Validation: 2022년 (과적합 방지)")
print(f"  🧪 Test:       2023년 전체 + 2024년 1~5월 (Zero-shot 비교)")

# ========================================
# 5. 분할 결과 확인
# ========================================
print("\n" + "="*70)
print("📊 분할 결과")
print("="*70)

print(f"\n✅ Train 데이터:")
print(f"  - 개수: {len(train_df):,}개 시간 ({len(train_df)/24:.1f}일)")
print(f"  - 기간: {train_df['timestamp'].min()} ~ {train_df['timestamp'].max()}")
print(f"  - 평균: {train_df['전력수요량'].mean():.2f} MWh")
print(f"  - 비율: {len(train_df)/len(df)*100:.1f}%")

print(f"\n✅ Validation 데이터:")
print(f"  - 개수: {len(val_df):,}개 시간 ({len(val_df)/24:.1f}일)")
print(f"  - 기간: {val_df['timestamp'].min()} ~ {val_df['timestamp'].max()}")
print(f"  - 평균: {val_df['전력수요량'].mean():.2f} MWh")
print(f"  - 비율: {len(val_df)/len(df)*100:.1f}%")

print(f"\n✅ Test 데이터:")
print(f"  - 개수: {len(test_df):,}개 시간 ({len(test_df)/24:.1f}일)")
print(f"  - 기간: {test_df['timestamp'].min()} ~ {test_df['timestamp'].max()}")
print(f"  - 평균: {test_df['전력수요량'].mean():.2f} MWh")
print(f"  - 비율: {len(test_df)/len(df)*100:.1f}%")

# ========================================
# 6. 시각화
# ========================================
print("\n" + "="*70)
print("📊 시각화 생성 중...")
print("="*70)

fig, axes = plt.subplots(3, 1, figsize=(20, 14))

# 1) 전체 시계열
axes[0].plot(train_df['timestamp'], train_df['전력수요량'], 
             label='Train (2019~2021)', color='#2E86AB', alpha=0.6, linewidth=0.8)
axes[0].plot(val_df['timestamp'], val_df['전력수요량'], 
             label='Validation (2022)', color='#F18F01', alpha=0.7, linewidth=1)
axes[0].plot(test_df['timestamp'], test_df['전력수요량'], 
             label='Test (2023~2024.5)', color='#A23B72', alpha=0.7, linewidth=1)

axes[0].axvline(val_df['timestamp'].min(), color='orange', linestyle='--', linewidth=2, alpha=0.7)
axes[0].axvline(test_df['timestamp'].min(), color='red', linestyle='--', linewidth=2, alpha=0.7)

axes[0].set_xlabel('날짜', fontsize=12, fontweight='bold')
axes[0].set_ylabel('전력 수요량 (MWh)', fontsize=12, fontweight='bold')
axes[0].set_title('Train/Validation/Test 데이터 분할 (Zero-shot vs Fine-tuned 비교용)', 
                  fontsize=14, fontweight='bold')
axes[0].legend(fontsize=11, loc='best')
axes[0].grid(True, alpha=0.3)

# 2) 연도별 평균
yearly_avg = df.groupby('연도')['전력수요량'].mean()
colors_list = []
for year in yearly_avg.index:
    if 2019 <= year <= 2021:
        colors_list.append('#2E86AB')
    elif year == 2022:
        colors_list.append('#F18F01')
    else:
        colors_list.append('#A23B72')

axes[1].bar(yearly_avg.index, yearly_avg.values, 
           color=colors_list, alpha=0.7, edgecolor='black')

for year, avg in yearly_avg.items():
    axes[1].text(year, avg + 5, f"{avg:.1f}", 
                ha='center', fontsize=10, fontweight='bold')

axes[1].set_xlabel('연도', fontsize=12, fontweight='bold')
axes[1].set_ylabel('평균 전력 수요 (MWh)', fontsize=12, fontweight='bold')
axes[1].set_title('연도별 평균 전력 수요', fontsize=14, fontweight='bold')
axes[1].set_xticks(yearly_avg.index)
axes[1].grid(True, alpha=0.3, axis='y')

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2E86AB', alpha=0.7, label='Train (2019~2021)'),
    Patch(facecolor='#F18F01', alpha=0.7, label='Validation (2022)'),
    Patch(facecolor='#A23B72', alpha=0.7, label='Test (2023~2024)')
]
axes[1].legend(handles=legend_elements, fontsize=11)

# 3) 데이터 개수 비교
split_counts = pd.Series({
    'Train\n(2019~2021)': len(train_df),
    'Validation\n(2022)': len(val_df),
    'Test\n(2023~2024.5)': len(test_df)
})

axes[2].bar(range(len(split_counts)), split_counts.values, 
           color=['#2E86AB', '#F18F01', '#A23B72'], alpha=0.7, edgecolor='black')

for i, (label, count) in enumerate(split_counts.items()):
    axes[2].text(i, count + 500, f"{count:,}개\n({count/24:.0f}일)", 
                ha='center', fontsize=10, fontweight='bold')

axes[2].set_xticks(range(len(split_counts)))
axes[2].set_xticklabels(split_counts.index, fontsize=11)
axes[2].set_ylabel('데이터 개수 (시간)', fontsize=12, fontweight='bold')
axes[2].set_title('Train/Validation/Test 데이터 개수 비교', fontsize=14, fontweight='bold')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('데이터_분할_시각화_통합.png', dpi=150, bbox_inches='tight')
print("💾 저장: 데이터_분할_시각화_통합.png")
plt.show()

# ========================================
# 7. CSV 저장
# ========================================
print("\n" + "="*70)
print("💾 분할된 데이터 저장 중...")
print("="*70)

train_df[['timestamp', '전력수요량']].to_csv('train_data.csv', index=False, encoding='utf-8-sig')
print(f"✅ 'train_data.csv' 저장 완료! ({len(train_df):,}개)")

val_df[['timestamp', '전력수요량']].to_csv('validation_data.csv', index=False, encoding='utf-8-sig')
print(f"✅ 'validation_data.csv' 저장 완료! ({len(val_df):,}개)")

test_df[['timestamp', '전력수요량']].to_csv('test_data.csv', index=False, encoding='utf-8-sig')
print(f"✅ 'test_data.csv' 저장 완료! ({len(test_df):,}개)")

# 통합 데이터도 저장
df[['timestamp', '전력수요량']].to_csv('전체_데이터_통합.csv', index=False, encoding='utf-8-sig')
print(f"✅ '전체_데이터_통합.csv' 저장 완료! ({len(df):,}개)")

# ========================================
# 8. 리포트 저장
# ========================================
print("\n📄 리포트 저장 중...")

with open('데이터_통합_및_분할_리포트.txt', 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("여러 연도 데이터 통합 및 분할 리포트\n")
    f.write("="*70 + "\n\n")
    
    f.write(f"작업 일시: {pd.Timestamp.now()}\n\n")
    
    f.write("="*70 + "\n")
    f.write("통합된 파일 목록\n")
    f.write("="*70 + "\n")
    for year in yearly_counts.index:
        count = yearly_counts[year]
        f.write(f"{year}년: {count:,}개 시간 ({count/24:.1f}일)\n")
    
    f.write(f"\n총 데이터: {len(df):,}개 시간 ({len(df)/24:.1f}일)\n\n")
    
    f.write("="*70 + "\n")
    f.write("데이터 분할 전략\n")
    f.write("="*70 + "\n")
    f.write("목적: Zero-shot vs Fine-tuned 모델 성능 비교\n\n")
    f.write("Train: 2019~2021년 (Fine-tuning 학습용)\n")
    f.write("Validation: 2022년 (과적합 방지)\n")
    f.write("Test: 2023년 + 2024년 1~5월 (공정 비교)\n\n")
    
    f.write("="*70 + "\n")
    f.write("분할 결과\n")
    f.write("="*70 + "\n")
    f.write(f"Train: {len(train_df):,}개 ({len(train_df)/len(df)*100:.1f}%)\n")
    f.write(f"  기간: {train_df['timestamp'].min()} ~ {train_df['timestamp'].max()}\n")
    f.write(f"  평균: {train_df['전력수요량'].mean():.2f} MWh\n\n")
    
    f.write(f"Validation: {len(val_df):,}개 ({len(val_df)/len(df)*100:.1f}%)\n")
    f.write(f"  기간: {val_df['timestamp'].min()} ~ {val_df['timestamp'].max()}\n")
    f.write(f"  평균: {val_df['전력수요량'].mean():.2f} MWh\n\n")
    
    f.write(f"Test: {len(test_df):,}개 ({len(test_df)/len(df)*100:.1f}%)\n")
    f.write(f"  기간: {test_df['timestamp'].min()} ~ {test_df['timestamp'].max()}\n")
    f.write(f"  평균: {test_df['전력수요량'].mean():.2f} MWh\n")

print(f"✅ '데이터_통합_및_분할_리포트.txt' 저장 완료!")

# ========================================
# 최종 요약
# ========================================
print("\n" + "="*70)
print("✅ 데이터 통합 및 분할 완료!")
print("="*70)
print(f"\n생성된 파일:")
print(f"  📄 train_data.csv ({len(train_df):,}개)")
print(f"  📄 validation_data.csv ({len(val_df):,}개)")
print(f"  📄 test_data.csv ({len(test_df):,}개)")
print(f"  📄 전체_데이터_통합.csv ({len(df):,}개)")
print(f"  📊 데이터_분할_시각화_통합.png")
print(f"  📄 데이터_통합_및_분할_리포트.txt")
print("\n다음 단계:")
print(f"  1️⃣ '03_Zero-shot_추론.py' 실행 (Pre-trained 모델)")
print(f"  2️⃣ '04_Fine-tuning.py' 실행 (내 데이터 학습)")
print(f"  3️⃣ '05_성능_비교.py' 실행 (결과 비교)")
print("="*70)