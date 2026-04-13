import json
import os
import re
import time
import logging
from datetime import datetime
from ai_writer import AIWriter

# [V3.0] 로깅 설정
logger = logging.getLogger("LegoSia.NewsEditor")

# [V7.5] 용어 사전 (Glossary) - 오역 방지 및 전문성 강화
GLOSSARY = {
    "Anthropic": "앤트로픽(Anthropic)",
    "NVIDIA": "엔비디아(NVIDIA)",
    "Blackwell": "블랙웰(Blackwell)",
    "HBM": "HBM(고대역폭 메모리)",
    "LLM": "LLM(대규모 언어 모델)",
    "MoE": "MoE(전문가 혼합 모델)",
    "Foundry": "파운드리(위탁 생산)",
    "Startups": "스타트업",
    "Monetization": "수익화",
    "White Noise": "백색 소음"
}

NEWS_JSON_SCHEMA = """
{
    "score": 1~10,
    "cluster": "Intelligence",
    "category": "...",
    "eng_title": "...",
    "eng_keywords": ["Keyword1", "Keyword2", "Brand", "Industry", "Trend"],
    "eng_content": "### Section Title\n\nContent...",
    "kor_title": "...",
    "kor_summary": ["핵심 포인트 1", "핵심 포인트 2"],
    "kor_keywords": ["개체명", "기술명", "트렌드", "전망", "가격/성능"],
    "kor_analysis_title": "Dyanmic keyword-rich subtitle (e.g., 'HBM4 기술의 성능 병목 해결')",
    "kor_content": "### 세부 부제\n\n본문...",
    "kor_insight_title": "Dynamic subtitle (e.g., '엔비디아의 독점 체제에 미칠 영향')",
    "kor_insight": "### 시사점\n\n전문적인 통찰..."
}
"""

SCORING_PROMPT = """
[TASK]: Score these news items from 1-10 based on Tech Innovation, Market Impact, and Global Relevance.
[OUTPUT]: Strictly JSON list of integers. (e.g., [8, 4, 9])
[ITEMS]:
"""

