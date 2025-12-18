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
print("🔬 최적화된 LSTM - 단계별 특성 추가 실험")
print("="*70)

# ========================================
# 1. 데이터 로드
# ========================================
print("\n📂 데이터 로드 중...")
train_df = pd.read_csv("../../Data/train_data_fixed.csv")
val_df = pd.read_csv("../../Data/validation_data_fixed.csv")
test_df = pd.read_csv("../../Data/test_data_fixed_filtered.csv")

for df in [train_df, val_df, test_df]:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

# ========================================
# 2. 상관관계 분석
# ========================================
print("\n📊 특성 상관관계 분석 중...")

# 기본 시간 특성 추가
for df in [train_df, val_df, test_df]:
    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
    df['dayofyear'] = df['timestamp'].dt.dayofyear

# 상관계수 계산
corr_features = ['전력수요량', 'temp', 'rain', 'humidity', 'insolation', 'cloud', 
                 'hour', 'month']
correlation = train_df[corr_features].corr()['전력수요량'].sort_values(ascending=False)

print("\n🔍 전력수요량과의 상관계수:")
print(correlation)

# ========================================
# 3. 여러 모델 실험 준비
# ========================================
def prepare_nf_data(df, feature_list=None):
    """특성 선택이 가능한 데이터 준비 함수"""
    result_df = pd.DataFrame({
        'unique_id': 'jeju_solar',
        'ds': df['timestamp'],
        'y': df['전력수요량']
    })
    
    if feature_list:
        for col in feature_list:
            result_df[col] = df[col].values
    
    return result_df

validation_length = len(val_df)

# 실험할 특성 조합들
experiments = [
    {
        'name': 'Baseline (외부변수 없음)',
        'features': None,
        'params': {
            'encoder_n_layers': 2,
            'encoder_hidden_size': 64,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1000,
            'batch_size': 32
        }
    },
    {
        'name': '기상 변수만',
        'features': ['temp', 'humidity', 'insolation', 'cloud'],
        'params': {
            'encoder_n_layers': 2,
            'encoder_hidden_size': 64,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1000,
            'batch_size': 32
        }
    },
    {
        'name': '시간 특성만',
        'features': ['hour', 'month', 'dayofyear'],
        'params': {
            'encoder_n_layers': 2,
            'encoder_hidden_size': 64,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1000,
            'batch_size': 32
        }
    },
    {
        'name': '핵심 변수 조합',
        'features': ['temp', 'insolation', 'hour', 'month'],
        'params': {
            'encoder_n_layers': 2,
            'encoder_hidden_size': 64,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1000,
            'batch_size': 32
        }
    },
    {
        'name': '모든 변수 (작은 모델)',
        'features': ['temp', 'rain', 'humidity', 'insolation', 'cloud', 
                    'hour', 'month', 'dayofyear'],
        'params': {
            'encoder_n_layers': 2,
            'encoder_hidden_size': 64,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1200,
            'batch_size': 32
        }
    },
    {
        'name': '모든 변수 (큰 모델)',
        'features': ['temp', 'rain', 'humidity', 'insolation', 'cloud', 
                    'hour', 'month', 'dayofyear'],
        'params': {
            'encoder_n_layers': 3,
            'encoder_hidden_size': 128,
            'decoder_layers': 2,
            'decoder_hidden_size': 64,
            'max_steps': 1500,
            'batch_size': 64
        }
    }
]

# ========================================
# 4. 실험 실행
# ========================================
results = []
horizon = 24 * 30
input_size = 24 * 30

print("\n" + "="*70)
print("🧪 실험 시작 (총 {}개 모델)".format(len(experiments)))
print("="*70)

