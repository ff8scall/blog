import json
import os
import re
from ai_writer import AIWriter

# [V2.7.1] 가이드 전용 JSON 스키마
GUIDE_JSON_SCHEMA = """
{
    "guide_title": "Tutorial Title",
    "guide_summary": "1-sentence gist",
    "guide_type": "ai-usage | performance-tuning | troubleshooting | recommendations",
    "difficulty": "Beginner | Intermediate | Advanced",
    "guide_content": "Full markdown with markers: 🏁 Starts, 🛠️ Prerequisites, 📝 Step-by-Step, 💡 Pro-Tips, ⚠️ Troubleshooting",
    "tags": ["tag1", "tag2"]
}
"""

class GuideEditor:
    """[V2.7.1] 무결점 가이드 에디터: SEO 상속 및 변수 치환 정상화"""
    def __init__(self, model_name="gemini-2.0-flash", writer=None):
        self.model_name = model_name
        self.writer = writer if writer else AIWriter()

    def _extract_json(self, res):
        """[V2.7.1 Safe Parser]"""
        try:
            if not res or len(res) > 30000: return None
            res = re.sub(r'```json\s*|\s*```', '', res)
            start = res.find('{')
            end = res.rfind('}')
            if start == -1 or end == -1: return None
            return json.loads(res[start:end+1], strict=False)
        except Exception as e:
            print(f" [!] Guide Parsing Error: {e}")
            return None

    def write_guide(self, news_draft):
        """[V2.7.1] 변수 치환 버그 수정 및 가이드 필력 강화"""
        # 요약 정규화
        summary = news_draft.get('kor_summary', '')
        if isinstance(summary, list):
            summary = " ".join(summary)
            
        base_slug = news_draft.get('sync_slug', 'strategic-guide')
        
        # [V2.7.1] f-string 중괄호 오류 수정: { } 로 변수 치환
        prompt = f"""
        [PERSONA]: Senior Tech Instructor & Architect.
        [TASK]: Based on the following context, write a deep-dive 'Strategic Guide'.
        
        [INPUT CONTEXT]:
        - Source Title: {news_draft.get('kor_title')}
        - Key Summary: {summary}
        - SEO Slug: {base_slug}
        - Detailed Info: {news_draft.get('kor_content', '')[:2500]}

        [OUTPUT STRUCTURE - STRICT JSON]:
        {GUIDE_JSON_SCHEMA}
        
        [WRITING RULE]: Ensure 'guide_content' uses rich markdown and all 5 markers (🏁, 🛠️, 📝, 💡, ⚠️).
        """
        
        res = self.writer.generate_content(prompt, model=self.model_name)
        result = self._extract_json(res)
        
        # [V2.7.1 Validation] 섹션 검증 및 자동 보정 시도
        if result and 'guide_content' in result:
            content = result['guide_content']
            required = ['🏁', '🛠️', '📝', '💡', '⚠️']
            missing = [m for m in required if m not in content]
            if missing:
                print(f" [!] Guide missing sections: {missing}. Notifying system.")
        
        return result
