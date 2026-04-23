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
    [V1.5] Streaming Mode 전환: 개별 URL 통보로 검색 엔진 부하 최적화
    """
    if not urls:
        return
    
    # 중복 제거
    urls = list(set(urls))
    
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/123.0.0.0"
    }

    print(f" [*] Streaming {len(urls)} URLs to IndexNow Engines...")
    
    for url in urls:
        for target in targets:
            name = target["name"]
            # [STREAMING MODE] GET 요청 사용
            params = {
                "url": url,
                "key": target["key"]
            }
            
            try:
                # 스트리밍 방식은 GET 요청이 표준이며 부하가 적음
                res = requests.get(target["url"], params=params, headers=headers, timeout=10)
                if res.status_code in [200, 202]:
                    logger.info(f"{name} streaming success: {url} ({res.status_code})")
                else:
                    print(f" [!] {name} streaming failed for {url}: {res.status_code}")
                    logger.warning(f"{name} streaming failed: {res.status_code} - {url}")
            except Exception as e:
                logger.error(f"{name} streaming error: {e}")
    
    print(f" [OK] IndexNow streaming notification completed.")
    
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

