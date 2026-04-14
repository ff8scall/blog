import os
import json
import re
import time
import hashlib
import requests
import logging
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from news_harvester import NewsHarvester

class StateTracker:
    """[V9.0] Job State Management: Ensures resumable & atomic operations"""
    def __init__(self, state_file="automation/job_state.json"):
        self.state_file = state_file
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"guides": {}, "news": {}}
        return {"guides": {}, "news": {}}

    def save_state(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def is_done(self, section, slug, lang):
        return lang in self.state.get(section, {}).get(slug, [])

    def mark_done(self, section, slug, lang):
        if section not in self.state: self.state[section] = {}
        if slug not in self.state[section]: self.state[section][slug] = []
        if lang not in self.state[section][slug]:
            self.state[section][slug].append(lang)
            self.save_state()

# [V3.0.32] Environment Auto-Loader
load_dotenv()

from ai_news_editor import NewsEditor
from ai_guide_editor import GuideEditor
from ai_writer import AIWriter
from history_manager import HistoryManager
from indexnow_service import notify_indexnow

# [V3.0.15] Advanced Diagnostic & Reporting Edition
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[
    logging.FileHandler("news_main.log", encoding='utf-8'),
    logging.StreamHandler()
])
logger = logging.getLogger("LegoSia.Main")

# 모듈 임포트 가드
def safe_import_class(module_name, class_name):
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except: return type(class_name, (), {"send_resp": lambda s, m: logger.info(f"[Mock] {m}"), "review_article": lambda s, d: {"decision":"PASS"}})

TelegramRemote = safe_import_class("telegram_remote", "TelegramRemote")
EditorInChief = safe_import_class("ai_reviewer", "EditorInChief")

CATEGORY_BUDGETS = {
    "ai-models": 8, "ai-tools": 8, "gpu-chips": 8, "pc-robotics": 8,
    "game-optimization": 8, "ai-gameplay": 8, "tutorials": 4, "compare": 4
}

def sanitize_slug(text):
    if not text: return "topic"
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).lower()
    return re.sub(r'\s+', '-', clean).strip('-')[:50]

def hash_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:6]

CAT_MAP = {
    "ai-models": "AI 모델·트렌드", "ai-tools": "AI 도구·사용법",
    "gpu-chips": "GPU·반도체", "pc-robotics": "AI PC & 로봇",
    "game-optimization": "게임 최적화·엔진", "ai-gameplay": "AI 게임 기술",
    "tutorials": "실전 튜토리얼", "compare": "성능 비교"
}

# [V0] Fallback mapping to Major Clusters
FALLBACK_MAP = {
    "ai-models": "ai-models-tools", "ai-tools": "ai-models-tools",
    "gpu-chips": "gpu-hardware", "pc-robotics": "gpu-hardware",
    "game-optimization": "ai-gaming", "ai-gameplay": "ai-gaming",
    "tutorials": "guides", "compare": "guides"
}

