# -*- coding: utf-8 -*-
import os
import requests
import time
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

class NewsHarvester:
    def __init__(self, test_mode=False):
        self.keys = {
            "gnews": os.getenv("GNEWS_API_KEY"),
            "newsapi": os.getenv("NEWSAPI_ORG_KEY"),
            "thenewsapi": os.getenv("THENEWSAPI_KEY"),
            "currents": os.getenv("CURRENTSAPI_KEY")
        }
        self.test_mode = test_mode
        self.rotation_list = ["NewsAPI", "GNews", "TheNewsAPI"]
        
        # [V10.0] 2026년 4월 현재 메가 트렌드 키워드로 업데이트
        self.categories_config = {
            "ai_tech": {"query": "Latest AI breakthroughs 2026 NLP Vision models LLM innovation", "kor_name": "AI-기술"},
            "ai_agent": {"query": "AI agent tools autonomous workflows AI automation productivity", "kor_name": "AI-에이전트"},
            "hardware": {"query": "New computer hardware 2026 GPU CPU storage tech gadgets", "kor_name": "하드웨어"},
            "game": {"query": "Latest video games 2026 console news gaming industry updates", "kor_name": "게임"},
            "business": {"query": "Tech business news 2026 startup funding investment trends", "kor_name": "수익화-전략"},
            "tech_biz": {"query": "Global technology policy regulation market competition 2026", "kor_name": "테크-비즈니스"}
        }

    def _normalize(self, raw, source_api, kor_name):
        title = raw.get("title") or "Untitled Article"
        image = raw.get("urlToImage") or raw.get("image") or raw.get("image_url") or ""
        desc = raw.get("description") or raw.get("snippet") or raw.get("content", "")
        url = raw.get("url") or ""
        source = raw.get("source", {}).get("name") if isinstance(raw.get("source"), dict) else raw.get("source", source_api)

        return {
            "title": title,
            "description": desc,
            "urlToImage": image,
            "url": url,
            "source": source,
            "category": kor_name  # 저장할 때는 한글 이름으로 전달
        }

    def _fetch_currents(self, query, kor_name, limit):
        """CurrentsAPI V2: 가장 성공률이 높은 latest-news 엔드포인트 활용"""
        # [V5.7.1] V2 Canonical Taxonomy 직접 매칭
        # [V6.5] 사용자 취향 저격 카테고리 (불필요한 라이프/건축 제거 및 게임 강화)
        cur_cat_map = {
            "ai_tech": "science_technology",
            "ai_agent": "science_technology",
            "hardware": "science_technology",
            "game": "arts_culture_entertainment",
            "business": "economy_business_finance",
            "tech_biz": "economy_business_finance"
        }
        # 현재 처리 중인 영문 키(internal_key)를 어떻게 찾을까? 
        # kor_name으로 역추적하거나, fetch_all에서 key를 넘겨받도록 수정
        target_cat = "science_technology" # 기본값
        for ik, cfg in self.categories_config.items():
            if cfg["kor_name"] == kor_name:
                target_cat = cur_cat_map.get(ik, "general")
                break

        url = f"https://api.currentsapi.services/v2/latest-news?apiKey={self.keys['currents']}&category={target_cat}&language=en"
        try:
            res = requests.get(url, timeout=10).json()
            return [self._normalize(a, "Currents-V2", kor_name) for a in res.get("news", [])[:limit]]
        except: return []

    def _fetch_gnews(self, query, kor_name, limit):
        url = f"https://gnews.io/api/v4/search?q={query.split(' ')[0]}&lang=en&max={limit}&token={self.keys['gnews']}"
        try:
            res = requests.get(url, timeout=10).json()
            return [self._normalize(a, "GNews", kor_name) for a in res.get("articles", [])]
        except: return []

    def _fetch_newsapi(self, query, kor_name, limit):
        # [V10.1] 시간대에 따른 정렬 기준 동적 변경 (인기 vs 최신)
        hour = datetime.now().hour
        sort_by = "popularity" if (8 <= hour <= 10 or 17 <= hour <= 19) else "publishedAt"
        
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy={sort_by}&language=en&apiKey={self.keys['newsapi']}&pageSize={limit}"
        try:
            res = requests.get(url, timeout=10).json()
            return [self._normalize(a, "NewsAPI", kor_name) for a in res.get("articles", [])]
        except: return []

    def _fetch_thenewsapi(self, query, kor_name, limit):
        url = f"https://api.thenewsapi.com/v1/news/all?api_token={self.keys['thenewsapi']}&categories=tech&language=en&limit={limit}"
        try:
            res = requests.get(url, timeout=10).json()
            return [self._normalize(a, "TheNewsAPI", kor_name) for a in res.get("data", [])]
        except: return []

    def _fetch_kr_rss(self):
        """국내 IT 이슈 수집 (ITWorld Korea RSS)"""
        rss_url = "https://www.itworld.co.kr/rss/feed/index.php"
        articles = []
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:10]:
                articles.append(self._normalize({
                    "title": entry.title,
                    "description": entry.get('summary', ''),
                    "url": entry.link,
                    "urlToImage": None, 
                    "publishedAt": entry.get('published', datetime.now().isoformat())
                }, "ITWorld-KR", "테크-비즈니스"))
        except Exception as e:
            print(f" [!] KR RSS fetch failed: {e}")
        return articles

    def fetch_all(self, limit_per_cat=5):
        all_unique_news = []
        seen_urls = set()
        hour = datetime.now().hour
        current_main = self.rotation_list[hour % 3]

        for internal_key, config in self.categories_config.items():
            kor_name = config["kor_name"]
            query = config["query"]
            
            print(f"[*] Processing: {kor_name} ({internal_key})")
            cat_results = []
            
            if self.test_mode:
                print(f"    [!] MODE: Test Only (CurrentsAPI)")
                cat_results = self._fetch_currents(query, kor_name, 5)
            else:
                print(f"    [+] MODE: Production (Full API Refill - 5 items each)")
                # [V10.2] 모든 API 소스에서 각각 5개씩 수집 (인기 기사 집중 확보)
                cat_results += self._fetch_newsapi(query, kor_name, limit_per_cat)
                cat_results += self._fetch_gnews(query, kor_name, limit_per_cat)
                cat_results += self._fetch_thenewsapi(query, kor_name, limit_per_cat)
                cat_results += self._fetch_currents(query, kor_name, limit_per_cat)
                # [V10.6] 국내 RSS 통합
                cat_results += self._fetch_kr_rss()

            for article in cat_results:
                if article["url"] and article["url"] not in seen_urls:
                    all_unique_news.append(article)
                    seen_urls.add(article["url"])
            
            print(f"    [V] Added {len(cat_results)} articles.")
            time.sleep(2)

        return all_unique_news
