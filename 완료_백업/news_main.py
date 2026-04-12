import os
import json
import re
import time
import hashlib
import requests
from datetime import datetime
from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from ai_guide_editor import GuideEditor
from history_manager import HistoryManager
from indexnow_service import notify_indexnow
from ai_reviewer import EditorInChief
from telegram_remote import TelegramRemote

# [V2.7.1] 환경 설정 및 상수
MAX_GUIDES_PER_DAY = 3
CATEGORY_BUDGETS = {
    "llm-ai-models": 6, "ai-agents": 6, "ai-policy": 3, "ai-tools": 5,
    "gpu-semiconductor": 6, "pc-server-infra": 5, "robotics": 3,
    "ai-business": 4, "startups": 5, "tech-industry": 3,
    "game-tech": 4, "xr-ar-vr": 5
}

def download_image(url, category_slug, slug):
    """[V2.7.1 Safe Downloader]"""
    if not url: return f"/images/fallbacks/{category_slug}.jpg"
    
    img_dir = f"static/images/posts/{datetime.now().strftime('%Y/%m')}"
    os.makedirs(img_dir, exist_ok=True)
    img_path = f"{img_dir}/{slug}.jpg"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            return img_path.replace('static', '')
    except Exception as e:
        print(f" [!] Image down error: {e}")
    
    return f"/images/fallbacks/{category_slug}.jpg"

def sanitize_slug(title):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    return re.sub(r'\s+', '-', clean).strip('-')[:50]

def hash_slug(url):
    return hashlib.md5(url.encode()).hexdigest()[:6]

def load_queue():
    queue_file = "runtime/news_queue.json"
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_queue(queue):
    os.makedirs("runtime", exist_ok=True)
    with open("runtime/news_queue.json", "w", encoding="utf-8") as f:
        json.dump(queue[:100], f, ensure_ascii=False, indent=2)

def create_hugo_post(article, lang='ko'):
    year, month = datetime.now().strftime('%Y'), datetime.now().strftime('%m')
    base_path = f"content/{lang}/posts/{year}/{month}"
    os.makedirs(base_path, exist_ok=True)
    
    slug = article['sync_slug']
    md_filename = f"{slug}.md" # [V2.7.1 Fix] 리터럴 중괄호 제거
    local_img_url = download_image(article.get('original_image_url'), article.get('category'), slug)
    
    tags = json.dumps(article.get('keywords', []), ensure_ascii=False)
    is_featured = "true" if article.get('score', 0) >= 9.5 else "false"

    if lang == 'ko':
        summary_text = "\n".join([f"- {s}" for s in article.get('kor_summary', [])])
        content = f"""---
title: "{article['kor_title']}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{(article.get('kor_summary', [''])[0])[:150]}"
image: "{local_img_url}"
clusters: ["{article.get('cluster')}"]
categories: ["{article.get('category')}"]
tags: {tags}
featured: {is_featured}
---
## Executive Summary
{summary_text}

## Strategic Analysis
{article.get('kor_content')}

## Insights
{article.get('kor_insight')}

---
*참조 소스: {article.get('source_name', 'Global Tech Sources')}*
"""
    else:
        content = f"""---
title: "{article['eng_title']}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{article.get('eng_summary', '')}"
image: "{local_img_url}"
clusters: ["{article.get('cluster')}"]
categories: ["{article.get('category')}"]
tags: {tags}
featured: {is_featured}
---
{article.get('eng_content')}

---
*Published by Lego-Sia Intelligence V2.7.1*
"""
    with open(f"{base_path}/{md_filename}", "w", encoding="utf-8-sig") as f:
        f.write(content)

def create_guide_post(guide_data, sync_slug, lang='ko'):
    base_path = f"content/{lang}/guides"
    os.makedirs(base_path, exist_ok=True)
    content = f"""---
title: "{guide_data.get('guide_title')}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{guide_data.get('guide_summary')}"
type: "guides"
difficulty: "{guide_data.get('difficulty')}"
categories: ["{guide_data.get('guide_type')}"]
---
{guide_data.get('guide_content')}

---
*Created by Lego-Sia Strategic Guide Engine V2.7.1*
"""
    with open(f"{base_path}/{sync_slug}.md", "w", encoding="utf-8-sig") as f:
        f.write(content)

