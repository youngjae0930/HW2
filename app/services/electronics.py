from typing import Dict, List, Optional
import re
from ..schemas.response import ElectricalInfo

ELECTRONICS_METADATA: Dict[str, ElectricalInfo] = {
    "refrigerator": ElectricalInfo(
        korean_name="냉장고",
        description_template="음식의 신선도를 유지하는 핵심 가전입니다. 효율적인 냉기 순환을 위해 내부의 70% 정도만 채우고, 뜨거운 음식은 충분히 식혀서 넣어주세요!",
        voltage_range="한국(220V), 미국/일본(110V-120V), 유럽(230V)",
        typical_power="100W - 400W"
    ),
    "washing machine": ElectricalInfo(
        korean_name="세탁기",
        description_template="옷의 오염을 제거하는 필수 가전입니다. 세제를 너무 많이 쓰면 거품만 나고 세탁이 덜 될 수 있어요! 주기적으로 세탁조 통세척을 해주면 냄새 없이 오래 쓸 수 있습니다.",
        voltage_range="한국(220V), 미국/일본(110V-120V), 유럽(230V)",
        typical_power="500W - 2000W"
    ),
    "nintendo switch": ElectricalInfo(
        korean_name="닌텐도 스위치",
        description_template="휴대하거나 TV에 연결해 쓰는 게임기입니다. 조이콘(컨트롤러)은 소모품이라 쏠림 현상이 생길 수 있으니 주의하세요. 충전할 때는 정품 독이나 PD 충전기를 쓰는 게 가장 안전합니다.",
        voltage_range="전 세계 호환 (100V - 240V, 프리볼트)",
        typical_power="10W - 18W"
    ),
    "game controller": ElectricalInfo(
        korean_name="게임 컨트롤러",
        description_template="게임기를 조작하는 컨트롤러입니다. 장시간 사용 시 손목 터널 증후군을 주의하시고, 가끔 마른 천으로 땀과 기름기를 닦아주면 고무 재질이 끈적해지는 것을 막을 수 있습니다.",
        voltage_range="배터리/USB 충전 (5V)",
        typical_power="0.5W - 5W",
        is_variable=True
    ),
    "laptop": ElectricalInfo(
        korean_name="노트북",
        description_template="휴대용 컴퓨터입니다. 배터리를 오래 쓰려면 20~80% 사이로 유지하는 게 좋아요. 열이 잘 빠지도록 이불보다는 책상 위와 같은 평평한 곳에서 사용하세요!",
        voltage_range="어댑터 사용 시 전 세계 호환 (100V - 240V)",
        typical_power="30W - 200W+"
    ),
    "mouse": ElectricalInfo(
        korean_name="컴퓨터 마우스",
        description_template="PC를 조작하는 장치입니다. 무선 마우스는 안 쓸 때 꺼두는 게 배터리 절약에 좋고, 감도가 예민하게 안 움직인다면 바닥면 센서 부위를 가끔 닦아주세요.",
        voltage_range="USB 전원 (5V)",
        typical_power="0.5W 이하"
    ),
    "keyboard": ElectricalInfo(
        korean_name="키보드",
        description_template="입력 장치입니다. 가끔 뒤집어서 털어주는 것만으로도 이물질로 인한 오작동을 예방할 수 있으니 참고하세요.",
        voltage_range="USB 전원 (5V)",
        typical_power="0.5W 이하"
    ),
    "monitor": ElectricalInfo(
        korean_name="모니터",
        description_template="화면을 보는 장치입니다. 눈 건강을 위해 20분마다 먼 곳을 보는 습관을 들이세요! 코팅이 벗겨지지 않게 전용 세정제나 부드러운 천으로 닦는 것이 좋습니다.",
        voltage_range="한국(220V), 미국/일본(110V), 유럽(230V) - 대부분 프리볼트",
        typical_power="20W - 100W"
    ),
    "speaker": ElectricalInfo(
        korean_name="스피커",
        description_template="소리를 들려주는 음향 기기입니다. 너무 크게 틀면 스피커 수명이 줄어들 수 있으니 주의하세요. 제품별 전압 규격이 다를 수 있으니 전원 연결 전 확인이 필수입니다.",
        voltage_range="제품별 상이 (한국-220V / 미국-110V 등 확인 필요)",
        typical_power="5W - 500W+",
        is_variable=True
    ),
    "camera": ElectricalInfo(
        korean_name="카메라",
        description_template="사진과 영상을 찍는 기기입니다. 렌즈 부위는 아주 예민하니 지문이 묻지 않게 주의하시고, 습한 곳을 피해 서늘하고 건조한 곳에 보관하는 것이 좋습니다.",
        voltage_range="배터리/USB 충전 (제품별 상이)",
        typical_power="5W - 20W",
        is_variable=True
    ),
    "printer": ElectricalInfo(
        korean_name="프린터",
        description_template="인쇄 기기입니다. 잉크젯 프린터는 너무 안 쓰면 노즐이 굳을 수 있으니 일주일에 한 번은 꼭 테스트 인쇄를 해보시는 게 좋습니다.",
        voltage_range="한국(220V), 미국/일본(110V-120V) 등",
        typical_power="10W - 500W+"
    ),
    "projector": ElectricalInfo(
        korean_name="프로젝터",
        description_template="영상을 투사하는 장치입니다. 내부 램프가 뜨거워지니 사용 직후 바로 전선을 뽑지 마세요! 팬이 돌며 열을 충분히 식혀야 수명이 오래갑니다.",
        voltage_range="한국(220V), 미국/일본(110V-120V) 등",
        typical_power="150W - 500W"
    ),
    "air purifier": ElectricalInfo(
        korean_name="공기청정기",
        description_template="공기를 걸러주는 가전입니다. 필터 청소나 교체 시기를 놓치면 성능이 떨어집니다. 필터 겉면의 큰 먼지는 가끔 진공청소기로 제거해주면 필터 수명을 늘릴 수 있습니다.",
        voltage_range="한국(220V), 미국/일본(110V-120V) 등",
        typical_power="30W - 100W"
    ),
    "vacuum cleaner": ElectricalInfo(
        korean_name="진공청소기",
        description_template="먼지를 빨아들이는 가전입니다. 먼지통을 자주 비워야 흡입력이 유지됩니다. 브러시에 낀 머리카락 등을 제거하면 소음이 줄고 성능이 좋아집니다.",
        voltage_range="한국(220V), 미국/일본(110V) 등",
        typical_power="500W - 1500W"
    ),
    "microwave": ElectricalInfo(
        korean_name="전자레인지",
        description_template="음식을 데우는 가전입니다. 알루미늄 호일이나 금속 그릇은 절대 넣지 마세요! 유리나 도자기 재질의 전용 용기만 사용하는 것이 안전합니다.",
        voltage_range="한국(220V), 미국/일본(110V), 유럽(230V)",
        typical_power="700W - 1500W"
    ),
    "humidifier": ElectricalInfo(
        korean_name="가습기",
        description_template="습도를 조절하는 기기입니다. 세균 번식을 막기 위해 물통의 물은 매일 갈아주고 세척도 자주 해주세요. 수돗물이 정수물보다 세균 억제에 더 좋다고 알려져 있습니다.",
        voltage_range="USB 전원(5V) 또는 한국(220V) 등",
        typical_power="10W - 50W",
        is_variable=True
    ),
    "television": ElectricalInfo(
        korean_name="텔레비전",
        description_template="영상을 재생하는 가전입니다. 화면 패널은 충격에 약하니 주의하세요! 멀리서 시청하는 게 눈 건강에 좋으며, 에너지 절약 모드를 활용해 전력을 아낄 수 있습니다.",
        voltage_range="한국(220V), 미국/일본(110V), 유럽(230V) - 대부분 프리볼트",
        typical_power="50W - 300W"
    ),
    "air conditioner": ElectricalInfo(
        korean_name="에어컨",
        description_template="온도를 조절하는 냉방 가전입니다. 주기적인 필터 청소는 냉방 효율을 높이고 전기료를 아껴줍니다. 실외기 근처에 물건을 두지 않아야 원활한 열 배출이 가능합니다.",
        voltage_range="한국(220V), 미국(240V 전용 콘센트) 등",
        typical_power="800W - 2500W+"
    ),
    "hair dryer": ElectricalInfo(
        korean_name="드라이기",
        description_template="머리를 말리는 도구입니다. 뒷부분 먼지망에 먼지가 차지 않게 칫솔로 가끔 털어내 주시는 게 안전하고 풍량도 좋아지는 비결입니다.",
        voltage_range="한국(220V), 미국(110V) - 전용 전압 확인 필수",
        typical_power="1200W - 2000W"
    ),
    "router": ElectricalInfo(
        korean_name="인터넷 공유기",
        description_template="와이파이를 송출하는 기기입니다. 탁 트인 높은 곳에 두는 게 전파가 더 잘 퍼집니다. 인터넷이 느려지면 재부팅만으로도 속도가 개선되는 경우가 많습니다.",
        voltage_range="전용 어댑터 방식 (보통 프리볼트)",
        typical_power="5W - 20W"
    ),
    "electric kettle": ElectricalInfo(
        korean_name="전기포트",
        description_template="물을 끓이는 주전자입니다. 바닥의 흰색 가루는 구연산을 넣고 끓여 제거할 수 있어요! 전력이 많이 소비되므로 벽면 콘센트에 바로 꽂아 쓰시길 권장합니다.",
        voltage_range="한국(220V), 미국(110V) 등",
        typical_power="1000W - 2400W"
    ),
    "guitar": ElectricalInfo(
        korean_name="기타",
        description_template="줄의 진동으로 소리 내는 악기입니다. 습도에 예민하니 하드케이스에 보관하거나 적정 습도를 유지하는 게 좋습니다. 일렉 기타의 경우 앰프 연결 전 전압을 꼭 확인하세요.",
        voltage_range="앰프 연결 시 전압 확인 (보통 한국 220V)",
        typical_power="데이터 없음 (앰프 사용 시 10W - 100W+)",
        is_variable=True
    )
}

SYNONYMS_MAPPING = {
    "fridge": "refrigerator", "cooler": "refrigerator", "dryer": "hair dryer",
    "switch": "nintendo switch", "console": "game console", "controller": "game controller",
    "gamepad": "game controller", "joypad": "game controller", "charger": "phone charger",
    "adapter": "phone charger", "pc": "laptop", "notebook": "laptop",
    "tv": "television", "screen": "monitor", "vaccum": "vacuum cleaner",
    "cleaner": "vacuum cleaner", "guitar": "guitar", "electric guitar": "guitar"
}

def get_electrical_info(object_name: str) -> Optional[ElectricalInfo]:
    """제품명이나 캡션을 기반으로 전기 사양 조회"""
    name_lower = object_name.lower()
    
    # 1. 메타데이터와 직접 매칭
    for key, info in ELECTRONICS_METADATA.items():
        if key in name_lower:
            return info
            
    # 2. 동의어 매칭
    for syn, official in SYNONYMS_MAPPING.items():
        if syn in name_lower:
            return ELECTRONICS_METADATA.get(official)
            
    return None
