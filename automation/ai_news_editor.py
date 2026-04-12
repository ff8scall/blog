import json
import re
import time
from ai_writer import AIWriter

class NewsEditor:
    def __init__(self, writer=None):
        self.writer = writer if writer else AIWriter()

    def review_batch(self, articles, recent_posts=None):
        """[V15.1] Context-Aware Editorial Workflow (Recent History integration)"""
        all_drafts = []
        
        # 최근 기사 맥락 구성
        recent_context = ""
        if recent_posts:
            recent_context = "\n[Recent Articles Context (for internal reference)]:\n" + \
                             "\n".join([f"- {p['title']}" for p in recent_posts])
        
        # [V15.0] 여러 기사가 하나의 그룹으로 들어오면 병합 처리
        is_merged = len(articles) > 1
        source_titles = " | ".join([a['title'] for a in articles])
        source_contents = "\n\n---\n\n".join([f"Source [{i+1}]: {a.get('description', '')}" for i, a in enumerate(articles)])
        
        try:
            # [Step 1] Journalism-Level English Polish (Multi-Source Support)
            merge_instruction = "MERGE the following multiple sources into a single coherent report." if is_merged else "Expand the following news."
            polish_prompt = f"""
            Task: {merge_instruction} Create a high-end Journalism feature in English.
            Rules: Use advanced vocabulary, 6+ robust paragraphs.
            Focus: Industry disruption, Business Impact, and Market competitive landscape.
            Visuals: If numerical data is present, include a Markdown Table summary.
            
            Source Titles: {source_titles}
            Source Contents:
            {source_contents}
            
            {recent_context}
            
            Output ONLY the polished English content in Markdown format.
            """
            
            print(f" [*] Step 1: {'Merging and ' if is_merged else ''}Polishing English content for '{articles[0]['title'][:30]}...'")
            polished_en = self.writer.generate_content(polish_prompt, model="gemini-3.1-flash-lite-preview")
            if not polished_en or len(polished_en) < 300:
                print(f" [!] Step 1 failed. Skipping.")
                return []

            # [Step 2] Strategic Localization & Korean Insight
            localize_prompt = f"""
            Task: Localize the provided English Journalism piece for a premium Korean tech magazine.
            Context: This report was synthesized from {len(articles)} different sources (Global & Local).
            Identity: Senior Tech Strategist.
            Rules: Advanced Korean business terminology, sharp insights.
            SEO Constraints:
            - 'eng_title': Max 65 characters.
            - 'kor_title': Max 35 characters.
            Output Format: STRICT JSON ONLY.
            
            JSON Structure: {{ 
                "score": 10, 
                "category": "ai-tech", 
                "eng_title": "...", 
                "kor_title": "...", 
                "eng_content": "(Use the polished English content)", 
                "kor_content": "(Localized Korean version)", 
                "kor_summary": "...", 
                "kor_insight": "비즈니스 임팩트: ... 전략적 전망: ..." 
            }}
            
            Polished English Content:
            {polished_en}
            """
            
            print(f" [*] Step 2: Localizing and generating insights in Korean...")
            res = self.writer.generate_content(localize_prompt, model="gemini-2.0-flash")
            if not res: return []
            
            start_idx = res.find("{")
            end_idx = res.rfind("}")
            if start_idx != -1 and end_idx != -1:
                clean_json = res[start_idx:end_idx+1]
                try:
                    draft = json.loads(clean_json, strict=False)
                    # [V14.1] AI가 생성한 불필요한 제목 헤더 보정
                    for field in ['eng_content', 'kor_content', 'kor_summary']:
                        if field in draft:
                            draft[field] = re.sub(r'^#+.*?\n', '', draft[field]).strip()
                    
                    if 'eng_title' in draft: draft['eng_title'] = draft['eng_title'][:70]
                    if 'kor_title' in draft: draft['kor_title'] = draft['kor_title'][:40]

                    # 카테고리 보정 (분류 정확도 고도화)
                    text_pool = f"{draft.get('category','')} {draft.get('kor_title', '')} {draft.get('eng_title', '')}".lower()
                    if any(k in text_pool for k in ['agent', '에이전트', 'autonomous', '자율주행']): draft['category'] = 'ai-agents'
                    elif any(k in text_pool for k in ['hard', 'chip', 'hw', 'gpu', 'nvidia', 'hbm', 'ddr', '반도체', '하드웨어', '서버', 'server']): draft['category'] = 'hardware'
                    elif any(k in text_pool for k in ['game', 'gaming', '플레이', '게임', 'nintendo', 'switch', 'sony', 'ps5', 'xbox', 'steam', 'unreal']): draft['category'] = 'gaming'
                    elif any(k in text_pool for k in ['strategy', '전략', '수익', 'monetization', 'profit', '비즈니스']): draft['category'] = 'monetization'
                    elif any(k in text_pool for k in ['biz', 'trend', '시장', '동향', 'market', 'outlook', 'analysis']): draft['category'] = 'tech-biz'
                    else: draft['category'] = 'ai-tech'
                    
                    # 대표 이미지 및 URL은 그룹의 첫 번째(주로 글로벌) 기사 기준
                    draft['original_image_url'] = articles[0].get('urlToImage') or articles[0].get('image')
                    draft['original_url'] = articles[0].get('url')
                    
                    all_drafts.append(draft)
                except: pass
        except Exception as e:
            print(f" [!] Editorial process failed: {e}")
            
        return all_drafts
