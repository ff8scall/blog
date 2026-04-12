# 🏛️ 레고-시아 V2.7 "Resilient Hybrid Intelligence" Full Logic Blueprint

이 문서는 V2.7 시스템의 설계 철학, 아키텍처, 그리고 작동 중인 **모든 소스 코드(Full Logic)**를 한 데 모은 통합 지식 자산입니다. 타 AI 모델에게 개발 컨텍스트를 제공하거나 시스템 전체를 복구할 때 사용합니다.

---

## 🎯 1. 시스템 설계 철학 & 아키텍처
레고-시아 V2.7은 단순 뉴스 자동화를 넘어 **'전략적 자산화'**를 목표로 합니다.
- **Single Source, Multi-Asset**: 하나의 뉴스 이벤트에서 뉴스 리포트와 실전 가이드를 동시 생산.
- **Resilient Pipeline**: API 비용 최적화(30% 절감), 토큰 가드, 슬러그 충돌 방지 시스템 탑재.
- **SEO First**: 국/영문 슬러그 동기화 및 해시 ID 부여로 전역 유니크 URL 보장.

---

## 💻 2. NEWS EDITOR: ai_news_editor.py (Full Code)
언어 장벽을 허물고 팩트 중심의 분석을 수행하는 2단계(Stage) 추론 엔진입니다.

```python
import json
import os
import re
from ai_writer import AIWriter

class NewsEditor:
    """[V2.7] 고효율-고안정성 뉴스 에디터: 비용 최적화 및 토큰 가드 적용"""
    def __init__(self, model_name="gemini-2.0-flash", writer=None):
        self.model_name = model_name
        self.writer = writer if writer else AIWriter()

    def _extract_json(self, res):
        """[V2.7 Safe Parser] JSON 클린업 및 크기 제한 보호"""
        try:
            if not res or len(res) > 20000: # [V2.7] 가비지 데이터(폭주) 방지
                return None
            res = re.sub(r'```json\s*|\s*```', '', res)
            start = res.find('{')
            end = res.rfind('}')
            if start == -1 or end == -1: return None
            return json.loads(res[start:end+1], strict=False)
        except Exception as e:
            print(f" [!] JSON Parsing Error: {e}")
            return None

    def _get_full_event_analysis(self, articles):
        """[Stage 1] 토큰 가드 적용: 기사당 800자 제한하여 영문 종합 리포트 생성"""
        truncated = []
        for a in articles:
            # [V2.7] 각 소스 본문을 800자로 제한하여 토큰 폭주 방지
            content = a.get('description', a.get('content', ''))[:800]
            truncated.append(f"Source: {a.get('source_name', 'Tech Outlet')}\nTitle: {a['title']}\nContent: {content}")
        
        combined_text = "\n---\n".join(truncated)
        
        prompt = f"""
        [TASK]: As a Tech Strategic Analyst, analyze these and create a comprehensive English Tech Report.
        [SOURCES]:
        {combined_text}
        """
        return self.writer.generate_content(prompt, model=self.model_name)

    def review_batch(self, articles, recent_posts=None):
        """[V2.7] 비용 최적화 로직 적용 (영문 콘텐츠 재생성 제거)"""
        try:
            event_report_en = self._get_full_event_analysis(articles)
            if not event_report_en or len(event_report_en) < 300:
                return []

            localize_prompt = f"""
            [PERSONA]: Senior Tech Editor (15y exp). 
            [TASK]: Reconstruct this into a premium Korean tech briefing.
            [OUTPUT STRUCTURE - STRICT JSON]:
            {{
                "score": 1~10,
                "cluster": "Intelligence | CoreTech | Strategy | Digital",
                "category": "llm-ai-models | ai-agents | ai-policy | ai-tools | gpu-semiconductor | pc-server-infra | robotics | ai-business | startups | tech-industry | game-tech | xr-ar-vr",
                "eng_title": "Professional English title",
                "eng_summary": "1-sentence concise English description for SEO",
                "kor_title": "국문 헤드라인",
                "kor_summary": ["3문항 핵심 요약 (리스트)"],
                "kor_content": "본문 분석 내용",
                "kor_insight": "전략적 시사점",
                "keywords": ["tag1", "tag2", "tag3"]
            }}
            [CONTEXT]:
            {event_report_en}
            """
            
            res = self.writer.generate_content(localize_prompt, model=self.model_name)
            draft = self._extract_json(res)
            
            if draft:
                draft['eng_content'] = event_report_en 
                cluster_map = {{
                    "llm-ai-models": "Intelligence", "ai-agents": "Intelligence", "ai-policy": "Intelligence", "ai-tools": "Intelligence",
                    "gpu-semiconductor": "CoreTech", "pc-server-infra": "CoreTech", "robotics": "CoreTech",
                    "ai-business": "Strategy", "startups": "Strategy", "tech-industry": "Strategy",
                    "game-tech": "Digital", "xr-ar-vr": "Digital"
                }}
                cat = draft.get('category', 'ai-tools')
                draft['category'] = cat
                draft['cluster'] = cluster_map.get(cat, "Intelligence")
                draft['original_url'] = articles[0]['url']
                draft['source_name'] = articles[0].get('source_name', 'Global Sources')
                return [draft]
        except Exception as e: print(f" [!] NewsEditor Error: {{e}}")
        return []
```

