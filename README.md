# Object Detective API (전자기기 사양 식별)

이 프로젝트는 업로드된 이미지에서 전자기기를 식별하고, 해당 기기에 대한 글로벌 전기 사양 정보를 제공하는 FastAPI 기반 AI 서버입니다.

## 주요 기능
- **사물 인식**: Salesforce의 BLIP 모델을 활용하여 이미지 내 캡션 생성 및 전자기기 식별
- **전기 사양 매핑**: 식별된 기기(냉장고, 세탁기, 게임기 등)에 대해 글로벌 전압 및 전력 소비 정보 제공
- **Mops 최적화**: Docker 컨테이너 지원 및 GitHub Actions 기반 CI 연동

## 시작하기

### 로컬 실행
1. 가상환경 생성 및 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
2. 서버 실행
   ```bash
   uvicorn app.main:app --reload
   ```
3. API 문서 확인: `http://localhost:8000/docs` 로 접속하여 이미지 업로드 테스트

### Docker 실행
```bash
docker build -t object-detective .
docker run -p 8000:8000 object-detective
```

## 기술 스택
- **Language**: Python 3.10
- **Framework**: FastAPI
- **ML Model**: Hugging Face Transformers (`blip-image-captioning-base`)
- **DevOps**: Docker, GitHub Actions
