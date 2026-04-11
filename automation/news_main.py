import os
import time
import sys
import json
import re
import glob
import random
from datetime import datetime
from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from history_manager import HistoryManager
from indexnow_service import notify_indexnow

import requests

def download_image(original_url, category_slug, slug):
    """
    1차: 원본 뉴스 이미지 시도
    2차: 실패 시 카테고리별 전용 폴백 이미지 사용
    3차: 최후 수단으로 AI 생성 시도
    """
    save_path = os.path.join("static", "images", f"{slug}.jpg")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # [1단계] 원본 원고 이미지 시도
    if original_url and original_url.startswith("http"):
        try:
            print(f" [*] Attempting to download original image: {original_url[:50]}...")
            response = requests.get(original_url, timeout=10)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return f"/images/{slug}.jpg"
        except Exception as e:
            print(f" [!] Original image download failed: {e}")

    # [2단계] 카테고리별 폴백 이미지 (단, 파일이 실제 존재할 때만)
    fallback_path = f"static/images/fallbacks/{category_slug}.jpg"
    if os.path.exists(fallback_path):
        return f"/images/fallbacks/{category_slug}.jpg"

    # [3단계] AI 생성 (Pollinations AI)
    try:
        seed_val = sum(ord(c) for c in slug) % 1000000
        prompt = f"Futuristic technology concept for {category_slug}"
        ai_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=720&nologo=true&seed={seed_val}"
        response = requests.get(ai_url, timeout=20)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return f"/images/{slug}.jpg"
    except:
        pass

    return "/images/fallback-default.jpg"

def sanitize_slug(title):
    """영문 제목을 기반으로 URL 친화적인 파일명 생성"""
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    return re.sub(r'\s+', '-', clean).strip('-')[:50]

def create_hugo_post(article, lang='ko'):
    """[V10.1] 날짜별 폴더 구조(YYYY/MM) 및 고도화된 저장 로직"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    # 1. 언어별/날짜별 경로 설정 (구조적 관리)
    base_path = f"content/{lang}/posts/{year}/{month}"
    os.makedirs(base_path, exist_ok=True)
    
    # 2. 파일명 (영문 슬러그 공유)
    slug = sanitize_slug(article['eng_title'])
    timestamp = int(time.time())
    md_filename = f"{slug}-{timestamp}.md"
    
    # 3. 이미지 영구 저장 (V7.2)
    original_img = article.get('original_image_url')
    cat_slug = article.get('eng_category_slug', 'tech-biz')
    local_img_url = download_image(original_img, cat_slug, slug)
    
    # 4. 언어별 원고 구성
    cat_slug = article.get('eng_category_slug', 'tech-biz')
    tags = json.dumps(article.get('keywords', []), ensure_ascii=False)
    is_featured = "true" if article.get('score', 0) >= 9 else "false"
    
    if lang == 'ko':
        title = article['kor_title']
        summary_first_line = article.get('kor_summary', '').split('\n')[0][:100]
        content = f"""---
title: "{title}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{summary_first_line}"
image: "{local_img_url}"
categories: ["{cat_slug}"]
tags: {tags}
featured: {is_featured}
---

## 📋 Executive Summary: 핵심 이슈 브리핑

{article.get('kor_summary', '내용 요약 중...')}

---

## 🔍 심층 분석: 글로벌 테크 리포트

{article.get('kor_content', '진행 중...')}

---

## 💡 Editorial: 미래 전략과 시장 전망

{article.get('kor_insight', '인사이트 분석 중...')}
"""
    else: # English
        title = article['eng_title']
        eng_desc = article.get('eng_content', '')[:150].replace('"', "'")
        content = f"""---
title: "{title}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{eng_desc}..."
image: "{local_img_url}"
categories: ["{cat_slug}"]
tags: {tags}
featured: {is_featured}
---

{article.get('eng_content', 'Processing...')}

