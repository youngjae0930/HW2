from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import io
import os
import logging

from .services.vision import vision_service
from .schemas.response import PredictionResponse
from .core.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="전자기기 및 가구 사물 인식 AI 서비스",
    version="2.0.0",
    debug=settings.DEBUG
)

# 정적 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/health")
async def health_check():
    """서버 상태 확인용 엔드포인트"""
    return {"status": "healthy", "model": settings.MODEL_ID}

@app.post("/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    """이미지를 분석하여 카테고리별 전문 정보 반환"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")

    try:
        logger.info(f"Received file: {file.filename}")
        
        # 이미지 데이터 읽기 및 검증
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="이미지 데이터가 비어 있습니다.")
            
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # 비전 서비스 호출
        result = await vision_service.predict(image)
        
        logger.info(f"Analysis complete for {file.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")

# 전역 예외 처리기 (선택 사항)
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "detail": "예상치 못한 오류가 발생했습니다. 관리자에게 문의하세요.",
        "error": str(exc)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
