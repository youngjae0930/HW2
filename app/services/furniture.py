from typing import Dict, Optional
from ..schemas.response import FurnitureInfo

FURNITURE_METADATA: Dict[str, FurnitureInfo] = {
    "sofa": FurnitureInfo(
        korean_name="소파",
        description_template="휴식을 취할 수 있는 편안한 가구입니다. 주기적으로 쿠션을 두드려 모양을 잡아주면 수명을 늘릴 수 있습니다.",
        material="패브릭/가죽/벨벳",
        care_tip="직사광선을 피하고 가죽 전용 클리너나 마른 천으로 닦아주세요."
    ),
    "chair": FurnitureInfo(
        korean_name="의자",
        description_template="앉아서 작업을 하거나 쉴 때 필요한 의자입니다. 다리 연결 부위의 나사가 헐거워지지 않았는지 가끔 확인해 보세요.",
        material="원목/금속/플라스틱",
        care_tip="바닥 긁힘 방지 패드를 부착하면 소음과 흠집을 예방할 수 있습니다."
    ),
    "table": FurnitureInfo(
        korean_name="테이블/책상",
        description_template="활동의 중심이 되는 평평한 가구입니다. 뜨거운 물건은 받침대 없이 올리지 않도록 주의하세요.",
        material="원목/유리/대리석",
        care_tip="음식물 흘렸을 때 즉시 닦아내야 얼룩이 생기지 않습니다."
    ),
    "bed": FurnitureInfo(
        korean_name="침대",
        description_template="수면을 위한 핵심 가구입니다. 매트리스는 3~6개월마다 상하좌우를 뒤집어주면 꺼짐 현상을 방지할 수 있습니다.",
        material="목재/프레임/메모리폼",
        care_tip="침구류를 자주 세탁하고 한 달에 한 번 먼지를 털어주세요."
    ),
    "wardrobe": FurnitureInfo(
        korean_name="옷장",
        description_template="의류를 보관하는 수납장입니다. 내부에 제습제를 넣어 습기를 조절하는 것이 옷의 변색을 막는 데 중요합니다.",
        material="원목/MDF",
        care_tip="너무 많은 옷을 한꺼번에 걸면 봉이 휠 수 있으니 적절히 분산하세요."
    ),
    "bookshelf": FurnitureInfo(
        korean_name="책장",
        description_template="책이나 장식품을 두는 선반입니다. 무거운 책은 아래쪽 선반에 두어야 안정적입니다.",
        material="원목/철제",
        care_tip="먼지가 쌓이기 쉬우므로 정전기 포로 가끔 닦아주세요."
    )
}

FURNITURE_SYNONYMS = {
    "couch": "sofa", "bench": "chair", "desk": "table", "dining table": "table",
    "cabinet": "wardrobe", "closet": "wardrobe", "shelf": "bookshelf"
}

def get_furniture_info(object_name: str) -> (Optional[FurnitureInfo], bool):
    """가구 제품명을 기반으로 정보 및 가구 여부 반환"""
    name_lower = object_name.lower()
    
    # 1. 메타데이터 직접 매칭
    for key, info in FURNITURE_METADATA.items():
        if key in name_lower:
            return info, True
            
    # 2. 동의어 매칭
    for syn, official in FURNITURE_SYNONYMS.items():
        if syn in name_lower:
            return FURNITURE_METADATA.get(official), True
            
    # 3. 키워드 기반 판별 (정보는 없지만 가구인 경우)
    furniture_keywords = ["furniture", "drawer", "stool", "stand", "rack"]
    if any(kw in name_lower for kw in furniture_keywords):
        return None, True
        
    return None, False
