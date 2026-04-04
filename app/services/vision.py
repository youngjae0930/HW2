import sys
import re
import os
from unittest.mock import patch
from PIL import Image
import torch

# 1. Windows/CPU 환경에서의 flash_attn 종속성 체크 우회 패치
from transformers.dynamic_module_utils import get_imports

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    """임포트 목록에서 flash_attn을 강제로 제거하여 에러 방지"""
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

from transformers import AutoProcessor, AutoModelForCausalLM, pipeline
from ..core.config import settings
from .electronics import get_electrical_info
from ..schemas.response import DetectionResult, PredictionResponse

class VisionService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # [Phase 1] 사물 인식 모델 로드 (Florence-2)
        print(f"Loading recognition model: {settings.MODEL_ID}...")
        self.processor = AutoProcessor.from_pretrained(settings.MODEL_ID, trust_remote_code=True)
        
        # 패치를 적용하여 모델 로드
        with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_ID, 
                trust_remote_code=True, 
                torch_dtype=self.torch_dtype,
                attn_implementation="eager"
            ).to(self.device).eval()
        
        # [Phase 2] 차세대 번역 모델 로드 (NLLB-200)
        print("Loading advanced translation model (NLLB-200)...")
        try:
            self.translator = pipeline(
                "translation", 
                model="NHNDQ/nllb-finetuned-en2ko", 
                device=0 if torch.cuda.is_available() else -1,
                src_lang="eng_Latn",
                tgt_lang="kor_Hang"
            )
            self.use_ai_translator = True
        except Exception as e:
            print(f"AI 번역 모델 로드 실패: {e}. 사전 기반 번역으로 전환합니다.")
            self.use_ai_translator = False

    async def predict(self, image: Image.Image) -> PredictionResponse:
        """사물만 딱 추출하여 명사형 제목 제공 (비사물 필터링 포함)"""
        
        # 1. 캡셔닝 수행
        prompt = "<CAPTION>"
        inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)

        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=64,
            num_beams=1,
            repetition_penalty=1.2,
            do_sample=False
        )
        
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        raw_caption = parsed_answer["<CAPTION>"]

        # 2. 비사물(스크린샷, UI 등) 판별
        if self._is_non_object_image(raw_caption):
            return PredictionResponse(
                results=[DetectionResult(
                    object_name="사물 사진 필요",
                    description="업로드한 이미지가 실제 사물이 아닌 스크린샷이나 디지털 화면으로 보입니다. 분석을 위해 인공지능이 인식할 수 있는 실제 사물의 사진을 업로드해 주세요.",
                    electrical_info=None
                )],
                ai_model_info=settings.MODEL_ID
            )

        # 3. 핵심 명사 추출
        noun_en = self._extract_core_noun(raw_caption)
        
        # 전기 사양 정보 조회
        elec_info = get_electrical_info(noun_en)
        if not elec_info:
             elec_info = get_electrical_info(raw_caption)

        # 제목 결정 (명사형)
        object_name_ko = elec_info.korean_name if elec_info else self._translate_description(noun_en)
        object_name_ko = self._sanitize_title(object_name_ko)

        # 보편적 설명 생성
        rich_description = self._build_rich_description(noun_en, elec_info)

        # 결과 구성
        result = DetectionResult(
            object_name=object_name_ko,
            description=rich_description,
            electrical_info=elec_info
        )

        return PredictionResponse(
            results=[result],
            ai_model_info=settings.MODEL_ID
        )

    def _is_non_object_image(self, caption: str) -> bool:
        """스크린샷, UI, 차트 등 실제 물리적 사물이 아닌 이미지를 감별 (사물 오인식 방지)"""
        non_obj_keywords = [
            "screenshot", "screen shot", "digital", "ui", "interface", "website", 
            "graphics", "chess", "gameplay", "text on", "diagram",
            "web page", "application", "software"
        ]
        
        # 실제 물리적 사물 키워드가 포함되어 있다면 일단 허용
        physical_obj_keywords = [
            "refrigerator", "washing machine", "laptop", "monitor", "camera", "phone",
            "guitar", "instrument", "controller", "speaker", "gamepad", "joypad", "vacuum"
        ]
        
        caption_lower = caption.lower()
        
        # 비사물 키워드가 있고, 물리적 사물 키워드가 확실히 부재할 때만 필터링
        if any(kw in caption_lower for kw in non_obj_keywords):
            if not any(pk in caption_lower for pk in physical_obj_keywords):
                return True
            
        return False

    def _extract_core_noun(self, text: str) -> str:
        """위치 어구 및 묘사를 정밀 제거하여 핵심 명사만 추출"""
        cleaned = text.lower()
        patterns = [
            r"^(a |an |the )?(photo|image|view|picture) (of|shows|showing) ",
            r"^(there is|there are) ",
            r"^a close up of ",
            r"^a "
        ]
        for p in patterns:
            cleaned = re.sub(p, "", cleaned)

        pos_patterns = [
            r" (on|in|with|near|sitting on|placed on|hanging on|of a) .*",
            r" that is .*"
        ]
        for p in pos_patterns:
            cleaned = re.sub(p, "", cleaned)

        cleaned = cleaned.split(",")[0].split(".")[0].strip()
        return cleaned.capitalize()

    def _sanitize_title(self, text: str) -> str:
        """제목에서 서술어 및 위치 관형사구 제거"""
        text = text.replace(".", "").strip()
        text = re.sub(r"(입니다|보입니다|보여줍니다|나타냅니다|라고 합니다|있는 상태입니다)$", "", text)
        text = re.sub(r"^(책단 위에|책상 위에|벽에|바닥에|테이블 위에|선반 위에) (앉은|걸린|놓인|있는) ", "", text)
        return text.strip()

    def _build_rich_description(self, noun_en: str, elec_info: any) -> str:
        """사물 자체에 대한 정보만 제공"""
        if elec_info:
            return f"{elec_info.description_template}"
        
        translated_noun = self._translate_description(noun_en)
        translated_noun = self._sanitize_title(translated_noun)
        return f"인식된 사물은 '{translated_noun}'입니다. 해당 사물에 대한 구체적인 전기 사양 데이터가 보완 중입니다."

    def _translate_description(self, text: str) -> str:
        """NLLB-200을 사용하여 고품질 번역"""
        if self.use_ai_translator:
            try:
                result = self.translator(text)
                return result[0]['translation_text'].strip()
            except Exception:
                pass 
        return text

vision_service = VisionService()
