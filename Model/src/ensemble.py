import pandas as pd
import numpy as np
from neuralforecast import NeuralForecast
from neuralforecast.models import LSTM, GRU, NHITS
from neuralforecast.losses.pytorch import MAE
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import time
import os
import pickle
import shutil
import warnings
warnings.filterwarnings('ignore')

# lightning_logs 문제 해결: 기존 폴더 삭제 및 재생성
if os.path.exists('lightning_logs'):
    try:
        if os.path.isfile('lightning_logs'):
            os.remove('lightning_logs')
        else:
            shutil.rmtree('lightning_logs')
    except:
        pass

# 폰트 설정 (한글 깨짐 방지)
try:
    # Windows
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    try:
        # Mac
        plt.rcParams['font.family'] = 'AppleGothic'
    except:
        # Linux 또는 폰트 없을 경우
        plt.rcParams['font.family'] = 'DejaVu Sans'
        print("⚠️ 한글 폰트를 찾을 수 없어 영문으로 표시됩니다.")

plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("🎯 앙상블 + Dropout + 최적화된 특성 선택")
print("="*70)

# ========================================
# 1. 데이터 로드
# ========================================
print("\n📂 데이터 로드 중...")
train_df = pd.read_csv("../../Data/weather/train_data_fixed.csv")
val_df = pd.read_csv("../../Data/weather/validation_data_fixed.csv")
test_df = pd.read_csv("../../Data/weather/test_data_fixed_filtered.csv")

for df in [train_df, val_df, test_df]:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

# ========================================
# 2. 상관관계 분석으로 중요 변수 선택
# ========================================
print("\n🔍 상관관계 분석 중...")

for df in [train_df, val_df, test_df]:
    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
    df['dayofyear'] = df['timestamp'].dt.dayofyear

# 상관계수 계산
corr_features = ['전력수요량', 'temp', 'rain', 'humidity', 'insolation', 'cloud', 
                 'hour', 'month']
correlation = train_df[corr_features].corr()['전력수요량'].sort_values(ascending=False)

print("\n📊 전력수요량과의 상관계수:")
for var, corr_val in correlation.items():
    if var != '전력수요량':
        print(f"   {var:15s}: {corr_val:7.4f}")

# 상관계수 0.1 이상인 변수만 선택 (절대값)
important_features = [var for var in correlation.index 
                     if var != '전력수요량' and abs(correlation[var]) > 0.1]
print(f"\n✅ 선택된 중요 변수 ({len(important_features)}개): {important_features}")

# ========================================
# 3. 데이터 준비
# ========================================
def prepare_nf_data(df, feature_list):
    result_df = pd.DataFrame({
        'unique_id': 'jeju_solar',
        'ds': df['timestamp'],
        'y': df['전력수요량']
    })
    
    for col in feature_list:
        result_df[col] = df[col].values
    
    return result_df

train_nf = prepare_nf_data(train_df, important_features)
val_nf = prepare_nf_data(val_df, important_features)
test_nf = prepare_nf_data(test_df, important_features)

validation_length = len(val_nf)

full_df = pd.concat([train_nf, val_nf, test_nf], ignore_index=True)
full_df = full_df.sort_values('ds').reset_index(drop=True)

print(f"✅ 전체 데이터 준비 완료 (총 {len(full_df):,}개)")

# ========================================
# 4. 앙상블 모델 설정 (LSTM + GRU + NHITS)
# ========================================
print("\n⚙️ 앙상블 모델 설정 중...")
print("   - LSTM")
print("   - GRU")
print("   - NHITS")

horizon = 24 * 30
input_size = 24 * 30

