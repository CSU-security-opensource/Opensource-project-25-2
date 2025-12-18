from chronos import BaseChronosPipeline
import torch
import os

# 1. 모델 다운로드
print("⬇️ 모델 다운로드 중...")
pipeline = BaseChronosPipeline.from_pretrained(
    "amazon/chronos-bolt-base",
    device_map="cpu",
    dtype=torch.float32  # torch_dtype 대신 dtype 사용
)

# 2. 저장 디렉토리 생성
save_directory = "./my_saved_model"
os.makedirs(save_directory, exist_ok=True)

# 3. 모델의 state_dict를 .pt 파일로 저장
model_path = os.path.join(save_directory, "chronos_model.pt")
torch.save(pipeline.model.state_dict(), model_path)
print(f"✅ 모델이 '{model_path}'에 저장되었습니다!")

# 4. 전체 파이프라인 객체도 저장 (선택사항)
pipeline_path = os.path.join(save_directory, "chronos_pipeline.pt")
torch.save(pipeline, pipeline_path)
print(f"✅ 전체 파이프라인이 '{pipeline_path}'에 저장되었습니다!")

# 5. 추가 정보 저장 (config 등)
if hasattr(pipeline, 'model') and hasattr(pipeline.model, 'config'):
    config_path = os.path.join(save_directory, "config.pt")
    torch.save(pipeline.model.config, config_path)
    print(f"✅ 설정이 '{config_path}'에 저장되었습니다!")

print("\n📁 저장된 파일들:")
for file in os.listdir(save_directory):
    file_path = os.path.join(save_directory, file)
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"  - {file} ({size_mb:.2f} MB)")

print("\n✨ 이제 인터넷 없이도 이 폴더의 .pt 파일들을 사용할 수 있습니다!")