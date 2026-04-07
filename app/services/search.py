import re
from typing import Optional, Dict
from duckduckgo_search import DDGS
from ..schemas.response import ElectricalInfo

class SearchService:
    def __init__(self):
        self.ddgs = DDGS()

    def get_info(self, object_name: str) -> Optional[ElectricalInfo]:
        """실시간 웹 검색을 통해 사물의 전기 사양을 추출합니다."""
        search_query = f"{object_name} typical voltage and power consumption specifications"
        print(f"Searching for: {search_query}")
        
        try:
            # 1. 웹 검색 수행 (최신 정보 3개 추출)
            results = self.ddgs.text(search_query, max_results=3)
            if not results:
                return None
                
            combined_text = " ".join([r['body'] for r in results])
            
            # 2. 전압(Voltage) 추출 로직 (정규식)
            # 패턴 예: 220V, 110-240V, 5V, 12.5V 등
            voltage_pattern = r'(\d+(?:-\d+)?\s*[vV](?:olt[s]?)?)'
            voltages = re.findall(voltage_pattern, combined_text)
            voltage_str = voltages[0] if voltages else "확인 필요(제품 라벨 참조)"
            
            # 3. 전력(Power) 추출 로직 (정규식)
            # 패턴 예: 100W, 1000 watts, 1.5kW 등
            power_pattern = r'(\d+(?:\.\d+)?\s*[wW](?:att[s]?)?)'
            powers = re.findall(power_pattern, combined_text)
            power_str = powers[0] if powers else "분석 중..."
            
            # 4. 정보 구성
            return ElectricalInfo(
                korean_name=object_name,
                description_template=f"실시간 검색 결과: {results[0]['body'][:150]}...",
                voltage_range=voltage_str,
                typical_power=power_str,
                is_variable=True
            )
        except Exception as e:
            print(f"실시간 검색 중 오류 발생: {e}")
            return None

search_service = SearchService()