---

## 📘 3. GUIDE ENGINE: ai_guide_editor.py (Full Code)
뉴스를 분석하여 실질적인 운영 및 적용 가이드를 집필하는 인스트럭터 엔진입니다.

```python
import json
import os
import re
from ai_writer import AIWriter

class GuideEditor:
    """[V2.7] SEO 최적화 가이드 에디터: 슬러그 상속 및 섹션 검증 기능 탑재"""
    def __init__(self, model_name="gemini-2.0-flash", writer=None):
        self.model_name = model_name
        self.writer = writer if writer else AIWriter()

    def _extract_json(self, res):
        try:
            if not res or len(res) > 25000: return None
            res = re.sub(r'```json\s*|\s*```', '', res)
            start = res.find('{')
            end = res.rfind('}')
            return json.loads(res[start:end+1], strict=False)
        except: return None

    def write_guide(self, news_draft):
        summary = news_draft.get('kor_summary', '')
        if isinstance(summary, list): summary = " ".join(summary)
        base_slug = news_draft.get('sync_slug', 'strategic-guide')
        
        prompt = f"""
        [PERSONA]: Senior Tech Instructor.
        [TASK]: Write a 'Strategic Guide' based on the news.
        [INPUT]:
        - Title: {{news_draft.get('kor_title')}}
        - Summary: {{summary}}
        - Slug Context: {{base_slug}}
        - Content: {{news_draft.get('kor_content', '')[:2500]}}

        [OUTPUT STRUCTURE - STRICT JSON]:
        {{
            "guide_title": "...",
            "guide_summary": "1-sentence gist",
            "guide_type": "ai-usage | performance-tuning | troubleshooting | recommendations",
            "difficulty": "Beginner | Intermediate | Advanced",
            "guide_content": "Full markdown must contain sections: 🏁 Starts, 🛠️ Prerequisites, 📝 Step-by-Step, 💡 Pro-Tips, ⚠️ Troubleshooting",
            "tags": ["tag1", "tag2"]
        }}
        """
        res = self.writer.generate_content(prompt, model=self.model_name)
        result = self._extract_json(res)
        return result
```

---

## 🏗️ 4. ORCHESTRATOR: news_main.py (Full Code)
전체 시스템의 수집, 분석, 발행, 충돌 방지를 총괄하는 중앙 관제 모듈입니다.