def group_articles_by_topic(articles):
    """[V2.7.1 Restored] 단순 제목 기반 그룹화"""
    return [[a] for a in articles] # 고도화 여부에 따라 Jaccard 추가 가능

def calculate_editorial_score(group):
    """[V2.7.1 Restored] 에디토리얼 점수 산출"""
    # 팩트 수, 소스 신뢰도 등에 따른 가중치 (임시 8.5~9.5)
    return 9.0

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--rss-only", action="store_true")
    args = parser.parse_args()

    harvester = NewsHarvester(); editor = NewsEditor(); guide_editor = GuideEditor()
    history = HistoryManager(); reviewer = EditorInChief(); telegram = TelegramRemote()
    
    cat_issued = {cat: 0 for cat in CATEGORY_BUDGETS}
    news_queue = load_queue()
    raw_news, _ = harvester.fetch_all(limit_per_cat=args.limit, rss_only=args.rss_only)
    
    # 중복 필터링
    new_articles = [a for a in (news_queue + raw_news) if not history.is_already_processed(a['url'])]
    if not new_articles: return

    # [V2.7.1] 로직 원복: 그룹화 및 스코어링
    article_groups = group_articles_by_topic(new_articles)
    scored_groups = sorted([(calculate_editorial_score(g), g) for g in article_groups], key=lambda x: x[0], reverse=True)

    published_count, published_guides = 0, 0
    published_urls, next_cycle_queue = [], []
    recent_posts = history.get_recent_posts(limit=10)

    for score, group in scored_groups:
        if published_count >= 30:
            next_cycle_queue.extend(group); continue # [V2.7.1 Fix] 원본 데이터 유지

        # [V2.7.1 Fix] 가이드 감지 강화
        is_guide = score >= 8.5 and any(k in group[0]['title'].lower() for k in ['how to', '설치', '방법', 'optimize'])
        
        drafts = editor.review_batch(group, recent_posts=recent_posts)
        if not drafts: continue
        
        # [V2.7.1 Fix] 해시 슬러그 인덱싱 수정
        sync_slug = f"{sanitize_slug(drafts[0]['eng_title'])}-{hash_slug(group[0]['url'])}"

        for draft in drafts:
            cat = draft.get('category', 'ai-tools')
            if score < 9.5 and cat_issued.get(cat, 0) >= CATEGORY_BUDGETS.get(cat, 5):
                next_cycle_queue.extend(group); continue
            
            draft['sync_slug'], draft['score'] = sync_slug, score
            if reviewer.review_article(draft).get('decision') != 'PASS': continue

            # 뉴스 발행 (KO/EN)
            create_hugo_post(draft, lang='ko')
            create_hugo_post(draft, lang='en')
            
            # [V2.7.1 Handshake] 가이드 발행 (Global 지원)
            if is_guide and published_guides < MAX_GUIDES_PER_DAY:
                guide_data = guide_editor.write_guide(draft)
                if guide_data:
                    create_guide_post(guide_data, sync_slug, lang='ko')
                    create_guide_post(guide_data, sync_slug, lang='en') # 글로벌 지원
                    published_guides += 1
            
            # [V2.7.1 Fix] 중복 방지를 위한 History 기록
            for a in group: history.add_to_history(a['url'], a['title'])
            
            cat_issued[cat] += 1; published_count += 1
            published_urls.append(f"https://news.lego-sia.com/posts/{datetime.now().strftime('%Y/%m')}/{sync_slug}/")

    save_queue(next_cycle_queue)
    if published_count > 0:
        notify_indexnow(published_urls) # [V2.7.1 Fix] 색인 서비스 활성화
        telegram.send_resp(f"🚀 V2.7.1 정밀 수술 완료\n- 발행: {published_count}\n- 가이드: {published_guides}\n- 대기: {len(next_cycle_queue)}")

if __name__ == "__main__": main()