models = [
    # Model 1: LSTM (로거 비활성화)
    LSTM(
        h=horizon,
        input_size=input_size,
        hist_exog_list=important_features,
        encoder_n_layers=2,
        encoder_hidden_size=64,
        decoder_layers=2,
        decoder_hidden_size=64,
        scaler_type='standard',
        max_steps=1200,
        batch_size=32,
        learning_rate=1e-3,
        early_stop_patience_steps=5,
        loss=MAE(),
        random_seed=42,
        logger=False,  # 로거 비활성화
        alias='LSTM'
    ),
    
    # Model 2: GRU (로거 비활성화)
    GRU(
        h=horizon,
        input_size=input_size,
        hist_exog_list=important_features,
        encoder_n_layers=2,
        encoder_hidden_size=64,
        decoder_layers=2,
        decoder_hidden_size=64,
        scaler_type='standard',
        max_steps=1200,
        batch_size=32,
        learning_rate=1e-3,
        early_stop_patience_steps=5,
        loss=MAE(),
        random_seed=123,
        logger=False,  # 로거 비활성화
        alias='GRU'
    ),
    
    # Model 3: NHITS (로거 비활성화)
    NHITS(
        h=horizon,
        input_size=input_size,
        hist_exog_list=important_features,
        stack_types=['identity', 'identity', 'identity'],
        n_blocks=[1, 1, 1],
        mlp_units=[[64, 64], [64, 64], [64, 64]],
        scaler_type='standard',
        max_steps=1200,
        batch_size=32,
        learning_rate=1e-3,
        early_stop_patience_steps=5,
        loss=MAE(),
        random_seed=456,
        logger=False,  # 로거 비활성화
        alias='NHITS'
    )
]

nf = NeuralForecast(models=models, freq='H')

# ========================================
# 5. 12개월 연속 예측
# ========================================
print("\n🔄 12개월 연속 예측 수행 중...")
start_time = time.time()

cv_df = nf.cross_validation(
    df=full_df,
    val_size=validation_length,
    n_windows=12,
    step_size=horizon
)

duration = time.time() - start_time
print(f"✅ 예측 완료 (소요시간: {duration/60:.1f}분)")

# ========================================
# 6. 앙상블 예측 생성
# ========================================
print("\n🎯 앙상블 예측 생성 중...")

# 단순 평균 앙상블
cv_df['Ensemble_Mean'] = (cv_df['LSTM'] + 
                          cv_df['GRU'] + 
                          cv_df['NHITS']) / 3

# 가중 평균 앙상블 (LSTM 40%, GRU 30%, NHITS 30%)
cv_df['Ensemble_Weighted'] = (cv_df['LSTM'] * 0.4 + 
                              cv_df['GRU'] * 0.3 + 
                              cv_df['NHITS'] * 0.3)

print("✅ 앙상블 완료")
print("   - Ensemble_Mean: 단순 평균")
print("   - Ensemble_Weighted: 가중 평균 (LSTM 40%, GRU 30%, NHITS 30%)")

# ========================================
# 7. 성능 평가
# ========================================
print("\n📊 성능 평가")

y_true = cv_df['y'].values

results = []
model_names = ['LSTM', 'GRU', 'NHITS', 
               'Ensemble_Mean', 'Ensemble_Weighted']

for model_name in model_names:
    y_pred = cv_df[model_name].values
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    mask = y_true > 0.1
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    
    results.append({
        'Model': model_name,
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE(%)': mape
    })
    
    print(f"\n{model_name}:")
    print(f"   MAE : {mae:.3f}")
    print(f"   RMSE: {rmse:.3f}")
    print(f"   R²  : {r2:.4f}")
    print(f"   MAPE: {mape:.2f}%")

results_df = pd.DataFrame(results).sort_values('MAE')
best_model = results_df.iloc[0]

# ========================================
# 8. 모델 저장
# ========================================
print("\n💾 모델 저장 중...")

if not os.path.exists('../Models'):
    os.makedirs('../Models')

if not os.path.exists('../checkpoint'):
    os.makedirs('../checkpoint')

# [1] NeuralForecast 전체 모델 저장 (.ckpt 파일들)
nf.save(path='../Models/', model_index=None, overwrite=True)
print("   ✅ NeuralForecast 모델 저장: ../Models/")

# [2] 메타 정보 저장 (피클)
model_metadata = {
    'important_features': important_features,
    'horizon': horizon,
    'input_size': input_size,
    'best_model_name': best_model['Model'],
    'best_model_performance': {
        'MAE': best_model['MAE'],
        'RMSE': best_model['RMSE'],
        'R2': best_model['R2'],
        'MAPE': best_model['MAPE(%)']
    },
    'ensemble_weights': {
        'LSTM': 0.4,
        'GRU': 0.3,
        'NHITS': 0.3
    },
    'scaler_type': 'standard',
    'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
}

with open('../checkpoint/model_metadata.pkl', 'wb') as f:
    pickle.dump(model_metadata, f)
print("   ✅ 메타데이터 저장: ../checkpoint/model_metadata.pkl")

