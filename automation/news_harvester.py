import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# [V4.0] 환경변수 완벽 가시성 로직 (Relative Path)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class NewsHarvester:
    def __init__(self):
        # API 키 로드
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_ORG_KEY")
        self.thenewsapi_key = os.getenv("THENEWSAPI_KEY")
        self.currents_key = os.getenv("CURRENTSAPI_KEY")

    def fetch_all(self):
        print(f"[*] Starting Global News Harvest (2026 Strategy)...")
        results = []
        
        # 1. GNews (Global Focus)
        try:
            url = f"https://gnews.io/api/v4/search?q=AI OR NVIDIA Rubin OR GPT-6&lang=en&token={self.gnews_key}&max=10"
            res = requests.get(url, timeout=10).json()
            for i in res.get("articles", []):
                results.append({"title": i["title"], "url": i["url"], "source": i["source"]["name"], "urlToImage": i.get("image")})
        except: pass

        # 2. NewsAPI (Technology Focus)
        try:
            url = f"https://newsapi.org/v2/everything?q=AIGC OR Semiconductor&language=en&apiKey={self.newsapi_org_key if hasattr(self, 'newsapi_org_key') else self.newsapi_key}&pageSize=10"
            res = requests.get(url, timeout=10).json()
            for i in res.get("articles", []):
                results.append({"title": i["title"], "url": i["url"], "source": i["source"]["name"], "urlToImage": i.get("urlToImage")})
        except: pass

        # 3. Currents API (Diversity Focus)
        try:
            url = f"https://api.currentsapi.services/v1/search?apiKey={self.currents_key}&keywords=Artificial Intelligence&language=en&limit=10"
            res = requests.get(url, timeout=10).json()
            for i in res.get("news", []):
                results.append({"title": i["title"], "url": i["url"], "source": i["author"], "urlToImage": i.get("image")})
        except: pass

        # 중복 제거
        seen = set()
        unique = []
        for n in results:
            if n["url"] not in seen:
                unique.append(n)
                seen.add(n["url"])
        
        print(f"[SUCCESS] Harvested {len(unique)} global articles via 2026 Pipeline.")
        return unique
