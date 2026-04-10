import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class NewsHarvester:
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_ORG_KEY")
        self.thenewsapi_key = os.getenv("THENEWSAPI_KEY")
        self.currents_key = os.getenv("CURRENTSAPI_KEY")

    def _get_og_image(self, url):
        """API 이미지 누락 시 원문 og:image 스캔 (Fallback)"""
        try:
            res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            meta = soup.find("meta", property="og:image")
            return meta["content"] if meta else None
        except:
            return None

    def fetch_gnews(self, query="IT Tech AI Gaming"):
        """GNews API 호출 (일 100회)"""
        url = f"https://gnews.io/api/v4/search?q={query}&lang=ko&token={self.gnews_key}"
        try:
            res = requests.get(url).json()
            articles = []
            for item in res.get("articles", []):
                img = item.get("image") or self._get_og_image(item["url"])
                articles.append({
                    "title": item["title"],
                    "url": item["url"],
                    "source": item["source"]["name"],
                    "image": img,
                    "published": item["publishedAt"]
                })
            return articles
        except: return []

    def fetch_newsapi(self, query="technology OR gaming"):
        """NewsAPI.org 호출 (일 100회)"""
        url = f"https://newsapi.org/v2/everything?q={query}&language=ko&apiKey={self.newsapi_key}"
        try:
            res = requests.get(url).json()
            articles = []
            for item in res.get("articles", []):
                img = item.get("urlToImage") or self._get_og_image(item["url"])
                articles.append({
                    "title": item["title"],
                    "url": item["url"],
                    "source": item["source"]["name"],
                    "image": img,
                    "published": item["publishedAt"]
                })
            return articles
        except: return []

    def fetch_thenewsapi(self, query="tech"):
        """TheNewsAPI 호출 (일 100회)"""
        url = f"https://api.thenewsapi.com/v1/news/all?api_token={self.thenewsapi_key}&search={query}&language=ko"
        try:
            res = requests.get(url).json()
            articles = []
            for item in res.get("data", []):
                img = item.get("image_url") or self._get_og_image(item["url"])
                articles.append({
                    "title": item["title"],
                    "url": item["url"],
                    "source": item["source"],
                    "image": img,
                    "published": item["published_at"]
                })
            return articles
        except: return []

    def fetch_currentsapi(self, query="IT AI Gaming"):
        """Currents API 호출 (일 600회 - 넉넉!)"""
        url = f"https://api.currentsapi.services/v1/search?apiKey={self.currents_key}&keywords={query}&language=ko"
        try:
            res = requests.get(url).json()
            articles = []
            for item in res.get("news", []):
                img = item.get("image") or self._get_og_image(item["url"])
                articles.append({
                    "title": item["title"],
                    "url": item["url"],
                    "source": item["author"], # Currents는 source명이 author로 나올 때가 많음
                    "image": img,
                    "published": item["published"]
                })
            return articles
        except: return []

    def fetch_all(self):
        """4대 천왕 종합 수집기 (중복 제거)"""
        print("[*] Harvesting news from all 4 sources...")
        all_news = self.fetch_gnews() + self.fetch_newsapi() + self.fetch_thenewsapi() + self.fetch_currentsapi()
        
        # 중복 제거 (URL 기준)
        seen = set()
        unique_news = []
        for n in all_news:
            if n["url"] not in seen:
                unique_news.append(n)
                seen.add(n["url"])
        print(f"[SUCCESS] Harvested {len(unique_news)} unique articles.")
        return unique_news