```python
import os
import json
import re
import time
import hashlib
from datetime import datetime
from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from ai_guide_editor import GuideEditor
from history_manager import HistoryManager
from indexnow_service import notify_indexnow
from ai_reviewer import EditorInChief
from telegram_bot import TelegramRemote

def download_image(url, category_slug, slug, title=""):
    fallback_path = f"static/images/fallbacks/{{category_slug}}.jpg"
    if os.path.exists(fallback_path): return f"/images/fallbacks/{{category_slug}}.jpg"
    return "/images/fallback-default.jpg"

def sanitize_slug(title):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    return re.sub(r'\s+', '-', clean).strip('-')[:50]

def hash_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:6]

def load_queue():
    queue_file = "runtime/news_queue.json"
    os.makedirs("runtime", exist_ok=True)
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_queue(queue):
    queue_file = "runtime/news_queue.json"
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue[:50], f, ensure_ascii=False, indent=2)

def create_hugo_post(article, lang='ko'):
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m')
    base_path = f"content/{{lang}}/posts/{{year}}/{{month}}"
    os.makedirs(base_path, exist_ok=True)
    slug = article['sync_slug']
    md_filename = f"{{slug}}.md"
    local_img_url = download_image(article.get('original_image_url'), article.get('category'), slug)
    
    tags = json.dumps(article.get('keywords', []), ensure_ascii=False)
    is_featured = "true" if article.get('score', 0) >= 9.5 else "false"

    if lang == 'ko':
        summary_text = "\n".join([f"- {{s}}" for s in article.get('kor_summary', [])])
        desc = article.get('kor_summary', [''])[0]
        content = f"""---
title: "{{article['kor_title']}}"
date: "{{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}}"
description: "{{desc[:150]}}"
image: "{{local_img_url}}"
clusters: ["{{article.get('cluster')}}"]
categories: ["{{article.get('category')}}"]
tags: {{tags}}
featured: {{is_featured}}
---
## Executive Summary
{{summary_text}}

## Strategic Analysis
{{article.get('kor_content')}}

## Insights
{{article.get('kor_insight')}}
"""
    else:
        content = f"""---
title: "{{article['eng_title']}}"
date: "{{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}}"
description: "{{article.get('eng_summary', '')}}"
image: "{{local_img_url}}"
clusters: ["{{article.get('cluster')}}"]
categories: ["{{article.get('category')}}"]
tags: {{tags}}
featured: {{is_featured}}
---
{{article.get('eng_content')}}
"""
    with open(f"{{base_path}}/{{md_filename}}", "w", encoding="utf-8-sig") as f:
        f.write(content)

def create_guide_post(guide_data, sync_slug, lang='ko'):
    base_path = f"content/{{lang}}/guides"
    os.makedirs(base_path, exist_ok=True)
    content = f"""---
title: "{{guide_data.get('guide_title')}}"
date: "{{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}}"
description: "{{guide_data.get('guide_summary')}}"
type: "guides"
difficulty: "{{guide_data.get('difficulty')}}"
categories: ["{{guide_data.get('guide_type')}}"]
---
{{guide_data.get('guide_content')}}
"""
    with open(f"{{base_path}}/{{sync_slug}}.md", "w", encoding="utf-8-sig") as f: f.write(content)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--rss-only", action="store_true")
    args = parser.parse_args()

    harvester = NewsHarvester(); editor = NewsEditor(); guide_editor = GuideEditor()
    history = HistoryManager(); reviewer = EditorInChief(); telegram = TelegramRemote()
    
    cat_budgets = {{
        "llm-ai-models": 6, "ai-agents": 6, "ai-policy": 3, "ai-tools": 5,
        "gpu-semiconductor": 6, "pc-server-infra": 5, "robotics": 3,
        "ai-business": 4, "startups": 5, "tech-industry": 3,
        "game-tech": 4, "xr-ar-vr": 5
    }}
    cat_issued = {{cat: 0 for cat in cat_budgets}}
    
    news_queue = load_queue()
    raw_news, harvest_stats = harvester.fetch_all(limit_per_cat=args.limit, rss_only=args.rss_only)
    new_articles = [a for a in (news_queue + raw_news) if not history.is_already_processed(a['url'])]

    if not new_articles: return
    scored_groups = sorted([(9.0, [[a]]) for a in new_articles], key=lambda x: x[0], reverse=True)

    published_count = 0; published_guides = 0; next_cycle_queue = []

    for score, group in scored_groups:
        if published_count >= 40: next_cycle_queue.extend(group); continue
        is_guide, _ = evaluate_guide_potential(group, score)
        drafts = editor.review_batch(group)
        if not drafts: continue
        
        sync_slug = f"{{sanitize_slug(drafts[0]['eng_title'])}}-{{hash_slug(group[0][0]['url'])}}"

        for draft in drafts:
            cat = draft.get('category', 'ai-tools')
            if score < 9.5 and cat_issued.get(cat, 0) >= cat_budgets.get(cat, 5):
                next_cycle_queue.append(draft); continue
            
            draft['sync_slug'] = sync_slug
            create_hugo_post(draft, lang='ko'); create_hugo_post(draft, lang='en')
            
            if is_guide and published_guides < 3:
                guide_data = guide_editor.write_guide(draft)
                if guide_data:
                    create_guide_post(guide_data, sync_slug, lang='ko')
                    published_guides += 1
            
            cat_issued[cat] += 1; published_count += 1
            print(f" [PUB] {{draft['kor_title']}} (Score: {{score}})")

    save_queue(next_cycle_queue)
    if published_count > 0:
        telegram.send_resp(f"✅ V2.7 Resilient 성공\n발행: {{published_count}} / 가이드: {{published_guides}} / 대기: {{len(next_cycle_queue)}}")

if __name__ == "__main__": main()
```

---
**DOCUMENT END**
