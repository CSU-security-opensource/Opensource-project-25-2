import pandas as pd
import numpy as np
from chronos import BaseChronosPipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time
import warnings
import torch
import os

# 경고 무시
warnings.filterwarnings('ignore')

# 폰트 설정
try:
    import matplotlib.font_manager as fm
    font_list = [f.name for f in fm.fontManager.ttflist]
    if 'NanumGothic' in font_list:
        plt.rcParams['font.family'] = 'NanumGothic'
    elif 'Malgun Gothic' in font_list:
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans' 
except:
    pass
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("🧠 Chronos (T5-Large) - 1년치 Rolling Forecast")
print("="*70)

# ========================================
# 1. 모델 로드
# ========================================
print("\n📦 Chronos 모델 로딩 중...")

device_map = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Using device: {device_map.upper()}")

# 모델 사이즈: tiny, mini, small, base, large
model_name = 'amazon/chronos-t5-large' 

start_time = time.time()
try:
    pipeline = BaseChronosPipeline.from_pretrained(
        model_name, 
        device_map=device_map,
        torch_dtype=torch.bfloat16 if device_map == "cuda" else torch.float32
    )
    print(f"✅ 모델 로드 완료! (소요: {time.time() - start_time:.1f}초)")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    exit()

# ========================================
# 2. 데이터 로드
# ========================================
print("\n📂 데이터 로딩 중...")

# 1년치(2023년) 데이터가 있는 filtered 파일을 사용합니다.
train_df = pd.read_csv("../train_data_fixed.csv")
val_df = pd.read_csv("../validation_data_fixed.csv")
test_df = pd.read_csv("../test_data_fixed_filtered.csv") # 2024년 제외된 파일

# datetime 변환
train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])

print(f"✅ 데이터 로드 완료")
print(f"   Test 데이터 기간: {test_df['timestamp'].min()} ~ {test_df['timestamp'].max()}")

# ========================================
# 3. Rolling Forecast (핵심 로직)
# ========================================
print("\n🔄 1년치 Rolling Forecast 시작 (30일씩 끊어서 예측)")
print("   (방식: 예측 -> 실제값 Context 추가 -> 다음 달 예측)")

# 초기 Context: Train + Val
history_df = pd.concat([train_df, val_df]).sort_values('timestamp').reset_index(drop=True)

# 예측 설정
horizon = 24 * 30  # 30일 (720시간)
total_steps = len(test_df)
predictions = []

predict_start_time = time.time()

# 반복문으로 30일씩 전진하며 예측
for i in range(0, total_steps, horizon):
    # 이번에 예측할 길이 (마지막 달은 30일보다 짧을 수 있음)
    current_horizon = min(horizon, total_steps - i)
    
    # 진행 상황 출력
    progress = (i / total_steps) * 100
    print(f"   Running... {progress:.1f}% ({i}/{total_steps})")
    
    # 1. Context 데이터프레임 생성 (현재까지의 역사)
    context_df = pd.DataFrame({
        'item_id': 'jeju_solar',
        'timestamp': history_df['timestamp'],
        'value': history_df['전력수요량']
    })
    
    # 2. Chronos 예측 수행
    # context는 길어지면 Chronos가 알아서 뒤쪽(최신) 위주로 자릅니다.
    forecast = pipeline.predict_df(
        context_df,
        prediction_length=current_horizon,
        quantile_levels=[0.5], # 중앙값만 예측 (속도 향상)
        id_column="item_id",
        timestamp_column="timestamp",
        target="value"
    )
    
    # 3. 예측 결과 저장
    # 음수값 보정
    pred_values = forecast['0.5'].clip(lower=0).values
    predictions.extend(pred_values)
    
    # 4. [중요] 실제값(Ground Truth)을 History에 추가 (다음 예측을 위해)
    actual_chunk = test_df.iloc[i : i + current_horizon]
    history_df = pd.concat([history_df, actual_chunk], ignore_index=True)

total_duration = time.time() - predict_start_time
print(f"✅ 1년치 예측 완료! (소요: {total_duration/60:.1f}분)")

# ========================================
# 4. 성능 평가
# ========================================
print("\n📊 성능 분석")

y_true = test_df['전력수요량'].values
y_pred = np.array(predictions[:len(y_true)]) # 길이 맞추기

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

# MAPE (0 제외)
mask = y_true > 0.1
if mask.sum() > 0:
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
else:
    mape = np.nan

print(f"   - MAE : {mae:.3f} MWh")
print(f"   - RMSE: {rmse:.3f} MWh")
print(f"   - MAPE: {mape:.2f} %")
print(f"   - R²  : {r2:.4f}")

# ========================================
# 5. 결과 저장
# ========================================
if not os.path.exists('../Results'):
    os.makedirs('../Results')

# 1) 예측 데이터 CSV
result_df = pd.DataFrame({
    'timestamp': test_df['timestamp'],
    'Actual': y_true,
    'Chronos_Pred': y_pred
})
save_path_data = "../Results/Chronos_1년_Rolling_예측.csv"
result_df.to_csv(save_path_data, index=False, encoding='utf-8-sig')
print(f"\n💾 예측 데이터 저장: {save_path_data}")

# 2) 성능 지표 CSV
perf_df = pd.DataFrame([{
    '모델': 'Chronos (T5-Large)',
    '방식': '1년 Rolling Forecast',
    'MAE': mae,
    'RMSE': rmse,
    'MAPE': mape,
    'R2': r2,
    '소요시간(분)': round(total_duration/60, 2)
}])
save_path_perf = "../Results/Chronos_1년_성능_지표.csv"
perf_df.to_csv(save_path_perf, index=False, encoding='utf-8-sig')
print(f"💾 성능 지표 저장: {save_path_perf}")

# ========================================
# 6. 시각화
# ========================================
print("📈 그래프 생성 중...")

plt.figure(figsize=(20, 8))
plt.plot(test_df['timestamp'], y_true, label='Actual', color='black', alpha=0.3)
plt.plot(test_df['timestamp'], y_pred, label='Chronos (1년 예측)', color='#8A2BE2', alpha=0.8) # 보라색

plt.title(f'Chronos 1-Year Rolling Forecast (R²={r2:.4f})', fontsize=16, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Power Generation (MWh)')
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('../Results/Chronos_1년_예측_그래프.png')
print("💾 그래프 저장: ../Results/Chronos_1년_예측_그래프.png")
plt.show()

print("\n✅ 모든 작업 완료!")