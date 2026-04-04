from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import io
import os
from .services.vision import vision_service
from .schemas.response import PredictionResponse
from .core.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# 정적 파일 경로 설정
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/style.css")
async def get_css():
    return FileResponse(os.path.join(static_path, "style.css"))

@app.get("/script.js")
async def get_js():
    return FileResponse(os.path.join(static_path, "script.js"))

@app.post("/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")

    try:
        # 이미지 데이터 읽기 및 PIL 객체로 변환
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # 모델 추론 수행
        result = await vision_service.predict(image)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 처리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
