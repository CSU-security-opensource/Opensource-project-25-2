import pandas as pd
import numpy as np
from chronos import BaseChronosPipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time
import warnings
import torch

warnings.filterwarnings('ignore')
try:
    import matplotlib.font_manager as fm
    font_list = [f.name for f in fm.fontManager.ttflist]
    if 'NanumGothic' in font_list:
        plt.rcParams['font.family'] = 'NanumGothic'
    elif 'Malgun Gothic' in font_list:
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        # 한글 폰트가 없으면 깨짐 방지를 위해 영어 폰트 설정
        plt.rcParams['font.family'] = 'DejaVu Sans' 
except:
    pass

plt.rcParams['axes.unicode_minus'] = False


print("="*70)
print("🌞 제주 태양광 발전 예측 (Chronos Base - Context 수정버전)")
print("="*70)

# ========================================
# 1. 모델 선택 및 로드
# ========================================
print("\n📦 Chronos 모델 로딩 중...")

# GPU 사용 가능 여부 확인
device_map = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Using device: {device_map.upper()}")

model_name = 'amazon/chronos-t5-large' 

start_time = time.time()

try:
    pipeline = BaseChronosPipeline.from_pretrained(
        model_name, 
        device_map=device_map,
        torch_dtype=torch.bfloat16 if device_map == "cuda" else torch.float32
    )
    load_time = time.time() - start_time
    print(f"✅ 모델 로드 완료! (소요: {load_time:.1f}초)\n")
    
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    exit()

# ========================================
# 2. 데이터 로드
# ========================================
print("📂 데이터 로딩 중...")

try:
    train_df = pd.read_csv("../train_data_fixed.csv")
    val_df = pd.read_csv("../validation_data_fixed.csv")
    test_df = pd.read_csv("../test_data_fixed.csv")
    
    # datetime 변환
    train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
    val_df['timestamp'] = pd.to_datetime(val_df['timestamp'])
    test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])
    
    print("✅ 모든 데이터 로드 완료!")
    
except FileNotFoundError as e:
    print(f"❌ 파일 없음: {e}")
    exit()

# ========================================
# 3. Context 데이터 준비 (핵심 수정 부분)
# ========================================
print("\n" + "="*70)
print("📝 Context 데이터 준비 (Data Leakage 방지 및 연결)")
print("="*70)

# Validation 예측용 Context (Train만 사용)
val_context_df = pd.DataFrame({
    'item_id': 'jeju_solar',
    'timestamp': train_df['timestamp'],
    'value': train_df['전력수요량']
})

#  Test 예측용 Context (Train + Validation 합본 사용)
full_history_df = pd.concat([train_df, val_df]).sort_values('timestamp').reset_index(drop=True)

test_context_df = pd.DataFrame({
    'item_id': 'jeju_solar',
    'timestamp': full_history_df['timestamp'],
    'value': full_history_df['전력수요량']
})

print(f"✅ Context 준비 완료:")
print(f"  1. Validation 예측용 (Train Only): {len(val_context_df):,}개 (끝: {val_context_df['timestamp'].max()})")
print(f"  2. Test 예측용 (Train + Val):      {len(test_context_df):,}개 (끝: {test_context_df['timestamp'].max()})")
print(f"     -> Test 데이터 시작점인 {test_df['timestamp'].min()}과 연결됨.")


# ========================================
# 4. Validation 예측
# ========================================
print("\n" + "="*70)
print("🔍 Validation 데이터 예측")
print("="*70)

val_len = len(val_df)
print(f"예측 길이: {val_len:,}개 시간")

try:
    val_pred_df = pipeline.predict_df(
        val_context_df, # Train 데이터만 보고 예측
        prediction_length=val_len,
        quantile_levels=[0.1, 0.5, 0.9],
        id_column="item_id",
        timestamp_column="timestamp",
        target="value",
    )
    
    # 음수값 보정 (Post-processing)
    cols = ['0.1', '0.5', '0.9']
    val_pred_df[cols] = val_pred_df[cols].clip(lower=0)
    
    # 평가
    y_val_true = val_df['전력수요량'].values
    y_val_pred = val_pred_df['0.5'].values[:len(y_val_true)]
    
    val_mae = mean_absolute_error(y_val_true, y_val_pred)
    val_r2 = r2_score(y_val_true, y_val_pred)
    
    print(f"📊 Validation 결과:")
    print(f"  - MAE: {val_mae:.2f} MWh")
    print(f"  - R²:  {val_r2:.4f}")
    