class NewsEditor:
    """[V7.5] 완성형 에디터: 용어 사전, 지능형 스코어링, 백로그 아카이브 탑재"""
    def __init__(self, writer=None):
        self.writer = writer if writer else AIWriter()
        self.authority_sources = ["Reuters", "TechCrunch", "Bloomberg", "The Verge", "CNBC", "Wired", "Engadget", "Digital Trends", "CNET"]

    def _apply_glossary(self, text):
        """[V7.5] 용어 사전을 적용하여 텍스트 정제"""
        if not text: return text
        for eng, kor in GLOSSARY.items():
            # 대소문자 구분 없이 강제 치환 (고유명사 보호)
            text = re.sub(re.escape(eng), kor, text, flags=re.IGNORECASE)
        return text

    def _save_to_backlog(self, article, score):
        """[V7.1] 탈락된 기사를 백로그 파일에 보관"""
        try:
            archive_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive")
            os.makedirs(archive_dir, exist_ok=True)
            backlog_path = os.path.join(archive_dir, "backlog.json")
            
            backlog_data = []
            if os.path.exists(backlog_path):
                with open(backlog_path, "r", encoding="utf-8") as f:
                    try: backlog_data = json.load(f)
                    except: backlog_data = []
            
            if not any(item['url'] == article['url'] for item in backlog_data):
                article['selection_score'] = score
                article['archived_at'] = datetime.now().isoformat()
                backlog_data.append(article)
                with open(backlog_path, "w", encoding="utf-8") as f:
                    json.dump(backlog_data[-300:], f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Backlog Save Error: {e}")

    def _score_articles(self, articles):
        """[V7.0] 기사 선별 스코어러"""
        if not articles: return []
        titles = [f"- {a['title']} ({a.get('source_name')})" for a in articles]
        prompt = SCORING_PROMPT + "\n".join(titles)
        res = self.writer.generate_content(prompt, role="processing")
        try:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if not match: return [articles[0]]
            scores = json.loads(match.group())
            final_selection = []
            for i, score in enumerate(scores):
                if i >= len(articles): break
                source = articles[i].get('source_name', '')
                is_authority = any(src.lower() in source.lower() for src in self.authority_sources)
                if score >= 7 or (score >= 5 and is_authority):
                    final_selection.append(articles[i])
                else:
                    self._save_to_backlog(articles[i], score)
            return final_selection if final_selection else [articles[0]]
        except: return [articles[0]]

    def _is_cached(self, query):
        """[V7.8] 12시간 내 동일 쿼리 중복 분석 방지용 캐시"""
        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".news_cache")
        now = time.time()
        
        cache_data = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f: cache_data = json.load(f)
            except: pass
        
        # 12시간(43200초) 이내면 캐시 히트
        if query in cache_data and (now - cache_data[query]) < 43200:
            return True
            
        # 캐시 갱신
        cache_data[query] = now
        with open(cache_path, "w") as f: json.dump(cache_data, f)
        return False

    def _get_full_event_analysis(self, articles):
        # [V7.8] 캐시 체크로 API 낭비 철저 차단
        query_sig = articles[0]['title'][:30]
        if self._is_cached(query_sig):
            logger.info(f" [CACHE HIT] Already analyzed: {query_sig}")
            return None

        # [V7.0] 우수 기사 선별 후 분석 진행
        selected = self._score_articles(articles)
        if not selected: return None
        truncated = []
        for a in selected:
            content = a.get('description', a.get('content', ''))[:1000]
            truncated.append(f"Source: {a.get('source_name')}\nTitle: {a['title']}\nContent: {content}")
        combined_text = "\n---\n".join(truncated)
        prompt = f"[TASK]: Create a detailed English Tech Report synthesize from these: \n{combined_text}"
        return self.writer.generate_content(prompt, role="processing")

    def _extract_json_safe(self, text):
        if not text: return None
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try: return json.loads(match.group(), strict=False)
            except: pass
        return None

    def review_batch(self, articles, recent_posts=None):
        try:
            event_report_en = self._get_full_event_analysis(articles)
            if not event_report_en or len(event_report_en) < 300: return []

            history_context = ""
            if recent_posts:
                titles = [p.get('title', '') for p in recent_posts[:10]]
                history_context = f"\n[CONTEXT: RECENTLY PUBLISHED TITLES]\n- {chr(10)+'- '.join(titles)}\n"

            localize_prompt = f"""
            [PERSONA]: Senior Technical Journalist & Strategic Analyst.
            [TASK]: Localize the English report into a professional Korean tech paper. 
            {history_context}
            [STRICT RULES]: 100% Korean Integrity. No Gibberish. Professional Journalism Tone.
            [OUTPUT STRUCTURE]: {NEWS_JSON_SCHEMA}
            [REPORT CONTEXT]: {event_report_en}
            """
            
            res = self.writer.generate_content(localize_prompt, role="writing")
            draft = self._extract_json_safe(res)
            
            if draft:
                # [V7.5] 용어 사전 최종 적용 및 정제
                draft['kor_title'] = self._apply_glossary(draft.get('kor_title', ''))
                draft['kor_content'] = self._apply_glossary(draft.get('kor_content', ''))
                draft['kor_insight'] = self._apply_glossary(draft.get('kor_insight', ''))
                
                draft['eng_content'] = event_report_en 
                cluster_map = {
                    "llm-tech": "Intelligence", "ai-agent": "Intelligence", "ai-policy": "Intelligence", "future-sw": "Intelligence",
                    "semi-hbm": "Physical", "hpc-infra": "Physical", "robotics": "Physical",
                    "monetization": "Strategy", "startups-vc": "Strategy", "market-trend": "Strategy",
                    "game-tech": "Digital", "spatial-tech": "Digital"
                }
                cat = draft.get('category', 'ai-tools')
                draft['cluster'] = cluster_map.get(cat, cluster_map.get("llm-tech"))
                draft['original_url'] = articles[0]['url']
                draft['original_image_url'] = articles[0].get('image')
                draft['source_name'] = articles[0].get('source_name', 'Global Sources')
                return [draft]
                
        except Exception as e:
            logger.error(f"NewsEditor Error: {e}")
        return []
