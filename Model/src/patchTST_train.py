import pandas as pd
import numpy as np
from neuralforecast import NeuralForecast
from neuralforecast.models import PatchTST
from neuralforecast.losses.pytorch import MAE
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("🧠 PatchTST - 1년치(12개월) Rolling Forecast")
print("="*70)

# ========================================
# 1. 데이터 로드 및 통합
# ========================================
print("\n📂 데이터 로딩 및 병합 중...")

train_df = pd.read_csv("../train_data_fixed.csv")
val_df = pd.read_csv("../validation_data_fixed.csv")
test_df = pd.read_csv("../test_data_fixed_filtered.csv") # 2024년 제외된 파일 사용 권장

# 날짜 변환
train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])

# NeuralForecast 형식 변환
def prepare_nf_data(df):
    return pd.DataFrame({
        'unique_id': 'jeju_solar',
        'ds': df['timestamp'],
        'y': df['전력수요량']
    })

train_nf = prepare_nf_data(train_df)
val_nf = prepare_nf_data(val_df)
test_nf = prepare_nf_data(test_df)

# Validation 데이터 길이 저장 (검증용)
validation_length = len(val_nf)

# ⭐ 전체 데이터 합치기 (Train + Val + Test)
# Rolling Forecast를 위해 전체 타임라인이 필요함
full_df = pd.concat([train_nf, val_nf, test_nf], ignore_index=True)
full_df = full_df.sort_values('ds').reset_index(drop=True)

print(f"✅ 전체 데이터 통합 완료: {len(full_df):,}개 시간")
print(f"   기간: {full_df['ds'].min()} ~ {full_df['ds'].max()}")

# ========================================
# 2. PatchTST 모델 설정
# ========================================
print("\n" + "="*70)
print("⚙️ PatchTST 모델 설정")
print("="*70)

horizon = 24 * 30       # 30일
input_size = 24 * 30    # 30일

print(f"\n모델 하이퍼파라미터:")
print(f"  - 입력 길이: {input_size}")
print(f"  - 예측 길이: {horizon}")

models = [
    PatchTST(
        h=horizon,
        input_size=input_size,
        
        # 모델 구조 (기존 설정 유지)
        patch_len=24,
        stride=12,
        hidden_size=128,
        n_heads=4,
        encoder_layers=3,
        dropout=0.1,
        
        # 학습 설정
        scaler_type='standard',
        max_steps=1000,
        batch_size=32,
        learning_rate=1e-4,
        
        # Validation 기반 조기 종료 (Validation Size를 활용하기 위함)
        early_stop_patience_steps=3,
        val_check_steps=100,
        
        loss=MAE(),
        random_seed=42,
        alias='PatchTST'
    )
]

nf = NeuralForecast(models=models, freq='H')

# ========================================
# 3. 12개월 연속 예측 (Cross Validation)
# ========================================
print("\n🔄 12개월 연속 예측 시작 (Rolling Forecast)")
print("   (방식: 1월 예측 -> 이동 -> 2월 예측 ... -> 12월 예측)")

start_time = time.time()

# ⭐ 핵심 함수: cross_validation
cv_df = nf.cross_validation(
    df=full_df,
    val_size=validation_length, # 검증 데이터 활용 (Early Stopping 작동)
    n_windows=12,               # 12개월 반복
    step_size=horizon           # 30일씩 이동
)

duration = time.time() - start_time
print(f"\n✅ 1년치 예측 완료! (소요시간: {duration/60:.1f}분)")

# ========================================
# 4. 성능 평가 및 저장
# ========================================
print("="*70)
print("📊 1년 전체 평균 성능 평가")
print("="*70)

y_true = cv_df['y'].values
y_pred = cv_df['PatchTST'].values

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

# MAPE (0 제외)
mask = y_true > 0.1
if mask.sum() > 0:
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
else:
    mape = np.nan

print(f"【 PatchTST 1년 성적표 】")
print(f"MAE:  {mae:>10.3f} MWh")
print(f"RMSE: {rmse:>10.3f} MWh")
print(f"MAPE: {mape:>10.2f} %")
print(f"R²:   {r2:>10.4f}")

# ----------------------------------------
# 파일 저장
# ----------------------------------------
if not os.path.exists('../Results'):
    os.makedirs('../Results')

# 1) 예측 결과 데이터 (CSV)
save_path_data = '../Results/PatchTST_1년_예측_데이터.csv'
cv_df.to_csv(save_path_data, index=False, encoding='utf-8-sig')
print(f"\n💾 예측 데이터 저장: {save_path_data}")

# 2) 성능 지표 (CSV)
save_path_perf = '../Results/PatchTST_1년_성능_지표.csv'
perf_df = pd.DataFrame([{
    '모델': 'PatchTST (1 Year Rolling)',
    'MAE': mae,
    'RMSE': rmse,
    'MAPE': mape,
    'R2': r2,
    '소요시간(분)': round(duration/60, 2)
}])
perf_df.to_csv(save_path_perf, index=False, encoding='utf-8-sig')
print(f"💾 성능 지표 저장: {save_path_perf}")

# ========================================
# 5. 시각화
# ========================================
print("📈 그래프 생성 중...")

plt.figure(figsize=(20, 8))
plt.plot(cv_df['ds'], cv_df['y'], label='Actual (실제)', color='black', alpha=0.3)
plt.plot(cv_df['ds'], cv_df['PatchTST'], label='PatchTST (1년 예측)', color='#06A77D', alpha=0.8)

plt.title(f'PatchTST 1-Year Rolling Forecast (R²={r2:.4f})', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Power Generation (MWh)', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('../Results/PatchTST_1년_예측_그래프.png')
print("💾 그래프 저장: ../Results/PatchTST_1년_예측_그래프.png")
plt.show()

# 모델 저장
nf.save(path='./patchtst_model_yearly/', overwrite=True)
print("\n✅ 모델 저장 완료: ./patchtst_model_yearly/")