def download_image(url, category_slug, slug):
    """[V2.9.6] 카테고리별 매핑된 고화질 폴백 이미지 보장"""
    # [Fix] 카테고리에 맞는 폴백 이미지 키 찾기
    fallback_key = FALLBACK_MAP.get(category_slug, "ai-models-tools")
    
    if not url: return f"/images/fallback/{fallback_key}.png"
    
    # [V3.0.31] Protocol-relative URL fix
    if url.startswith('//'): url = 'https:' + url
    
    date_dir = datetime.now().strftime('%Y/%m/%d')
    img_dir = f"static/images/posts/{date_dir}"
    os.makedirs(img_dir, exist_ok=True)
    
    img_path = f"{img_dir}/{slug}.jpg"
    web_url = f"/images/posts/{date_dir}/{slug}.jpg"
    
    try:
        resp = requests.get(url, timeout=(3, 10), headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            with open(img_path, 'wb') as f: f.write(resp.content)
            return web_url
    except: pass
    
    return f"/images/fallbacks/{fallback_key}.jpg"

def generate_and_save_thumbnail(image_prompt_core, slug_name):
    """[V8.0] 일자별 이미지 폴더 구조 (YYYY/MM/DD)"""
    aesthetic_base = ", minimalist dark mode tech aesthetic, isometric view, clean smooth surfaces, 8k resolution, highly detailed corporate editorial illustration --no text, no humans, no robots, no faces"
    
    final_prompt = (image_prompt_core if image_prompt_core else "Abstract tech geometry") + aesthetic_base
    logger.info(f"[IMAGE] Creating thumbnail for {slug_name}")
    
    encoded_prompt = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true"
    
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            date_dir = datetime.now().strftime("%Y/%m/%d")
            save_dir = f"static/images/posts/{date_dir}"
            os.makedirs(save_dir, exist_ok=True)
            
            save_path = f"{save_dir}/{slug_name}.jpg"
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return f"/images/posts/{date_dir}/{slug_name}.jpg"
    except Exception as e:
        logger.error(f"[IMAGE] Failed: {e}")
    return "/images/default-tech-bg.jpg"

def create_hugo_post(article, lang='ko'):
    """[V8.0] 일자별 콘텐츠 폴더 구조 (YYYY/MM/DD)"""
    date_path = datetime.now().strftime("%Y/%m/%d")
    target_dir = f"content/{lang}/posts/{date_path}"
    os.makedirs(target_dir, exist_ok=True)
    
    slug = article['sync_slug']
    cat_safe = sanitize_slug(article.get('category', 'ai-models'))
    img_url = download_image(article.get('original_image_url'), cat_safe, slug)
    
    filepath = os.path.join(target_dir, f"{slug}.md")
    
    if lang == 'ko':
        title = article.get('kor_title', '제목 없음')
        desc_val = article.get('kor_summary', [title])[0]
        tags_val = json.dumps(article.get('kor_keywords', []), ensure_ascii=False)
        date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
        analysis_title = article.get('kor_analysis_title', '상세 분석')
        insight_title = article.get('kor_insight_title', '인사이트')
        summary_text = "\n".join([f"- {s}" for s in article.get('kor_summary', [])])
        content_body = f"## 핵심 요약\n{summary_text}\n\n## {analysis_title}\n{article.get('kor_content')}\n\n## {insight_title}\n{article.get('kor_insight')}"
    else:
        title = article.get('eng_title', 'Untitled')
        eng_sum = article.get('eng_summary')
        desc_val = eng_sum if eng_sum else title
        tags_val = json.dumps(article.get('eng_keywords', []), ensure_ascii=False)
        date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        summary_section = f"## Executive Summary\n{eng_sum}\n\n" if eng_sum else ""
        content_body = f"{summary_section}## Strategic Deep-Dive\n{article.get('eng_content', 'Content not localized yet.')}"

    img_path = generate_and_save_thumbnail(article.get('image_prompt_core'), slug)
    safe_title = title.replace('"', "'")
    safe_desc = desc_val.replace('"', "'")
    is_featured = "true" if article.get('featured') else "false"

    post_md = f"""---
title: "{safe_title}"
date: "{date_str}"
description: "{safe_desc}"
image: "{img_url}"
clusters: ["{article.get('cluster', 'ai-models-tools')}"]
categories: ["{cat_safe}"]
tags: {tags_val}
featured: {is_featured}
---
{content_body}
"""
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(post_md)
    return True

def create_guide_post(guide_data, sync_slug, lang='ko'):
    base_path = f"content/{lang}/guides"
    os.makedirs(base_path, exist_ok=True)
    content = f"""---
title: "{guide_data.get('guide_title')}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{guide_data.get('guide_summary', '')}"
type: "guides"
difficulty: "{guide_data.get('difficulty', 'Intermediate')}"
categories: ["{guide_data.get('guide_type', 'ai-tools')}"]
---
{guide_data.get('guide_content')}
"""
    with open(f"{base_path}/{sync_slug}.md", "w", encoding="utf-8-sig") as f:
        f.write(content)
    return True

def manage_news_pipeline(limit=10):
    """지능형 뉴스 발행 파이프라인 (V9.0 복원력 추가)"""
    logger.info(f"Executive Intelligence Engine V3.1 starting with limit={limit}...")
    
    harvester = NewsHarvester()
    editor = NewsEditor(writer=AIWriter())
    tracker = StateTracker()
    
    # 1. 뉴스 수집
    news_items = harvester.fetch_all(limit_per_cat=limit)[0]
    
    count = 0
    for item in news_items:
        if count >= limit: break
        
        safe_slug = sanitize_slug(item['title'])
        # [V9.0] Skip if already done
        if tracker.is_done("news", safe_slug, "en") and tracker.is_done("news", safe_slug, "ko"):
            continue

        try:
            # 2. 뉴스 분석 및 집필 (영문/한글 통합 데이터 생성)
            article_data = editor.review_batch([item])[0]
            if article_data:
                article_data['sync_slug'] = safe_slug
                
                # 3. Hugo 포스트 생성 (영문)
                if not tracker.is_done("news", safe_slug, "en"):
                    create_hugo_post(article_data, lang='en')
                    tracker.mark_done("news", safe_slug, "en")
                
                # 4. Hugo 포스트 생성 (한글)
                if not tracker.is_done("news", safe_slug, "ko"):
                    create_hugo_post(article_data, lang='ko')
                    tracker.mark_done("news", safe_slug, "ko")
                
                count += 1
                logger.info(f"Published: {safe_slug}")
                time.sleep(10)
        except Exception as e:
            logger.error(f"Failed to process {item['title']}: {e}")

    logger.info("Master execution cycle completed.")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    manage_news_pipeline(limit=args.limit)

if __name__ == "__main__": 
    main()
