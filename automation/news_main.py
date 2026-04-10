import os
import time
from datetime import datetime
from news_harvester import NewsHarvester
from ai_news_editor import NewsEditor
from history_manager import HistoryManager

class NewsHub:
    def __init__(self):
        self.harvester = NewsHarvester()
        self.editor = NewsEditor()
        self.history = HistoryManager()

    def run_update(self):
        """뉴스 자동 큐레이션 실행 루틴"""
        print(f"[{datetime.now()}] Starting News Hub Update...")
        
        # 1. 뉴스 수집
        all_articles = self.harvester.fetch_all()
        processed_count = 0

        for article in all_articles:
            # 2. 중복 확인
            if self.history.is_already_processed(article['url']):
                continue
            
            # 3. AI 검토 (점수 및 요약)
            review = self.editor.review_article(article)
            if not review or review.get("score", 0) < 7:
                print(f"[-] Skipped: Low score or error. ({article['title'][:20]})")
                self.history.add_to_history(article['url'], article['title']) # 저퀄리티도 중복 방지 위해 등록
                continue

            # 4. 휴고 마크다운 생성
            self.create_hugo_post(article, review)
            self.history.add_to_history(article['url'], article['title'])
            processed_count += 1
            
            # API 쿼터 보호를 위한 30초 대기
            print(f"[+] Post Created: {article['title'][:30]}")
            time.sleep(30)
            
            # 무리해서 많이 뽑지는 않기 (하루 10-20개 적정)
            if processed_count >= 15: break

        print(f"[*] Update Complete. {processed_count} new articles posted.")

    def create_hugo_post(self, article, review):
        """휴고 규격에 맞춘 포스팅 생성"""
        # 영문 슬러그 생성 (간단히 타임스탬프 활용)
        file_name = f"news-{int(time.time())}.md"
        
        cat = "AI·신기술" if "AI" in article['title'] or "Tech" in article['title'] else "IT 소식"
        
        md_content = f"""---
title: "{article['title']}"
date: "{datetime.now().isoformat()}"
description: "{article['title']}"
featured_image: "{article['image'] if article['image'] else '/images/default-news.png'}"
categories: ["{cat}"]
tags: ["IT뉴스", "최신기술", "게임소식"]
source_url: "{article['url']}"
source_name: "{article['source']}"
---

### 📰 뉴스 요약
{review['summary']}

---

### 🔗 상세 내용 보기
이 뉴스의 더 자세한 내용은 아래 원문 링크에서 확인하실 수 있습니다.

**출처: [{article['source']}]**
[원문 바로가기]({article['url']})
"""
        # posts/ai-tech 폴더로 저장
        target_path = os.path.join("content", "posts", "ai-tech", file_name)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(md_content)

if __name__ == "__main__":
    hub = NewsHub()
    hub.run_update()
