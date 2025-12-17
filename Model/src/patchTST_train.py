import pandas as pd
import numpy as np
from neuralforecast import NeuralForecast
from neuralforecast.models import PatchTST
from neuralforecast.losses.pytorch import MAE, MSE
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

"""
=============================================================================
PatchTST: 최신 트랜스포머 기반 시계열 예측
=============================================================================
논문: A Time Series is Worth 64 Words (ICLR 2023)
- Patch-based self-attention
- SOTA 성능
=============================================================================
"""

print("="*70)
print("🧠 PatchTST - 최신 트랜스포머 시계열 예측")
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

print("✅ 데이터 로드 완료!")

print(f"\n📊 데이터 정보:")
print(f"  Train: {len(train_df):,}개 ({len(train_df)/24:.0f}일)")
print(f"  Val:   {len(val_df):,}개 ({len(val_df)/24:.0f}일)")
print(f"  Test:  {len(test_df):,}개 ({len(test_df)/24:.0f}일)")

# ========================================
# 2. NeuralForecast 형식으로 변환
# ========================================
print("\n🔄 NeuralForecast 형식 변환 중...")

# NeuralForecast 필수 컬럼: unique_id, ds, y
def prepare_nf_data(df):
    """NeuralForecast 형식으로 변환"""
    nf_df = pd.DataFrame({
        'unique_id': 'jeju_solar',  # 시계열 ID
        'ds': df['timestamp'],       # datetime
        'y': df['전력수요량']         # target
    })
    return nf_df

train_nf = prepare_nf_data(train_df)
val_nf = prepare_nf_data(val_df)
test_nf = prepare_nf_data(test_df)

# Train + Val 합치기 (학습용)
train_val_nf = pd.concat([train_nf, val_nf], ignore_index=True)

print("✅ 변환 완료!")
print(f"\n학습 데이터 샘플:")
print(train_nf.head())

# patchTST_inference.py 수정

## ========================================
# 3. PatchTST 모델 설정 (수정)
# ========================================
print("\n" + "="*70)
print("⚙️ PatchTST 모델 설정")
print("="*70)

horizon = 24 * 30       # 30일
input_size = 24 * 30    # 30일

print(f"\n모델 하이퍼파라미터:")
print(f"  - 입력 길이: {input_size}개 시간 ({input_size/24:.0f}일)")
print(f"  - 예측 길이: {horizon}개 시간 ({horizon/24:.0f}일)")

# ⭐ 수정: 파라미터 정리
models = [
    PatchTST(
        h=horizon,
        input_size=input_size,
        
        # 모델 구조
        patch_len=24,
        stride=12,
        hidden_size=128,
        n_heads=4,
        encoder_layers=3,        # ⭐ num_layers → encoder_layers
        dropout=0.1,
        
        # 학습 설정
        scaler_type='standard',
        max_steps=1000,
        val_check_steps=100,
        early_stop_patience_steps=3,
        batch_size=32,            # 배치 크기 명시
        learning_rate=1e-4,
        
        # 기타
        loss=MAE(),
        random_seed=42,
        alias='PatchTST'
    )
]

nf = NeuralForecast(models=models, freq='H')
# ========================================
# 4. 모델 학습 (그대로)
# ========================================
print("\n" + "="*70)
print("🎓 모델 학습 시작")
print("="*70)

train_start = time.time()

nf.fit(
    df=train_val_nf,
    val_size=len(val_nf)  # 이제 8760 > 720 이므로 OK!
)

train_time = time.time() - train_start
print(f"\n✅ 학습 완료! (소요: {train_time/60:.1f}분)")
# ========================================
# 5. Test 예측
# ========================================
print("\n" + "="*70)
print("🧪 Test 데이터 예측")
print("="*70)

predict_start = time.time()

try:
    pred = nf.predict(df=train_val_nf)
    y_pred = pred['PatchTST'].values
    y_true = test_df['전력수요량'].values[:len(y_pred)]
    
    predict_time = time.time() - predict_start
    
    print(f"✅ 예측 완료! (소요: {predict_time:.1f}초)")
    print(f"  - 예측: {len(y_pred):,}개 ({len(y_pred)/24:.0f}일)")
    print(f"  - Test 전체: {len(test_df):,}개")
    
except Exception as e:
    print(f"\n❌ 예측 실패: {e}")
    predict_time = 0  # 에러 시 기본값
