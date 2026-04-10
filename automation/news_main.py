import os
import time
import sys
import glob
from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from history_manager import HistoryManager
from telegram_notifier import TelegramNotifier
from gatekeeper import FinalGatekeeper

def count_all_posts():
    """블로그 내의 전체 마크다운 포스트 개수 계산"""
    posts = glob.glob("content/posts/**/*.md", recursive=True)
    # _index.md 같은 설정 파일 제외
    valid_posts = [p for p in posts if "_index" not in p]
    return len(valid_posts)

def create_hugo_post(article):
    """최종 선정된 뉴스를 Hugo 포스팅으로 생성"""
    path = "content/posts/news" 
    os.makedirs(path, exist_ok=True)
    
    clean_desc = article['summary'][:150].replace('\n', ' ')
    filename = f"news-{int(time.time())}.md"
    content = f"""---
title: "{article['title']}"
date: "{time.strftime('%Y-%m-%dT%H:%M:%S+09:00')}"
description: "{clean_desc}"
categories: ["AI·뉴스"]
tags: ["{article['source']}", "2026", "테크"]
image: "{article['urlToImage']}"
---

### 📡 AI 전문 편집장 3줄 요약

{article['summary']}

---

**[원본 기사 보기]({article['url']})**
"""
    with open(f"{path}/{filename}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCCESS] Draft: {article['title']}")

def main():
    is_night_mode = "--night" in sys.argv
    article_limit = 50 if is_night_mode else 20
    harvest_limit = 50 if is_night_mode else 5
    
    harvester = NewsHarvester()
    editor = NewsEditor()
    history = HistoryManager()
    gatekeeper = FinalGatekeeper()
    notifier = TelegramNotifier()
    
    print(f"=== [V4.8] News Hub Starting (Total Post Tracking) ===")
    
    # 1. 뉴스 수집
    new_raw_news = harvester.fetch_all(limit_per_api=harvest_limit)
    
    # 2. 중복 처리
    new_articles = []
    seen_urls = set()
    for article in new_raw_news:
        url = article['url']
        if url not in seen_urls and not history.is_already_processed(url):
            new_articles.append(article)
            seen_urls.add(url)
    
    # 3. AI 편집
    high_value_news = []
    if new_articles:
        new_articles = new_articles[:article_limit]
        batch_size = 10
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i : i + batch_size]
            reviews = editor.review_batch(batch)
            for rev in reviews:
                idx = rev.get('index')
                if idx is not None and isinstance(idx, int) and idx < len(batch):
                    score = rev.get('score', 0)
                    if score >= 7:
                        art = batch[idx]
                        art['summary'] = rev.get('summary', '요약 실패')
                        create_hugo_post(art)
                        history.add_to_history(art['url'], art['title'])
                        high_value_news.append(art)
            if i + batch_size < len(new_articles): time.sleep(5)
            
    # 4. 최종 검증 및 마이그레이션
    if high_value_news:
        gatekeeper.audit_and_migrate()

    # 5. 빌드 및 배포
    if is_night_mode and high_value_news:
        os.system(f"powershell -Command \"& C:\\hugo_tmp\\hugo.exe --gc --cleanDestinationDir; git add .; git commit -m 'Auto Harvest'; git push origin main\"")

    # 6. 알림 (실제 숫자 카운트 반영)
    total_posts = count_all_posts()
    mode_str = f"새벽 정규 수집({time.strftime('%H:%M')})" if is_night_mode else "주간 수동 원격 제어"
    msg = f"🛡️ **[{mode_str}] 작업완료**\n\n- 신규 발행 기사: {len(high_value_news)}건\n- 수집 후보: {len(new_articles)}건 중 선별\n- **현재 블로그 총 글수: {total_posts}개** 🏛️\n\nLego-sia 사옥의 질서가 유지되었습니다. 🛰️"
    notifier.send_message(msg)

if __name__ == "__main__":
    main()