for idx, exp in enumerate(experiments, 1):
    print(f"\n[{idx}/{len(experiments)}] {exp['name']}")
    print(f"   특성: {exp['features']}")
    
    # 데이터 준비
    train_nf = prepare_nf_data(train_df, exp['features'])
    val_nf = prepare_nf_data(val_df, exp['features'])
    test_nf = prepare_nf_data(test_df, exp['features'])
    
    full_df = pd.concat([train_nf, val_nf, test_nf], ignore_index=True)
    full_df = full_df.sort_values('ds').reset_index(drop=True)
    
    # 모델 생성
    model_params = exp['params'].copy()
    model = LSTM(
        h=horizon,
        input_size=input_size,
        hist_exog_list=exp['features'],
        encoder_n_layers=model_params['encoder_n_layers'],
        encoder_hidden_size=model_params['encoder_hidden_size'],
        decoder_layers=model_params['decoder_layers'],
        decoder_hidden_size=model_params['decoder_hidden_size'],
        scaler_type='standard',
        max_steps=model_params['max_steps'],
        batch_size=model_params['batch_size'],
        learning_rate=1e-3,
        early_stop_patience_steps=5,
        loss=MAE(),
        random_seed=42,
        alias=f'LSTM_{idx}'
    )
    
    nf = NeuralForecast(models=[model], freq='H')
    
    # 예측
    start_time = time.time()
    try:
        cv_df = nf.cross_validation(
            df=full_df,
            val_size=validation_length,
            n_windows=12,
            step_size=horizon
        )
        
        duration = time.time() - start_time
        
        # 성능 평가
        y_true = cv_df['y'].values
        y_pred = cv_df[f'LSTM_{idx}'].values
        
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        mask = y_true > 0.1
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = np.nan
        
        print(f"   ✅ MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.4f} | 소요: {duration/60:.1f}분")
        
        results.append({
            '순위': idx,
            '모델명': exp['name'],
            '특성개수': len(exp['features']) if exp['features'] else 0,
            '특성목록': ', '.join(exp['features']) if exp['features'] else 'None',
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2,
            'MAPE(%)': mape,
            '소요시간(분)': round(duration/60, 2),
            'Encoder층': model_params['encoder_n_layers'],
            'Hidden크기': model_params['encoder_hidden_size'],
            'Max Steps': model_params['max_steps']
        })
        
    except Exception as e:
        print(f"   ❌ 오류 발생: {str(e)}")
        results.append({
            '순위': idx,
            '모델명': exp['name'],
            '특성개수': len(exp['features']) if exp['features'] else 0,
            '특성목록': ', '.join(exp['features']) if exp['features'] else 'None',
            'MAE': np.nan,
            'RMSE': np.nan,
            'R2': np.nan,
            'MAPE(%)': np.nan,
            '소요시간(분)': 0,
            'Encoder층': model_params['encoder_n_layers'],
            'Hidden크기': model_params['encoder_hidden_size'],
            'Max Steps': model_params['max_steps']
        })

# ========================================
# 5. 결과 분석 및 저장
# ========================================
print("\n" + "="*70)
print("📊 실험 결과 분석")
print("="*70)

if not os.path.exists('../Results'):
    os.makedirs('../Results')

results_df = pd.DataFrame(results)

# MAE 기준 정렬
results_df = results_df.sort_values('MAE').reset_index(drop=True)
results_df['성능순위'] = range(1, len(results_df) + 1)

print("\n🏆 성능 순위 (MAE 기준):")
print(results_df[['성능순위', '모델명', 'MAE', 'RMSE', 'R2', '특성개수']].to_string(index=False))

# 저장
results_df.to_csv('../Results/실험_비교_결과.csv', index=False, encoding='utf-8-sig')
print(f"\n💾 결과 저장: ../Results/실험_비교_결과.csv")

