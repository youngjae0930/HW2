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
from .furniture import get_furniture_info
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

    async def predict(self, image: Image.Image, mode: str = "auto") -> PredictionResponse:
        """사물 분석 및 전자기기/가구 정보 제공 (모드 분기 지원)"""
        
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

        # 2. 비사물 필터링 (자동 모드일 때만 강력하게 적용)
        if mode == "auto" and self._is_non_object_image(raw_caption):
            return PredictionResponse(
                results=[DetectionResult(
                    object_name="사물 사진 필요",
                    description="업로드한 이미지가 실제 사물이 아닌 화면이나 UI로 보입니다. 실제 사물의 사진을 업로드해 주세요.",
                    is_ai_generated=True
                )],
                ai_model_info=settings.MODEL_ID
            )

        # 3. 분석 수행 (전자 vs 가구 vs 일반)
        noun_en = self._extract_core_noun(raw_caption)
        
        elec_info = None
        is_electronic = False
        is_ai_elec = False
        
        furn_info = None
        is_furniture = False

        # [Category 1] 전자기기 분석 (전자기기 모드이거나 자동 모드일 때만)
        if mode in ["auto", "electronics"]:
            elec_info, is_electronic, is_ai_elec = await get_electrical_info(noun_en)
            if not elec_info and is_electronic:
                 elec_info, is_electronic, is_ai_elec = await get_electrical_info(raw_caption)
        
        # [Category 2] 가구 분석 (가구 모드이거나 자동 모드일 때만)
        if mode in ["auto", "furniture"]:
            furn_info, is_furniture = get_furniture_info(noun_en)
            if not furn_info and is_furniture:
                furn_info, is_furniture = get_furniture_info(raw_caption)
        
        # 모드 강제 적용 (전자기기 모드인데 인식이 안 된 경우 AI fallback)
        if mode == "electronics":
            is_electronic = True
            is_furniture = False
            furn_info = None
        elif mode == "furniture":
            is_furniture = True
            is_electronic = False
            elec_info = None

        # 제목 결정
        title_ko = ""
        if elec_info and self._contains_korean(elec_info.korean_name):
            title_ko = elec_info.korean_name
        elif furn_info and self._contains_korean(furn_info.korean_name):
            title_ko = furn_info.korean_name
        else:
            title_ko = self._translate_description(noun_en)
            
        title_ko = self._sanitize_title(title_ko)

        # 설명 생성
        rich_description = ""
        if is_electronic and elec_info:
            if is_ai_elec: # 데이터에 없는 사물인 경우 AI 분석 캡션을 설명으로 활용
                translated_caption = self._translate_description(raw_caption)
                rich_description = f"{translated_caption} (AI 분석 정보)"
            else:
                rich_description = elec_info.description_template
        elif is_electronic: # 모드 강제 적용에 의한 fallback
            translated_caption = self._translate_description(raw_caption)
            rich_description = f"{translated_caption} (AI 분석 정보)"
        elif is_furniture:
            if furn_info:
                rich_description = furn_info.description_template
            else:
                translated_caption = self._translate_description(raw_caption)
                rich_description = f"{translated_caption} (가구 모드 AI 분석 정보)"
        else:
            translated_caption = self._translate_description(raw_caption)
            rich_description = f"{translated_caption} (일반 사물 분석 정보)"

        # 결과 구성
        result = DetectionResult(
            object_name=title_ko,
            description=rich_description,
            is_electronic=is_electronic,
            is_furniture=is_furniture,
            is_ai_generated=is_ai_elec or (is_furniture and not furn_info) or (mode != "auto"),
            electrical_info=elec_info,
            furniture_info=furn_info
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
        """위치 어구, 동사구 및 묘사를 정밀 제거하여 핵심 명사만 추출"""
        cleaned = text.lower()
        patterns = [
            r"^(a |an |the )?(photo|image|view|picture) (of|shows|showing) ",
            r"^(there is|there are) ",
            r"^a close up of ",
            r"^a "
        ]
        for p in patterns:
            cleaned = re.sub(p, "", cleaned)

        # 동사구 및 위치 전치사구 대거 추가 (동적으로 명사만 추출)
        pos_patterns = [
            r" (on|in|with|at|near|above|below|behind|beside|next to|sitting on|placed on|hanging on|of a|captured) .*",
            r" (flying|playing|standing|holding|looking|using|walking|watching|carried by|surrounded by) .*",
            r" that is .*",
            r" for .*"
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

    def _contains_korean(self, text: str) -> bool:
        """한글 포함 여부 확인"""
        return bool(re.search("[가-힣]", text))

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