---
*Published by Lego-Sia Intelligence (V10.0)*
"""

    with open(f"{base_path}/{md_filename}", "w", encoding="utf-8-sig") as f:
        f.write(content)
    
    return md_filename

def save_raw_archive(article, slug):
    """API 원본 데이터를 배포되지 않는 별도 폴더에 JSON으로 영구 보관"""
    archive_dir = "automation/raw_archive"
    os.makedirs(archive_dir, exist_ok=True)
    
    archive_path = os.path.join(archive_dir, f"{slug}.json")
    try:
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f" [!] Raw archive save failed: {e}")

def main():
    print(f"=== [V10.0 Global] April 2026 Strategy Engine Starting ===")
    
    harvester = NewsHarvester()
    editor = NewsEditor()
    history = HistoryManager()
    
    # 1. 뉴스 수집 (중복 기사 필터링 포함)
    raw_news = harvester.fetch_all(limit_per_cat=5)
    
    # 2. 중복 처리 강화 (DB 대조 + 실시간 배치 내 전수 조사)
    new_articles = []
    seen_titles = [] 
    published_urls = [] # [V10.5] 검색 색인용 URL 리스트
    
    for article in raw_news:
        url = article['url']
        title = article['title']
        
        # [V10.3] 하이브리드 중복 차단
        is_duplicate = False
        
        # 1) 히스토리 DB 대조 (문맥 유사도 0.5 이상 컷)
        if history.is_already_processed(url) or history.is_similar_title_exists(title, threshold=0.5):
            is_duplicate = True
        
        # 2) 현재 작업 리스트 내 근접 중복 검사 (앞부분 일치 검사 추가)
        for seen_title in seen_titles:
            # 제목 앞부분 15자 중 12자 이상이 겹치면 동일 사건으로 간주
            if title[:15] == seen_title[:15]:
                is_duplicate = True
                break
        
        if not is_duplicate:
            new_articles.append(article)
            seen_titles.append(title)
        else:
            continue
    
    if not new_articles:
        print("[*] No unique news found in this cycle. Keeping existing archive.")
        return

    # 3. AI 2-Step Editorial (Expansion Mode + Category Balancing)
    print(f"[*] Deep-Editing {len(new_articles)} fresh articles with Priority...")
    
    # [V10.4] 우선순위 카테고리 관리
    priority_order = ["ai-tech", "ai-agents", "hardware", "game"]
    category_quota = {"tech-biz": 2, "monetization": 3} # 과밀 카테고리 제한
    current_counts = {}

    # 우선순위대로 정렬하여 추출
    sorted_articles = sorted(new_articles, key=lambda x: 0 if any(k in x['category'].lower() or k in x['title'].lower() for k in ["ai", "chip", "hardware", "game"]) else 1)
    
    for article in sorted_articles:
        reviews = editor.review_batch([article])
        for rev in reviews:
            # 카테고리 매핑 및 정원 체크
            cat_map = {
                "AI-기술": "ai-tech", "AI-에이전트": "ai-agents", "하드웨어": "hardware",
                "게임": "game", "수익화-전략": "monetization", "테크-비즈니스": "tech-biz"
            }
            cat_slug = cat_map.get(rev.get('category', 'tech-biz'), 'tech-biz')
            rev['eng_category_slug'] = cat_slug
            
            # [V10.4] 쿼터제 적용: 테크-비즈니스 등이 이미 찼으면 스킵
            count = current_counts.get(cat_slug, 0)
            if cat_slug in category_quota and count >= category_quota[cat_slug]:
                # print(f" [QUOTA FULL] Skipping {cat_slug}: {rev['kor_title'][:30]}")
                continue

            if rev.get('score', 0) >= 8: # 품질 하한선 8점으로 상향
                post_slug = sanitize_slug(rev['eng_title'])
                save_raw_archive(article, post_slug)
                
                # [V10.5] 파일명과 날짜 기반 URL 추출
                now = datetime.now()
                url_path = f"posts/{now.strftime('%Y/%m')}/{post_slug}/"
                
                ko_file = create_hugo_post(rev, lang='ko')
                en_file = create_hugo_post(rev, lang='en')
                
                published_urls.append(f"https://news.lego-sia.com/{url_path}")
                published_urls.append(f"https://news.lego-sia.com/en/{url_path}")
                
                history.add_to_history(article['url'], rev['kor_title'])
                current_counts[cat_slug] = count + 1 # 카운트 증가
                print(f" [SUCCESS] Priority Added [{cat_slug}]: {rev['kor_title']}")

    # [V10.5] 검색 엔진 색인 알림 실행
    if published_urls:
        notify_indexnow(published_urls)

    print(f"[*] Global Update Complete. Archive Updated.")

if __name__ == "__main__":
    main()
