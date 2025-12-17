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
print("🧠 LSTM - 순환 신경망 시계열 예측 (수정됨)")
print("="*70)

# ========================================
# 1. 데이터 로드
# ========================================
print("\n📂 데이터 로딩 중...")
train_df = pd.read_csv("../train_data_fixed.csv")
val_df = pd.read_csv("../validation_data_fixed.csv")
test_df = pd.read_csv("../test_data_fixed.csv")

train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])

# ========================================
# 2. NeuralForecast 형식 변환
# ========================================
def prepare_nf_data(df):
    return pd.DataFrame({
        'unique_id': 'jeju_solar',
        'ds': df['timestamp'],
        'y': df['전력수요량']
    })

train_nf = prepare_nf_data(train_df)
val_nf = prepare_nf_data(val_df)
test_nf = prepare_nf_data(test_df)
train_val_nf = pd.concat([train_nf, val_nf], ignore_index=True)

# ========================================
# 3. LSTM 모델 설정
# ========================================
print("\n⚙️ LSTM 모델 설정")

horizon = 24 * 30       
input_size = 24 * 30    

models = [
    LSTM(
        h=horizon,
        input_size=input_size,
        
        # LSTM 파라미터
        encoder_n_layers=2,
        encoder_hidden_size=64,
        context_size=10,
        decoder_layers=2,
        decoder_hidden_size=64,
        
        # 학습 설정
        scaler_type='standard',
        max_steps=1000,
        val_check_steps=100,
        early_stop_patience_steps=3,
        batch_size=32,
        learning_rate=1e-3,
        
        # 기타
        loss=MAE(),
        random_seed=42,
        alias='LSTM'
    )
]

nf = NeuralForecast(models=models, freq='H')

# ========================================
# 4. 모델 학습
# ========================================
print("\n🎓 모델 학습 시작")
train_start = time.time()

nf.fit(df=train_val_nf, val_size=len(val_nf))

train_time = time.time() - train_start
print(f"\n✅ 학습 완료! (소요: {train_time/60:.1f}분)")

# ========================================
# 5. Test 예측
# ========================================
print("\n🧪 Test 데이터 예측")
predict_start = time.time()

try:
    pred = nf.predict(df=train_val_nf)
    y_pred = pred['LSTM'].values
    y_true = test_df['전력수요량'].values[:len(y_pred)]
    predict_time = time.time() - predict_start
    print("✅ 예측 완료!")
except Exception as e:
    print(f"❌ 예측 실패: {e}")
    y_pred = np.zeros(len(test_df))
    y_true = test_df['전력수요량'].values
    predict_time = 0

# ========================================
# 6. 결과 저장 및 시각화 (⭐ 성능 CSV 저장 추가됨)
# ========================================
print("\n📊 결과 저장 중...")

# --- 1) 성능 지표 계산 ---
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

# MAPE 계산 (0으로 나누기 방지)
non_zero_mask = y_true > 0.1
if non_zero_mask.sum() > 0:
    mape = np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
else:
    mape = np.nan

print(f"MAE: {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"MAPE: {mape:.2f}%")
print(f"R2: {r2:.4f}")

# --- 2) 예측 결과 CSV 저장 ---
result_df = pd.DataFrame({
    'timestamp': test_df['timestamp'].values[:len(y_pred)],
    '실제': y_true,
    'LSTM_예측': y_pred
})
if not os.path.exists('../Results'):
    os.makedirs('../Results')

result_df.to_csv('../Results/결과_LSTM.csv', index=False, encoding='utf-8-sig')
print("💾 '결과_LSTM.csv' 저장 완료")

# --- 3) ⭐ 성능 지표 CSV 저장 (추가된 부분) ---
performance_df = pd.DataFrame([{
    'Model': 'LSTM',
    'MAE': mae,
    'RMSE': rmse,
    'MAPE': mape,
    'R2': r2,
    'Train_Time(min)': train_time / 60,
    'Predict_Time(sec)': predict_time
}])

performance_df.to_csv('../Results/성능_LSTM.csv', index=False, encoding='utf-8-sig')
print("💾 '성능_LSTM.csv' 저장 완료")

# --- 4) 시각화 ---
plt.figure(figsize=(15, 6))
plt.plot(test_df['timestamp'][:len(y_true)], y_true, label='Actual', color='black', alpha=0.5)
plt.plot(test_df['timestamp'][:len(y_pred)], y_pred, label='LSTM', color='orange')
plt.title(f'LSTM Result (MAE: {mae:.2f}, R²: {r2:.4f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('../Results/LSTM_결과.png')
plt.show()

print("\n✅ 모든 과정 완료!")