import pandas as pd
import numpy as np
from neuralforecast import NeuralForecast
from neuralforecast.models import LSTM
from neuralforecast.losses.pytorch import MAE
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("📅 1년치 Rolling Forecast 및 성능 지표 별도 저장")
print("="*70)

# ========================================
# 1. 데이터 로드 및 전처리
# ========================================
print("\n📂 데이터 병합 중...")
train_df = pd.read_csv("../train_data_fixed.csv")
val_df = pd.read_csv("../validation_data_fixed.csv")
test_df = pd.read_csv("../test_data_fixed_filtered.csv")

# 날짜 변환
train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])

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

# 전체 데이터 통합
full_df = pd.concat([train_nf, val_nf, test_nf], ignore_index=True)
full_df = full_df.sort_values('ds').reset_index(drop=True)

print(f"✅ 전체 데이터 준비 완료 (총 {len(full_df):,}개)")

# ========================================
# 2. LSTM 모델 설정
# ========================================
print("\n⚙️ LSTM 모델 설정")
horizon = 24 * 30       
input_size = 24 * 30    

models = [
    LSTM(
        h=horizon,
        input_size=input_size,
        encoder_n_layers=2,
        encoder_hidden_size=64,
        decoder_layers=2,
        decoder_hidden_size=64,
        scaler_type='standard',
        max_steps=1000,
        batch_size=32,
        learning_rate=1e-3,
        early_stop_patience_steps=3, # 조기 종료 사용
        loss=MAE(),
        random_seed=42,
        alias='LSTM'
    )
]

nf = NeuralForecast(models=models, freq='H')

# ========================================
# 3. 12개월 연속 예측 (Cross Validation)
# ========================================
print("\n🔄 12개월 연속 예측 수행 중...")
start_time = time.time()

cv_df = nf.cross_validation(
    df=full_df,
    val_size=validation_length, # 검증 데이터 사용
    n_windows=12,
    step_size=horizon
)

duration = time.time() - start_time
print(f"✅ 예측 완료 (소요시간: {duration/60:.1f}분)")

# ========================================
# 4. 성능 평가 및 파일 저장 (핵심 ⭐)
# ========================================
print("\n📊 성능 분석 및 저장")

y_true = cv_df['y'].values
y_pred = cv_df['LSTM'].values

# 지표 계산
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

mask = y_true > 0.1
if mask.sum() > 0:
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
else:
    mape = np.nan

print(f"   - MAE : {mae:.3f}")
print(f"   - RMSE: {rmse:.3f}")
print(f"   - R²  : {r2:.4f}")

if not os.path.exists('../Results'):
    os.makedirs('../Results')

# [파일 1] 예측 결과 데이터 저장 (날짜, 실제값, 예측값)
# -----------------------------------------------------
prediction_save_name = '../Results/1년_예측_데이터.csv'
cv_df.to_csv(prediction_save_name, index=False, encoding='utf-8-sig')
print(f"💾 예측 데이터 저장: {prediction_save_name}")

# [파일 2] 성능 지표 별도 저장 (MAE, R2 등 점수표)
# -----------------------------------------------------
performance_save_name = '../Results/1년_성능_지표.csv'

# 보기 좋게 DataFrame으로 만들기
perf_df = pd.DataFrame([{
    '모델명': 'LSTM (12개월 Rolling)',
    'MAE (오차)': mae,
    'RMSE (오차)': rmse,
    'MAPE (%)': mape,
    'R2 (정확도)': r2,
    '총 소요시간(분)': round(duration/60, 2),
    '비고': 'Validation 적용됨'
}])

perf_df.to_csv(performance_save_name, index=False, encoding='utf-8-sig')
print(f"💾 성능 지표 저장: {performance_save_name} (이 파일을 확인하세요!)")

# ========================================
# 5. 시각화
# ========================================
plt.figure(figsize=(20, 8))
plt.plot(cv_df['ds'], cv_df['y'], label='Actual', color='black', alpha=0.3)
plt.plot(cv_df['ds'], cv_df['LSTM'], label='Prediction', color='green', alpha=0.7)
plt.title(f'12-Month Forecast Result (R²={r2:.4f})')
plt.legend()
plt.tight_layout()
plt.savefig('../Results/1년_예측_그래프.png')
plt.show()

print("\n✅ 모든 작업이 완료되었습니다.")