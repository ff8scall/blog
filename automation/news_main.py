# -*- coding: utf-8 -*-
import os
import time
import sys
import json
import re
import glob
import random
from datetime import datetime

# [V12.0] 터미널 인코딩 및 출력 플러싱 최적화
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from history_manager import HistoryManager
from indexnow_service import notify_indexnow
from ai_reviewer import EditorInChief
from telegram_remote import TelegramRemote

import requests
import subprocess

def download_image(original_url, category_slug, slug):
    save_path = os.path.join("static", "images", f"{slug}.jpg")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if original_url and original_url.startswith("http"):
        try:
            print(f" [*] Attempting to download original image: {original_url[:50]}...")
            response = requests.get(original_url, timeout=12)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return f"/images/{slug}.jpg"
        except Exception as e:
            print(f" [!] Original image download failed: {e}")
    fallback_path = f"static/images/fallbacks/{category_slug}.jpg"
    if os.path.exists(fallback_path): return f"/images/fallbacks/{category_slug}.jpg"
    return "/images/fallback-default.jpg"

def sanitize_slug(title):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    return re.sub(r'\s+', '-', clean).strip('-')[:50]

def create_hugo_post(article, lang='ko'):
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    base_path = f"content/{lang}/posts/{year}/{month}"
    os.makedirs(base_path, exist_ok=True)
    slug = sanitize_slug(article['eng_title'])
    timestamp = int(time.time())
    md_filename = f"{slug}-{timestamp}.md"
    # [V12.1] 이미지 URL 추출 로직 강화 (다중 변수 체크)
    raw_img_url = article.get('original_image_url') or article.get('urlToImage') or article.get('image')
    local_img_url = download_image(raw_img_url, article.get('eng_category_slug', 'tech-biz'), slug)
    cat_slug = article.get('eng_category_slug', 'tech-biz')
    tags = json.dumps(article.get('keywords', []), ensure_ascii=False)
    is_featured = "true" if article.get('score', 0) >= 9 else "false"
    
    if lang == 'ko':
        title = article['kor_title']
        summary = article.get('kor_summary', '').split('\n')[0][:100]
        content = f"""---
title: "{title}"
date: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{summary}"
image: "{local_img_url}"
categories: ["{cat_slug}"]
tags: {tags}
featured: {is_featured}
---

## Executive Summary: 핵심 이슈 브리핑

{article.get('kor_summary', '내용 요약 중...')}

---

## Deep Analysis: 글로벌 테크 리포트

{article.get('kor_content', '진행 중...')}

---

## Editorial Outlook: 미래 전략과 시장 전망

{article.get('kor_insight', '인사이트 분석 중...')}
"""
    else:
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
*Published by Lego-Sia Intelligence (V12.0)*
"""
    with open(f"{base_path}/{md_filename}", "w", encoding="utf-8-sig") as f:
        f.write(content)
    return md_filename

def get_api_quotas():
    results = []
    keys = {
        "NEWSAPI_ORG_KEY": "NewsAPI", "THENEWSAPI_KEY": "TheNewsAPI", 
        "CURRENTSAPI_KEY": "CurrentsAPI", "GNEWS_API_KEY": "GNews",
        "NEWSDATA_API_KEY": "NewsData"
    }
    for k, name in keys.items():
        v = os.getenv(k)
        if v:
            try:
                if name == "NewsAPI": res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey={v}", timeout=5)
                elif name == "TheNewsAPI": res = requests.get(f"https://api.thenewsapi.com/v1/news/top?api_token={v}&limit=1", timeout=5)
                elif name == "GNews": res = requests.get(f"https://gnews.io/api/v4/top-headlines?token={v}&max=1", timeout=5)
                elif name == "NewsData": res = requests.get(f"https://newsdata.io/api/1/latest?apikey={v}&size=1", timeout=5)
                else: res = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={v}", timeout=5)
                rem = res.headers.get('X-Remaining-Quota') or res.headers.get('X-RateLimit-Remaining') or "OK"
                results.append(f"- {name}: {rem}")
            except: pass
    return "\n".join(results) if results else "No quota data available."

def group_articles_by_topic(articles, threshold=0.12):
    """[V15.0] 관련 기사들을 주제별로 그룹화 (글로벌-로컬 매칭용)"""
    groups = []
    used_indices = set()
    
    # 1. 기사들을 순회하며 유사한 기사들을 그룹화
    for i in range(len(articles)):
        if i in used_indices: continue
        
        current_group = [articles[i]]
        used_indices.add(i)
        
        # 제목에서 불용어 제외한 핵심 단어 추출 (매칭 정확도 향상)
        def get_keywords(text):
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'from', 'as', 'is', 'are', 'was', 'were', 'it', 'on', 'off', 'up', 'down'}
            words = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text).lower().split()
            return set([w for w in words if len(w) > 1 and w not in stop_words])
        
        keywords_i = get_keywords(articles[i]['title'])
        
        for j in range(i + 1, len(articles)):
            if j in used_indices: continue
            
            keywords_j = get_keywords(articles[j]['title'])
            if not keywords_i or not keywords_j: continue
            
            # Jaccard 유사도 계산
            intersection = keywords_i.intersection(keywords_j)
            union = keywords_i.union(keywords_j)
            similarity = len(intersection) / len(union)
            
            # 특정 브랜드(NVIDIA, Apple 등)가 공통으로 포함되면 가중치 부여
            brands = {'nvidia', 'apple', 'samsung', 'google', 'microsoft', 'meta', 'openai', 'tesla', 'intel', 'sk', 'hynix', 'tsmc'}
            common_brands = keywords_i.intersection(keywords_j).intersection(brands)
            
            if similarity >= threshold or common_brands:
                current_group.append(articles[j])
                used_indices.add(j)
                # 그룹 내 최대 기사 수는 2개로 제한 (글로벌 1 + 로컬 1 조합 선호)
                if len(current_group) >= 2: break
                
        groups.append(current_group)
    return groups

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Lego-Sia Strategic News Engine V15.0")
    parser.add_argument("--rss-only", action="store_true", help="Only fetch from RSS sources (Skip News APIs)")
    parser.add_argument("--limit", type=int, default=8, help="Limit articles per category")
    args = parser.parse_args()

    print(f"=== [V15.0 Hawk-Eye] Strategic Media Engine Initializing (Global-Local Matching Mode) ===")
    harvester = NewsHarvester()
    from ai_writer import AIWriter
    writer = AIWriter()
    editor = NewsEditor(writer=writer)
    history = HistoryManager()
    reviewer = EditorInChief(writer=writer) 
    telegram = TelegramRemote()
    
    raw_news, harvest_stats = harvester.fetch_all(limit_per_cat=args.limit, rss_only=args.rss_only) 
    new_articles = []
    seen_urls = set()

    for article in raw_news:
        url = article['url']
        title = article['title']
        if not history.is_already_processed(url) and not history.is_similar_title_exists(title):
            if url not in seen_urls:
                new_articles.append(article)
                seen_urls.add(url)
        else:
            print(f" [SKIP] Duplicate or similar found: {title[:30]}...")

    if not new_articles:
        print("[*] No unique news found. System on standby.")
        quota_report = get_api_quotas()
        telegram.send_resp(f"ℹ️ [SKIP] 새로운 뉴스가 없습니다.\n\n[수집통계]\n{json.dumps(harvest_stats, indent=2)}\n\n[QUOTA]\n{quota_report}")
        return

    # [V15.0] 글로벌-로컬 매칭을 위한 그룹화 단계
    article_groups = group_articles_by_topic(new_articles)
    print(f"[*] Grouping complete. {len(new_articles)} articles clustered into {len(article_groups)} topic blocks.")

    # AI/전략 기사 우선 정렬 (그룹의 첫 번째 기사 기준)
    sorted_groups = sorted(article_groups, key=lambda g: 0 if any(k in g[0]['title'].lower() for k in ["ai", "chip", "nvidia", "hardware", "semiconductor", "agent", "robot", "llm"]) else 1)

    published_count = 0
    published_urls = []

    # [V15.1] 내부 링크 및 컨텍스트를 위해 최근 기사 목록 획득
    recent_posts = history.get_recent_posts(limit=12)

    for group in sorted_groups:
        if writer.is_all_exhausted():
            print(" [CRITICAL] All AI Providers exhausted.")
            break

        # [V15.1] 그룹 단위로 에디터에게 전달 (최근 맥락 포함)
        drafts = editor.review_batch(group, recent_posts=recent_posts)
        if not drafts: continue
        
        for draft in drafts:
            raw_cat = draft.get('category', 'tech-biz')
            cat_map = {
                "ai-tech": "ai-tech", "AI Insight": "ai-tech", "AI-기술": "ai-tech",
                "ai-agents": "ai-agents", "AI Agents": "ai-agents", "AI-에이전트": "ai-agents",
                "hardware": "hardware", "Computing HW": "hardware", "하드웨어": "hardware",
                "game": "gaming", "Next-Gen Game": "gaming", "게임": "gaming",
                "monetization": "monetization", "Strategy & Biz": "monetization", "수익화-전략": "monetization",
                "tech-biz": "tech-biz", "Market Trend": "tech-biz", "테크-비즈니스": "tech-biz"
            }
            cat_slug = cat_map.get(raw_cat, "tech-biz")
            draft['eng_category_slug'] = cat_slug
            
            # [V12.0 Aggressive Mode] 카테고리별 티켓 체크 제거 - 점수(Score)가 높으면 무조건 발행
            review = reviewer.review_article(draft)
            if review.get('decision') != 'PASS':
                print(f" [REJECTED] {draft['kor_title'][:30]} - Reason: {review.get('reason', 'Low Score')}")
                continue

            if draft.get('score', 0) >= 7:
                post_slug = sanitize_slug(draft['eng_title'])
                url_path = f"posts/{datetime.now().strftime('%Y/%m')}/{post_slug}/"
                create_hugo_post(draft, lang='ko')
                create_hugo_post(draft, lang='en')
                published_urls.append(f"https://news.lego-sia.com/{url_path}")
                published_urls.append(f"https://news.lego-sia.com/en/{url_path}")
                history.add_to_history(article['url'], draft['kor_title'])
                published_count += 1
                print(f" [PUB] {draft['kor_title']} (Score: {draft.get('score')})")
            else:
                print(f" DEBUG: Score too low ({draft.get('score')}) for final publication.")

    # [V11.8] 기사 발행 여부와 상관없이 항상 상태 보고 수행
    print(f"[*] Dispatching final intelligence report... (Articles: {published_count})")
    try:
        quota_report = get_api_quotas()
        
        # 상세 리포트 구성
        h_detail = "\n".join([f"- {k}: {v}건" for k, v in harvest_stats.items()])
        total_h = sum(harvest_stats.values())
        
        # AI 사용량 통계 추가
        ai_usage = "\n".join([f"- {p.capitalize()}: {c}건" for p, c in writer.usage_stats.items() if c > 0])
        ai_fails = ", ".join(writer.failed_providers) if writer.failed_providers else "None"
        
        if published_count > 0:
            report_msg = f"✅ [STRATEGIC REPORT COMPLETE]\n\n" \
                         f"📦 [수집 통계]\n{h_detail}\n" \
                         f"📑 후보군: {total_h}건 -> 필터링: {len(new_articles)}건\n\n" \
                         f"🤖 [AI 작업 통계]\n{ai_usage}\n" \
                         f"⚠️ 소진된 API: {ai_fails}\n\n" \
                         f"🚀 [발행 규모]\n최종 발행: {published_count}건\n" \
                         f"성공률: {int(published_count/len(new_articles)*100)}%\n\n" \
                         f"[QUOTA]\n{quota_report}"
        else:
            report_msg = f"ℹ️ [SKIP] 새로운 뉴스가 없습니다.\n\n📦 [수집 통계]\n{h_detail}\n\n[QUOTA]\n{quota_report}"
            
        telegram.send_resp(report_msg)
        
        # 기사가 있을 때만 IndexNow 통보
        if published_urls:
            print(f" [*] Notifying IndexNow for {len(published_urls)} URLs...")
            notify_indexnow(published_urls)
            
    except Exception as e:
        print(f" [!] Report failed: {e}")

if __name__ == "__main__":
    telegram = TelegramRemote()
    try:
        # 1. 시작 알림
        telegram.send_resp("🚀 [Lego-Sia v12.0] Strategic News Engine 가동을 시작합니다.")
        main()
    except Exception as e:
        # 2. 에러 긴급 보고
        import traceback
        err_detail = traceback.format_exc()
        error_msg = f"⚠️ [CRITICAL ERROR] 엔진 가동 중단!\n\n원인: {str(e)}\n\n세부사항:\n{err_detail[:300]}..."
        print(error_msg)
        telegram.send_resp(error_msg)
        sys.exit(1)