# ========================================
# 6. 시각화
# ========================================
print("\n📊 시각화 생성 중...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 6-1. MAE 비교
valid_results = results_df[results_df['MAE'].notna()]
axes[0, 0].barh(valid_results['모델명'], valid_results['MAE'], color='skyblue', edgecolor='black')
axes[0, 0].set_xlabel('MAE (낮을수록 좋음)')
axes[0, 0].set_title('모델별 MAE 비교', fontweight='bold')
axes[0, 0].invert_yaxis()
axes[0, 0].grid(alpha=0.3, axis='x')

# 6-2. R² 비교
axes[0, 1].barh(valid_results['모델명'], valid_results['R2'], color='lightcoral', edgecolor='black')
axes[0, 1].set_xlabel('R² (높을수록 좋음)')
axes[0, 1].set_title('모델별 R² 비교', fontweight='bold')
axes[0, 1].invert_yaxis()
axes[0, 1].grid(alpha=0.3, axis='x')

# 6-3. 특성 개수 vs MAE
axes[1, 0].scatter(valid_results['특성개수'], valid_results['MAE'], 
                   s=200, c=valid_results['R2'], cmap='RdYlGn', 
                   edgecolor='black', linewidth=2)
for _, row in valid_results.iterrows():
    axes[1, 0].annotate(row['성능순위'], 
                       (row['특성개수'], row['MAE']),
                       ha='center', va='center', fontweight='bold')
axes[1, 0].set_xlabel('특성 개수')
axes[1, 0].set_ylabel('MAE')
axes[1, 0].set_title('특성 개수와 성능의 관계', fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# 6-4. 성능 요약 테이블
axes[1, 1].axis('off')
table_data = []
for _, row in valid_results.head(3).iterrows():
    table_data.append([
        f"{int(row['성능순위'])}위",
        row['모델명'][:20],
        f"{row['MAE']:.2f}",
        f"{row['R2']:.4f}"
    ])

table = axes[1, 1].table(cellText=table_data,
                         colLabels=['순위', '모델명', 'MAE', 'R²'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0.3, 1, 0.6])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# 헤더 스타일
for i in range(4):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 1위 강조
for i in range(4):
    table[(1, i)].set_facecolor('#FFD700')

axes[1, 1].set_title('Top 3 모델', fontweight='bold', fontsize=14, pad=20)

plt.tight_layout()
plt.savefig('../Results/실험_비교_시각화.png', dpi=300)
print("💾 시각화 저장: ../Results/실험_비교_시각화.png")

# ========================================
# 7. 최적 모델 분석
# ========================================
best_model = valid_results.iloc[0]

print("\n" + "="*70)
print("🏆 최적 모델 분석")
print("="*70)
print(f"모델명: {best_model['모델명']}")
print(f"사용 특성: {best_model['특성목록']}")
print(f"특성 개수: {int(best_model['특성개수'])}개")
print(f"MAE: {best_model['MAE']:.3f}")
print(f"RMSE: {best_model['RMSE']:.3f}")
print(f"R²: {best_model['R2']:.4f}")
print(f"MAPE: {best_model['MAPE(%)']:.2f}%")
print(f"네트워크 구조: Encoder {int(best_model['Encoder층'])}층 x {int(best_model['Hidden크기'])} units")
print("="*70)

# 결론 도출
print("\n💡 결론 및 권장사항:")

baseline = results_df[results_df['특성개수'] == 0].iloc[0] if len(results_df[results_df['특성개수'] == 0]) > 0 else None

if baseline is not None and best_model['특성개수'] > 0:
    mae_improvement = ((baseline['MAE'] - best_model['MAE']) / baseline['MAE']) * 100
    r2_improvement = best_model['R2'] - baseline['R2']
    
    if mae_improvement > 0:
        print(f"✅ 외부 변수 추가로 MAE가 {mae_improvement:.1f}% 개선되었습니다.")
        print(f"✅ R²가 {r2_improvement:.4f} 향상되었습니다.")
    else:
        print(f"⚠️ 외부 변수 추가가 오히려 성능을 {-mae_improvement:.1f}% 저하시켰습니다.")
        print(f"   가능한 원인: 과적합, 노이즈, 스케일링 문제")
        
elif best_model['특성개수'] == 0:
    print("⚠️ Baseline 모델(외부변수 없음)이 가장 좋은 성능을 보입니다.")
    print("   외부 변수가 예측에 도움이 되지 않거나 노이즈로 작용할 수 있습니다.")

print("\n📋 권장사항:")
print("   1. 상관관계가 높은 소수의 핵심 변수만 사용")
print("   2. 특성이 많을수록 더 많은 학습 데이터/시간 필요")
print("   3. 변수 간 스케일 차이 고려 (정규화 중요)")
print("   4. Dropout, L2 regularization 등으로 과적합 방지")

print("\n✅ 모든 실험이 완료되었습니다!")