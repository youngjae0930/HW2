import torch
from transformers import AutoProcessor, AutoModelForCausalLM, pipeline
import os

def download_models():
    """Dockerfile 빌드 단계에서 모델을 미리 다운로드하여 이미지에 포함시킵니다."""
    
    # 1. Florence-2-base 모델 다운로드
    model_id = "microsoft/Florence-2-base"
    print(f"Downloading {model_id}...")
    AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    
    # 2. NLLB-200 번역 모델 다운로드
    translator_id = "NHNDQ/nllb-finetuned-en2ko"
    print(f"Downloading {translator_id}...")
    pipeline("translation", model=translator_id)

if __name__ == "__main__":
    # Hugging Face 캐시 디렉토리가 Docker 레이어에 저장되도록 설정
    os.makedirs("/app/models", exist_ok=True)
    download_models()
    print("All models downloaded successfully!")
