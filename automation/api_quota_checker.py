import os
import requests
import json
from dotenv import load_dotenv

# .env 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

def check_quotas():
    results = {}
    
    # 1. NewsAPI
    newsapi_key = os.getenv("NEWSAPI_ORG_KEY")
    if newsapi_key:
        try:
            res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey={newsapi_key}")
            # NewsAPI는 헤더에 남은 양을 실어 보내는 경우가 많음
            remaining = res.headers.get('X-Remaining-Quota') or res.headers.get('X-RateLimit-Remaining', "Unknown (Approx 100/day)")
            results["NewsAPI"] = f"{remaining} (Headers Check)"
        except: results["NewsAPI"] = "Failed to fetch"

    # 2. GNews
    gnews_key = os.getenv("GNEWS_API_KEY")
    if gnews_key:
        try:
            res = requests.get(f"https://gnews.io/api/v4/top-headlines?token={gnews_key}&max=1")
            # GNews는 보통 헤더에 남은 양을 명시적으로 주지 않는 경우가 있어 상태 코드로 추정
            if res.status_code == 200:
                results["GNews"] = "Active (Fixed limit 10/day for Free tier)"
            else:
                results["GNews"] = f"Error: {res.status_code}"
        except: results["GNews"] = "Failed to fetch"

    # 3. TheNewsAPI
    thenews_key = os.getenv("THENEWSAPI_KEY")
    if thenews_key:
        try:
            # TheNewsAPI는 헤더에 X-RateLimit-Remaining-Month 등을 포함함
            res = requests.get(f"https://api.thenewsapi.com/v1/news/top?api_token={thenews_key}&limit=1")
            remaining = res.headers.get('X-RateLimit-Remaining', "Unknown")
            results["TheNewsAPI"] = f"{remaining} units left"
        except: results["TheNewsAPI"] = "Failed to fetch"

    # 4. CurrentsAPI
    currents_key = os.getenv("CURRENTSAPI_KEY")
    if currents_key:
        try:
            res = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={currents_key}")
            # CurrentsAPI는 헤더 확인
            remaining = res.headers.get('X-RateLimit-Remaining', "Unknown")
            results["CurrentsAPI"] = f"{remaining} calls left"
        except: results["CurrentsAPI"] = "Failed to fetch"

    return results

if __name__ == "__main__":
    print("\n[CHECK] Checking API Quotas for Lego-Sia Intelligence...")
    quotas = check_quotas()
    for api, status in quotas.items():
        print(f" - {api}: {status}")