# [3] 최고 성능 모델 정보를 JSON으로도 저장
import json
with open('../Models/best_model_info.json', 'w', encoding='utf-8') as f:
    json.dump({
        'best_model': best_model['Model'],
        'performance': {
            'MAE': float(best_model['MAE']),
            'RMSE': float(best_model['RMSE']),
            'R2': float(best_model['R2']),
            'MAPE': float(best_model['MAPE(%)'])
        },
        'features': important_features,
        'saved_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }, f, indent=4, ensure_ascii=False)
print("   ✅ 최고 성능 모델 정보: ../Models/best_model_info.json")

# ========================================
# 9. 결과 저장
# ========================================
print("\n💾 결과 저장 중...")

if not os.path.exists('../Results'):
    os.makedirs('../Results')

# [1] 예측 데이터
cv_df.to_csv('../Results/앙상블_예측_데이터.csv', index=False, encoding='utf-8-sig')
print("   ✅ 앙상블_예측_데이터.csv")

# [2] 성능 비교
results_df['Rank'] = range(1, len(results_df) + 1)
results_df.to_csv('../Results/앙상블_성능_비교.csv', index=False, encoding='utf-8-sig')
print("   ✅ 앙상블_성능_비교.csv")

# [3] 최종 성능 요약
summary_df = pd.DataFrame([{
    'Best_Model': best_model['Model'],
    'MAE': best_model['MAE'],
    'RMSE': best_model['RMSE'],
    'R2': best_model['R2'],
    'MAPE(%)': best_model['MAPE(%)'],
    'Training_Time(min)': round(duration/60, 2),
    'Features_Used': ', '.join(important_features),
    'Num_Features': len(important_features),
    'Early_Stopping': 'Yes (patience=5)',
    'Ensemble': 'Yes'
}])
summary_df.to_csv('../Results/최종_성능_요약.csv', index=False, encoding='utf-8-sig')
print("   ✅ 최종_성능_요약.csv")

# ========================================
# 10. 시각화
# ========================================
print("\n📊 시각화 생성 중...")

# 10-1. 모델별 성능 비교
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# MAE 비교
axes[0, 0].barh(results_df['Model'], results_df['MAE'], 
                color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
                edgecolor='black', linewidth=1.5)
axes[0, 0].set_xlabel('MAE (Lower is Better)')
axes[0, 0].set_title('Model Performance - MAE', fontweight='bold', fontsize=12)
axes[0, 0].invert_yaxis()
axes[0, 0].grid(alpha=0.3, axis='x')

# R² 비교
axes[0, 1].barh(results_df['Model'], results_df['R2'],
                color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
                edgecolor='black', linewidth=1.5)
axes[0, 1].set_xlabel('R-squared (Higher is Better)')
axes[0, 1].set_title('Model Performance - R2', fontweight='bold', fontsize=12)
axes[0, 1].invert_yaxis()
axes[0, 1].grid(alpha=0.3, axis='x')

# 전체 예측 결과 (Best Model)
best_model_name = best_model['Model']
sample_size = min(5000, len(cv_df))
sample_indices = np.random.choice(len(cv_df), sample_size, replace=False)
sample_indices = np.sort(sample_indices)

axes[1, 0].scatter(cv_df.iloc[sample_indices]['y'], 
                   cv_df.iloc[sample_indices][best_model_name],
                   alpha=0.3, s=1, color='steelblue')
axes[1, 0].plot([cv_df['y'].min(), cv_df['y'].max()], 
                [cv_df['y'].min(), cv_df['y'].max()],
                'r--', linewidth=2, label='Perfect Prediction')
axes[1, 0].set_xlabel('Actual Power Demand')
axes[1, 0].set_ylabel('Predicted Power Demand')
axes[1, 0].set_title(f'Actual vs Predicted ({best_model_name})', fontweight='bold', fontsize=12)
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

# 성능 순위 테이블
axes[1, 1].axis('off')
table_data = []
for idx, row in results_df.iterrows():
    table_data.append([
        f"#{row['Rank']}",
        row['Model'],
        f"{row['MAE']:.2f}",
        f"{row['R2']:.4f}"
    ])

table = axes[1, 1].table(cellText=table_data,
                         colLabels=['Rank', 'Model', 'MAE', 'R2'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0.2, 1, 0.7])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.5)

# 헤더 스타일
for i in range(4):
    table[(0, i)].set_facecolor('#2C3E50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 1위 강조
for i in range(4):
    table[(1, i)].set_facecolor('#FFD700')
    table[(1, i)].set_text_props(weight='bold')

axes[1, 1].set_title('Performance Ranking', fontweight='bold', fontsize=14, pad=20)

plt.tight_layout()
plt.savefig('../Results/앙상블_성능_비교.png', dpi=300, bbox_inches='tight')
print("   ✅ 앙상블_성능_비교.png")

# 10-2. 시계열 예측 결과
fig, axes = plt.subplots(3, 1, figsize=(20, 15))

# 처음 2000개 데이터포인트만 시각화
plot_range = slice(0, min(2000, len(cv_df)))

# 개별 모델
axes[0].plot(cv_df['ds'].iloc[plot_range], cv_df['y'].iloc[plot_range], 
            label='Actual', color='black', alpha=0.5, linewidth=1)
axes[0].plot(cv_df['ds'].iloc[plot_range], cv_df['LSTM'].iloc[plot_range],
            label='LSTM', color='red', alpha=0.6, linewidth=0.8)
axes[0].plot(cv_df['ds'].iloc[plot_range], cv_df['GRU'].iloc[plot_range],
            label='GRU', color='blue', alpha=0.6, linewidth=0.8)
axes[0].plot(cv_df['ds'].iloc[plot_range], cv_df['NHITS'].iloc[plot_range],
            label='NHITS', color='green', alpha=0.6, linewidth=0.8)
axes[0].set_ylabel('Power Demand')
axes[0].set_title('Individual Models Prediction', fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(alpha=0.3)

# 앙상블 모델
axes[1].plot(cv_df['ds'].iloc[plot_range], cv_df['y'].iloc[plot_range],
            label='Actual', color='black', alpha=0.5, linewidth=1.5)
axes[1].plot(cv_df['ds'].iloc[plot_range], cv_df['Ensemble_Mean'].iloc[plot_range],
            label='Ensemble (Mean)', color='purple', alpha=0.7, linewidth=1.2)
axes[1].plot(cv_df['ds'].iloc[plot_range], cv_df['Ensemble_Weighted'].iloc[plot_range],
            label='Ensemble (Weighted)', color='orange', alpha=0.7, linewidth=1.2)
axes[1].set_ylabel('Power Demand')
axes[1].set_title('Ensemble Models Prediction', fontweight='bold')
axes[1].legend(loc='upper right')
axes[1].grid(alpha=0.3)

# 최고 성능 모델
axes[2].plot(cv_df['ds'].iloc[plot_range], cv_df['y'].iloc[plot_range],
            label='Actual', color='black', alpha=0.5, linewidth=1.5)
axes[2].plot(cv_df['ds'].iloc[plot_range], cv_df[best_model_name].iloc[plot_range],
            label=f'Best Model ({best_model_name})', color='darkgreen', 
            alpha=0.8, linewidth=1.2)
axes[2].set_xlabel('Date')
axes[2].set_ylabel('Power Demand')
axes[2].set_title(f'Best Model: {best_model_name} (R²={best_model["R2"]:.4f})', 
                 fontweight='bold')
axes[2].legend(loc='upper right')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('../Results/앙상블_시계열_예측.png', dpi=300, bbox_inches='tight')
print("   ✅ 앙상블_시계열_예측.png")

# ========================================
# 11. 최종 결과 요약
# ========================================
print("\n" + "="*70)
print("🏆 최종 결과 요약")
print("="*70)
print(f"\n최고 성능 모델: {best_model['Model']}")
print(f"   MAE  : {best_model['MAE']:.3f}")
print(f"   RMSE : {best_model['RMSE']:.3f}")
print(f"   R²   : {best_model['R2']:.4f}")
print(f"   MAPE : {best_model['MAPE(%)']:.2f}%")
print(f"\n사용된 특성 ({len(important_features)}개):")
for feat in important_features:
    print(f"   - {feat}")
print(f"\n총 학습 시간: {duration/60:.1f}분")
print(f"정규화 방법: Early Stopping (patience=5)")
print(f"앙상블 방법: Mean + Weighted Average")
print("="*70)

print("\n📦 저장된 모델 파일:")
print("   - ../Models/*.ckpt (NeuralForecast 모델)")
print("   - ../checkpoint/model_metadata.pkl (메타데이터)")
print("   - ../Models/best_model_info.json (최고 성능 모델 정보)")