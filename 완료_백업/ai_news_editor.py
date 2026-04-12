import json
import os
import re
from ai_writer import AIWriter

# [V2.7.1] JSON 스키마 상수화로 프롬프트 안정성 확보
NEWS_JSON_SCHEMA = """
{
    "score": 1~10,
    "cluster": "Intelligence | CoreTech | Strategy | Digital",
    "category": "llm-ai-models | ai-agents | ai-policy | ai-tools | gpu-semiconductor | pc-server-infra | robotics | ai-business | startups | tech-industry | game-tech | xr-ar-vr",
    "eng_title": "Professional English title",
    "eng_summary": "1-sentence concise English description for SEO",
    "kor_title": "국문 헤드라인",
    "kor_summary": ["3문항 핵심 요약 (리스트형)"],
    "kor_content": "수석 에디터 심층 분석 본문",
    "kor_insight": "전략적 시사점 (What This Means)",
    "keywords": ["tag1", "tag2", "tag3"]
}
"""

class NewsEditor:
    """[V2.7.1] 최적화 에디터: 중복 방지(Context Awareness) 및 안정성 강화"""
    def __init__(self, model_name="gemini-2.0-flash", writer=None):
        self.model_name = model_name
        self.writer = writer if writer else AIWriter()

    def _extract_json(self, res):
        """[V2.7.1 Safe Parser] JSON 클린업 및 가비지 데이터 방어"""
        try:
            if not res or len(res) > 25000: return None
            # 마크다운 코드블록 및 불필요 텍스트 제거
            res = re.sub(r'```json\s*|\s*```', '', res)
            start = res.find('{')
            end = res.rfind('}')
            if start == -1 or end == -1: return None
            return json.loads(res[start:end+1], strict=False)
        except Exception as e:
            print(f" [!] JSON Parsing Error: {e}")
            return None

    def _get_full_event_analysis(self, articles):
        """[Stage 1] 토큰 가드: 기사당 800자 제한 종합 리포트 생성"""
        truncated = []
        for a in articles:
            content = a.get('description', a.get('content', ''))[:800]
            truncated.append(f"Source: {a.get('source_name', 'Tech Outlet')}\nTitle: {a['title']}\nContent: {content}")
        
        combined_text = "\n---\n".join(truncated)
        prompt = f"""
        [TASK]: As a Senior Strategic Analyst, create a comprehensive English Tech Report by synthesizing multiple sources.
        [SOURCES]:
        {combined_text}
        """
        return self.writer.generate_content(prompt, model=self.model_name)

    def review_batch(self, articles, recent_posts=None):
        """[V2.7.1] 무결점 에디팅: 중복 제목 방지 컨텍스트 반영"""
        try:
            event_report_en = self._get_full_event_analysis(articles)
            if not event_report_en or len(event_report_en) < 300: return []

            # [V2.7.1] 최근 포스팅 제목 주입 (중복 방지)
            history_context = ""
            if recent_posts:
                titles = [p.get('title', '') for p in recent_posts]
                history_context = f"[RECENT TITLES (DO NOT REPEAT)]: {', '.join(titles)}"

            localize_prompt = f"""
            [PERSONA]: Senior Tech Editor (15y exp). Sharp, strategic, expert tone.
            [TASK]: Reconstruct the English report into a premium Korean tech briefing.
            [HISTORY]: {history_context}
            
            [OUTPUT STRUCTURE - STRICT JSON]:
            {NEWS_JSON_SCHEMA}
            
            [CONTEXT TO ANALYZE]:
            {event_report_en}
            """
            
            res = self.writer.generate_content(localize_prompt, model=self.model_name)
            draft = self._extract_json(res)
            
            if draft:
                # [V2.7.1] Stage 1 영문 리포트 주입 (비용 절감)
                draft['eng_content'] = event_report_en
                
                cluster_map = {
                    "llm-ai-models": "Intelligence", "ai-agents": "Intelligence", "ai-policy": "Intelligence", "ai-tools": "Intelligence",
                    "gpu-semiconductor": "CoreTech", "pc-server-infra": "CoreTech", "robotics": "CoreTech",
                    "ai-business": "Strategy", "startups": "Strategy", "tech-industry": "Strategy",
                    "game-tech": "Digital", "xr-ar-vr": "Digital"
                }
                cat = draft.get('category', 'ai-tools')
                draft['category'] = cat
                draft['cluster'] = cluster_map.get(cat, "Intelligence")
                draft['original_url'] = articles[0]['url']
                draft['source_name'] = articles[0].get('source_name', 'Global Sources')
                return [draft]
                
        except Exception as e:
            print(f" [!] NewsEditor V2.7.1 Failure: {e}")
            
        return []
