import os
import requests
import logging
from dotenv import load_dotenv
from google_indexing_service import notify_google_indexing

load_dotenv()

logger = logging.getLogger("LegoSia.IndexNow")

def notify_indexnow(urls):
    """
    Search engines(Bing, Naver 등)에 새 URL 생성을 알림.
    [V1.3] Naver 통합 및 도메인별 키 지원
    """
    if not urls:
        return
    
    host = "news.lego-sia.com"
    bing_key = os.getenv("INDEXNOW_KEY_BING", "bbd0d9a6843c450eb3e9d811a0fd504a")
    naver_key = os.getenv("INDEXNOW_KEY_NAVER", "c3a4f8e21d6b4927a7c5b1e0d3f4a6b2")
    
    # 엔드포인트와 해당 엔진에서 사용할 키 매핑
    targets = [
        {"name": "Bing", "url": "https://www.bing.com/indexnow", "key": bing_key},
        {"name": "Naver", "url": "https://searchadvisor.naver.com/indexnow", "key": naver_key},
        {"name": "Yandex", "url": "https://yandex.com/indexnow", "key": bing_key},
        {"name": "IndexNow.org", "url": "https://api.indexnow.org/indexnow", "key": bing_key}
    ]
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/123.0.0.0"
    }

    print(f" [*] Notifying {len(urls)} URLs to IndexNow Engines...")
    
    for target in targets:
        payload = {
            "host": host,
            "key": target["key"],
            "urlList": urls
        }
        
        endpoint = target["url"]
        name = target["name"]
        
        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 202]:
                print(f" [SUCCESS] {name} accepted request (Status: {res.status_code})")
                logger.info(f"{name} success: {res.status_code}")
            else:
                print(f" [!] {name} ({endpoint}) returned status {res.status_code}")
                print(f" Response: {res.text}")
                logger.warning(f"{name} failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f" [ERROR] Could not notify {name}: {e}")
            logger.error(f"{name} error: {e}")
    
    # [V1.4] Google Indexing API 통합
    try:
        notify_google_indexing(urls)
    except Exception as e:
        print(f" [ERROR] Google Indexing notification failed: {e}")
        logger.error(f"Google Indexing error: {e}")

if __name__ == "__main__":
    # Test call
    logging.basicConfig(level=logging.INFO)
    test_urls = ["https://news.lego-sia.com/posts/2026/04/test-article/"]
    notify_indexnow(test_urls)

