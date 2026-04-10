import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class NewsHarvester:
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_ORG_KEY")
        self.thenewsapi_key = os.getenv("THENEWSAPI_KEY")
        self.currents_key = os.getenv("CURRENTSAPI_KEY")

    def fetch_all(self, limit_per_api=50):
        # [V3.7] 안정성 강화: 쿼리를 쪼개서 개별적으로 요청 (에러 방지)
        target_keywords = ["NVIDIA", "AI Tech", "RTX 5090", "HBM4", "Nintendo Switch 2", "AI SaaS"]
        print(f"[*] Multi-Query Harvest Level 2...")
        
        results = []
        
        # GNews (가장 안정적)
        for kw in target_keywords[:3]:
            try:
                url = f"https://gnews.io/api/v4/search?q={kw}&lang=en&token={self.gnews_key}&max=10"
                res = requests.get(url, timeout=10).json()
                if "articles" in res:
                    for i in res["articles"]:
                        results.append({"title": i["title"], "url": i["url"], "source": i["source"]["name"], "urlToImage": i.get("image")})
            except: pass

        # NewsAPI (상세 검색) - 가장 민감하므로 하나씩
        for kw in target_keywords[3:]:
            try:
                url = f"https://newsapi.org/v2/everything?q={kw}&language=en&apiKey={self.newsapi_key}&pageSize=10"
                res = requests.get(url, timeout=10).json()
                if "articles" in res:
                    for i in res["articles"]:
                        results.append({"title": i["title"], "url": i["url"], "source": i["source"]["name"], "urlToImage": i.get("urlToImage")})
            except: pass

        seen = set()
        unique = []
        for n in results:
            if n["url"] not in seen:
                if not n.get("urlToImage"):
                    n["urlToImage"] = "https://source.unsplash.com/featured/?technology"
                unique.append(n)
                seen.add(n["url"])
        
        print(f"[SUCCESS] Total {len(unique)} candidate articles collected.")
        return unique
