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

class NewsEditor:
    """[V11.2] 고품질 미러링 에디터: 2-Pass 아키텍처 및 한/영 통합 규격 적용"""
    
    # [V11.2] Mirroring Step 1 Schema (English Only)
    EN_JSON_SCHEMA = """
    {
      "title": "SEO-optimized English headline",
      "summary": ["Point 1", "Point 2", "Point 3"],
      "description": "Meta description (max 160 chars)",
      "content": "Professional English tech analysis (Markdown, subheaders use ###)",
      "insight": "Strategic analyst commentary",
      "keywords": ["tag1", "tag2"],
      "category": "ai|hardware|insights",
      "image_prompt": "Vivid image generation prompt"
    }
    """

    # [V11.2] Mirroring Step 2 Schema (Korean Only)
    KO_JSON_SCHEMA = """
    {
      "title": "Attractive Korean headline",
      "summary": ["포인트 1", "포인트 2", "포인트 3"],
      "description": "메타 설명 (최대 160자)",
      "content": "전문적인 한국어 기술 분석 (마크다운 ## 헤더 절대 금지, 상세분석/시사점 등 중복 헤더 금지)",
      "insight": "에디터의 전략적 시사점 (헤더 없이 내용만 작성)",
      "keywords": ["태그1", "태그2"]
    }
    """

    SCORING_PROMPT = """
    [TASK]: Score these news items from 1-10 based on Tech Innovation, Market Impact, and Global Relevance.
    [OUTPUT]: Strictly JSON list of integers. (e.g., [8, 4, 9])
    [ITEMS]:
    """
    def __init__(self, writer=None):
        self.writer = writer if writer else AIWriter()
        self.authority_sources = ["Reuters", "TechCrunch", "Bloomberg", "The Verge", "CNBC", "Wired", "Engadget", "Digital Trends", "CNET"]

    def _apply_glossary(self, text):
        """[V0.2.6 Upgrade] 정규식 단어 경계(\b) 및 소제목 인용구 강제 치환"""
        if not text: return text
        
        # [Strategy] 긴 단어부터 치환하여 부분 일치 오류 방지
        sorted_keys = sorted(GLOSSARY.keys(), key=len, reverse=True)
        
        for eng in sorted_keys:
            kor = GLOSSARY[eng]
            pattern = re.compile(r'\b' + re.escape(eng) + r'(?!\s*\([^)]*\))', re.IGNORECASE)
            text = pattern.sub(kor, text)
            
        # [V0.2.6] 하위 소제목 강제 포맷팅 (인용구 스타일 고정)
        text = re.sub(r'^###\s+', '> ', text, flags=re.MULTILINE)
        text = re.sub(r'^####\s+', '> ', text, flags=re.MULTILINE)
        
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

    def _score_articles(self, articles, model=None):
        """[V7.0] 기사 선별 스코어러 - 고도화된 파싱 및 Fallback 적용"""
        if not articles: return []
        titles = [f"- {a['title']} ({a.get('source_name')})" for a in articles]
        prompt = self.SCORING_PROMPT + "\n".join(titles)
        res = self.writer.generate_content(prompt, role="processing", model=model)
        
        scores = []
        try:
            match = re.search(r'\[(.*?)\]', res, re.DOTALL)
            if match:
                scores = json.loads(f"[{match.group(1)}]")
            else:
                numbers = re.findall(r'\b([1-9]|10)\b', res)
                scores = [int(n) for n in numbers]
        except Exception as e:
            logger.warning(f"Score Parsing Error: {e}")
            scores = [7] * len(articles)

        final_selection = []
        for i, article in enumerate(articles):
            score = scores[i] if i < len(scores) else 7
            source = article.get('source_name', '')
            is_authority = any(src.lower() in source.lower() for src in self.authority_sources)
            is_valid_score = isinstance(score, (int, float))
            if is_valid_score and (score >= 7 or (score >= 5 and is_authority)):
                final_selection.append(article)
            else:
                self._save_to_backlog(article, score)
                
        return final_selection if final_selection else [articles[0]]

    def _is_cached(self, query):
        """[V7.8] 12시간 내 동일 쿼리 중복 분석 방지용 캐시"""
        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".news_cache")
        now = time.time()
        cache_data = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f: cache_data = json.load(f)
            except: pass
        if query in cache_data and (now - cache_data[query]) < 43200:
            return True
        cache_data[query] = now
        with open(cache_path, "w") as f: json.dump(cache_data, f)
        return False

    def _extract_json(self, text):
        if not text: return None
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try: return json.loads(match.group(), strict=False)
            except: pass
        return None

    def review_batch(self, articles, recent_posts=None, model=None, hint_category=None):
        try:
            selected = self._score_articles(articles, model=model)
            if not selected: return []
            truncated = []
            for a in selected:
                content = a.get('description', a.get('content', ''))[:1000]
                truncated.append(f"Source: {a.get('source_name')}\nTitle: {a['title']}\nContent: {content}")
            combined_text = "\n---\n".join(truncated)

            # [V11.2] Step 1: High-Quality English Analysis & Polish
            en_prompt = f"""
            [TASK]: Create a professional English Tech Intelligence Report.
            [DATA]: {combined_text}
            [REQUIREMENTS]:
             - Analyze "Why" and "So What" behind the news.
             - Include technical specs, business risks, and future outlook.
             - Tone: Cold, analytical, Bloomberg-style.
             - Formatting: Use Markdown. Subheaders should use '###'.
            [OUTPUT FORMAT]: JSON based on this schema:
            {self.EN_JSON_SCHEMA}
            """
            
            res_en = self.writer.generate_content(en_prompt, role="processing", model=model)
            en_draft = self._extract_json(res_en)
            if not en_draft: return []

            # [V11.2] Step 2: Mirrored Korean Localization
            ko_prompt = f"""
            [TASK]: Localize and Mirror the following English tech report into a professional Korean article.
            [INPUT]: {json.dumps(en_draft, ensure_ascii=False)}
            [REQUIREMENTS]:
             - Mirror the structure and depth of the English version perfectly.
             - NO AI FILLER. Use professional, critical perspective.
             - **CRITICAL**: Do NOT include headings like '상세 분석', '심층 분석', '시사점', '인사이트 비평' within the content/insight fields. These are added by the template.
             - Subheaders inside 'content' should use '###' (e.g., ### 기술적 배경).
             - Tone: Authoritative and Insightful.
            [GLOSSARY]: {json.dumps(GLOSSARY, ensure_ascii=False)}
            [OUTPUT FORMAT]: JSON based on this schema:
            {self.KO_JSON_SCHEMA}
            """
            
            res_ko = self.writer.generate_content(ko_prompt, role="writing", model=model)
            ko_draft = self._extract_json(res_ko)
            if not ko_draft: return []
            
            # [Final Merge & Flattening]
            cat = en_draft.get('category', hint_category if hint_category else 'ai')
            valid_cats = ["ai", "hardware", "insights"]
            if cat not in valid_cats:
                legacy_map = {"ai-models": "ai", "ai-tools": "ai", "gpu-chips": "hardware", "pc-robotics": "hardware", "compare": "insights", "analysis": "insights"}
                cat = legacy_map.get(cat, "ai")
            
            final_article = {
                "eng_title": en_draft.get('title'),
                "kor_title": ko_draft.get('title'),
                "eng_summary": en_draft.get('summary', []),
                "kor_summary": ko_draft.get('summary', []),
                "eng_description": en_draft.get('description', ""),
                "kor_description": ko_draft.get('description', ""),
                "eng_content": en_draft.get('content', ""),
                "kor_content": ko_draft.get('content', ""),
                "eng_insight": en_draft.get('insight', ""),
                "kor_insight": ko_draft.get('insight', ""),
                "eng_keywords": en_draft.get('keywords', []),
                "kor_keywords": ko_draft.get('keywords', []),
                "category": cat,
                "cluster": cat,
                "image_prompt_core": en_draft.get('image_prompt', "Tech innovation"),
                "original_url": articles[0]['url'],
                "original_image_url": articles[0].get('image'),
                "source_name": articles[0].get('source_name', 'Global Sources')
            }
            
            # Apply Global Formatting (### -> > )
            for key in ["eng_content", "kor_content"]:
                content = final_article.get(key, "")
                if content:
                    content = re.sub(r'^###\s+', '> ', content, flags=re.MULTILINE)
                    final_article[key] = content
            
            return [final_article]
                
        except Exception as e:
            logger.error(f"NewsEditor Error: {e}")
        return []