# ========================================
# 6. 성능 평가
# ========================================
print("="*70)
print("📊 성능 평가")
print("="*70)

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

# MAPE (낮 시간만)
non_zero_mask = y_true > 0.1
if non_zero_mask.sum() > 0:
    mape = np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
else:
    mape = np.nan

mean_actual = np.mean(y_true)
mean_pred = np.mean(y_pred)
bias = np.mean(y_pred - y_true)

print(f"\n{'='*70}")
print(f"🧠 PatchTST 성능 (ICLR 2023)")
print(f"{'='*70}")
print(f"학습 데이터: {len(train_val_nf):,}개 시간")
print(f"평가 데이터: {len(y_true):,}개 시간")
print(f"")
print(f"【 성능 지표 】")
print(f"MAE:  {mae:>10.3f} MWh")
print(f"RMSE: {rmse:>10.3f} MWh")
print(f"MAPE: {mape:>10.2f} %")
print(f"R²:   {r2:>10.4f}")
print(f"Bias: {bias:>10.3f} MWh")
print(f"")
print(f"평균 실제: {mean_actual:.2f} MWh")
print(f"평균 예측: {mean_pred:.2f} MWh")
print(f"{'='*70}\n")

# ========================================
# 7. 시각화
# ========================================
print("📈 시각화 생성 중...\n")

fig, axes = plt.subplots(2, 1, figsize=(20, 12))

# 1) 전체 예측
axes[0].plot(test_df['timestamp'][:len(y_true)], y_true,
             label='실제', color='#2E86AB', linewidth=1.5)
axes[0].plot(test_df['timestamp'][:len(y_pred)], y_pred,
             label='PatchTST 예측', color='#06A77D', linewidth=1.5)

axes[0].set_xlabel('날짜', fontsize=12, fontweight='bold')
axes[0].set_ylabel('발전량 (MWh)', fontsize=12, fontweight='bold')
axes[0].set_title(f'PatchTST 예측 (ICLR 2023) - MAE: {mae:.2f}, R²: {r2:.4f}',
                  fontsize=14, fontweight='bold')
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.3)

# 2) 산점도
axes[1].scatter(y_true, y_pred, alpha=0.3, s=20, color='#06A77D')
axes[1].plot([0, y_true.max()], [0, y_true.max()],
             'r--', linewidth=2, label='완벽한 예측')

axes[1].set_xlabel('실제 (MWh)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('예측 (MWh)', fontsize=12, fontweight='bold')
axes[1].set_title(f'실제 vs 예측 (R²={r2:.4f})', fontsize=14, fontweight='bold')
axes[1].legend(fontsize=11)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../Results/PatchTST_결과.png', dpi=150, bbox_inches='tight')
print("💾 저장: PatchTST_결과.png")
plt.show()

# ========================================
# 8. 결과 저장
# ========================================
result_df = pd.DataFrame({
    'timestamp': test_df['timestamp'].values[:len(y_pred)],
    '실제_MWh': y_true,
    'PatchTST_예측_MWh': y_pred,
    '절대오차': np.abs(y_true - y_pred)
})

result_df.to_csv('../Results/결과_PatchTST.csv', index=False, encoding='utf-8-sig')
print("✅ '결과_PatchTST.csv' 저장!")

performance = pd.DataFrame([{
    '모델': 'PatchTST (ICLR 2023)',
    'MAE': mae,
    'RMSE': rmse,
    'MAPE': mape,
    'R2': r2,
    '학습시간_분': train_time / 60,
    '예측시간_초': predict_time
}])

performance.to_csv('../Results/성능_PatchTST.csv', index=False, encoding='utf-8-sig')
print("✅ '성능_PatchTST.csv' 저장!")

# ========================================
# 9. 모델 저장
# ========================================
print("\n💾 모델 저장 중...")

# 모델 체크포인트 저장 (재사용 가능)
nf.save(
    path='./patchtst_model/',
    overwrite=True
)

print("✅ 모델 저장 완료: './patchtst_model/'")

print("\n" + "="*70)
print("✅ PatchTST 학습 및 평가 완료!")
print("="*70)
print("\n📄 논문 어필 포인트:")
print("  🌟 'ICLR 2023 최신 트랜스포머 모델 적용'")
print("  🌟 'Patch-based Self-Attention 구현'")
print("  🌟 'SOTA 시계열 예측 기법 활용'")
print("="*70)