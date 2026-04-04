# [Phase 1] Python 3.11-slim 기반 경량 베이스 이미지 사용
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HUGGINGFACE_HUB_CACHE=/app/models

# 작업 디렉토리 설정
WORKDIR /app

# [Phase 2] 시스템 의존성 설치 (이미지 폰트 처리 등을 위한 라이브러리)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# [Phase 3] Python 패키지 설치 최적화
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# [Phase 4] AI 모델 프리로드 (Pre-download)
# 빌드 단계에서 모델을 미리 받아 이미지 용량을 키우되, 기동 시간을 대폭 단축
COPY scripts/download_models.py ./scripts/
RUN python scripts/download_models.py

# [Phase 5] 애플리케이션 코드 복사
COPY . .

# 포트 개방 (FastAPI 기본 포트)
EXPOSE 8000

# 서버 실행 (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
