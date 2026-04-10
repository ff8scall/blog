import json
from ai_writer import AIWriter

class NewsEditor:
    def __init__(self):
        self.writer = AIWriter()

    def review_batch(self, articles):
        """여러 기사를 한꺼번에 분석하여 점수와 요약을 반환 (Batch Processing)"""
        # 기사 목록을 텍스트로 변환
        news_list_str = ""
        for i, article in enumerate(articles):
            news_list_str += f"[{i}] {article['title']} (출처: {article['source']})\n"

        prompt = f"""
        당신은 IT/테크 전문 매거진의 편집장입니다. 다음 뉴스 목록을 분석하여 형식에 맞춰 응답하세요.
        현재 시점은 **2026년 4월**입니다.

        [뉴스 목록]
        {news_list_str}
        
        [지시사항]
        1. 각 기사별로 가치 평가(score)를 0~10점으로 매기세요.
           - 2026년 기준 최첨단 트렌드(Rubin, HBM4, GPT-6 등)는 높은 점수.
           - Blackwell, GPT-4 등 1~2년 전 구형 기술을 '신규'인 것처럼 소개하면 0점.
        2. 점수가 7점 이상인 기사에 대해서만 3줄 요약(summary)을 작성하세요.
        3. 응답은 반드시 아래 JSON 리스트 형식으로만 하세요. 다른 말은 절대 덧붙이지 마세요.
        
        [
            {{
                "index": 0,
                "score": 9,
                "summary": "1. 요약...\\n2. 요약...\\n3. 요약...",
                "title": "기사 제목 재확인"
            }},
            ...
        ]
        """
        
        try:
            print(f"[*] AI Batch Reviewing {len(articles)} articles...")
            response_text = self.writer.generate_content(prompt, category="AI·신기술", model="models/gemini-3.1-flash-lite-preview")
            # JSON만 추출
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            results = json.loads(clean_json)
            return results # 리스트 반환
        except Exception as e:
            print(f"[ERROR] AI Batch Review failed: {e}")
            return []
