import json
import os
import re
import logging
from ai_writer import AIWriter

logger = logging.getLogger("LegoSia.GuideEditor")

GUIDE_JSON_SCHEMA = """
{
    "guide_title": "Practical Guide Title",
    "guide_summary": "1-sentence summary",
    "guide_type": "...",
    "difficulty": "Beginner | Intermediate | Advanced",
    "guide_content": "Detailed Markdown content with markers (🏁, 🛠️, 📝, 💡, ⚠️)",
    "tags": ["tag1", "tag2"]
}
"""

class GuideEditor:
    """[V3.0] 글로벌 가이드 에디터: 다국어 집필 및 안정적 파싱"""
    def __init__(self, model_name=None, writer=None):
        self.model_name = model_name
        self.writer = writer if writer else AIWriter()

    def _extract_json_safe(self, text):
        if not text: return None
        stack = []
        start = -1
        for i, char in enumerate(text):
            if char == '{':
                if start == -1: start = i
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        try: return json.loads(text[start:i+1], strict=False)
                        except: return None
        return None

    def write_guide(self, news_draft, lang='ko'):
        """[V3.0] 언어별 가이드 집필 지원"""
        summary = news_draft.get('kor_summary', '')
        if isinstance(summary, list): summary = " ".join(summary)
            
        base_slug = news_draft.get('sync_slug', 'strategic-guide')
        language_name = "Korean" if lang == 'ko' else "English"
        
        prompt = f"""
        [TASK]: Write a technical 'Strategic Guide' in {language_name}.
        [PERSONA]: Tech Instructor.
        
        [INPUT CONTEXT]:
        - TOPIC: {news_draft.get('kor_title')}
        - SUMMARY: {summary}
        - SLUG: {base_slug}
        - DETAIL: {news_draft.get('kor_content', '')[:2000]}

        [OUTPUT STRUCTURE]:
        {GUIDE_JSON_SCHEMA}
        
        [RULE]: Content MUST be written in {language_name}. Use rich markdown (🏁, 🛠️, 📝, 💡, ⚠️).
        """
        
        res = self.writer.generate_content(prompt, model=self.model_name)
        result = self._extract_json_safe(res)
        
        if result and 'guide_content' in result:
            required = ['🏁', '🛠️', '📝', '💡', '⚠️']
            if not all(m in result['guide_content'] for m in required):
                logger.warning(f"Guide missing sections in {lang}")
        
        return result