except Exception as e:
    print(f"⚠️ Validation 예측 중 에러: {e}")


# ========================================
# 5. Test 데이터 예측 (최종 평가)
# ========================================
print("\n" + "="*70)
print("🧪 Test 데이터 예측 (최종 평가)")
print("="*70)

test_len = len(test_df)
print(f"예측 길이: {test_len:,}개 시간")
print(f"시작 시각: {pd.Timestamp.now().strftime('%H:%M:%S')}")

test_start = time.time()

try:
    # test_context_df 사용 (Train+Val 데이터)
    test_pred_df = pipeline.predict_df(
        test_context_df, 
        prediction_length=test_len,
        quantile_levels=[0.1, 0.5, 0.9],
        id_column="item_id",
        timestamp_column="timestamp",
        target="value",
    )
    
    # 음수값 보정 (Post-processing)
    cols = ['0.1', '0.5', '0.9']
    test_pred_df[cols] = test_pred_df[cols].clip(lower=0)

    test_time = time.time() - test_start
    print(f"✅ Test 예측 완료! (소요: {test_time/60:.1f}분)")

except Exception as e:
    print(f"❌ Test 예측 실패: {e}")
    exit()

# ========================================
# 6. Test 성능 평가
# ========================================
y_test_true = test_df['전력수요량'].values
y_test_pred = test_pred_df['0.5'].values[:len(y_test_true)]

# 메트릭 계산
mae = mean_absolute_error(y_test_true, y_test_pred)
rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
r2 = r2_score(y_test_true, y_test_pred)

# 낮 시간(06~18시) 성능 별도 계산
hours = test_df['timestamp'].dt.hour.values
day_mask = (hours >= 6) & (hours <= 18)
day_mae = mean_absolute_error(y_test_true[day_mask], y_test_pred[day_mask])

print(f"\n{'='*70}")
print(f"📊 최종 성능 평가 결과")
print(f"{'='*70}")
print(f"MAE (평균 절대 오차):    {mae:.3f} MWh")
print(f"RMSE (평균 제곱근 오차): {rmse:.3f} MWh")
print(f"R² Score (결정계수):     {r2:.4f}")
print(f"낮 시간 MAE:             {day_mae:.3f} MWh")
print(f"평균 실제 발전량:        {np.mean(y_test_true):.3f} MWh")
print(f"평균 예측 발전량:        {np.mean(y_test_pred):.3f} MWh")
print(f"{'='*70}\n")

# ========================================
# 7. 시각화
# ========================================
print("📈 시각화 생성 중...")

fig, axes = plt.subplots(3, 1, figsize=(20, 14))

# 1) 전체 시계열
axes[0].plot(test_df['timestamp'], y_test_true, label='Actual', color='black', alpha=0.6, linewidth=1)
axes[0].plot(test_df['timestamp'], y_test_pred, label='Prediction (Chronos)', color='#007acc', alpha=0.8, linewidth=1)
axes[0].set_title(f'Test Whole Period (R2: {r2:.3f}, MAE: {mae:.2f})', fontsize=14)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 2) 확대 (첫 14일)
zoom_slice = slice(0, 24 * 14)
axes[1].plot(test_df['timestamp'][zoom_slice], y_test_true[zoom_slice], '.-', label='Actual', color='black')
axes[1].plot(test_df['timestamp'][zoom_slice], y_test_pred[zoom_slice], '.-', label='Prediction', color='#007acc')
axes[1].set_title('First 14 Days Zoom-in', fontsize=14)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 3) 산점도
axes[2].scatter(y_test_true, y_test_pred, alpha=0.3, s=10, color='#007acc')
axes[2].plot([0, y_test_true.max()], [0, y_test_true.max()], 'r--', label='Perfect Fit')
axes[2].set_xlabel('Actual')
axes[2].set_ylabel('Predicted')
axes[2].set_title('Actual vs Predicted Scatter', fontsize=14)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../Results/Result_Fixed_Context.png')
print("💾 그래프 저장 완료: Result_Fixed_Context.png")

# CSV 저장
result_df = pd.DataFrame({
    'timestamp': test_df['timestamp'],
    'Actual': y_test_true,
    'Predicted': y_test_pred
})
result_df.to_csv("../Results/Result_Fixed_Context.csv", index=False)
print("💾 결과 CSV 저장 완료: Result_Fixed_Context.csv")

print("\n✅ 모든 작업 완료!")