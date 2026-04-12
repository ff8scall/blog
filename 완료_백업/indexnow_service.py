import requests
import json

def notify_indexnow(urls):
    """
    Search engines(Bing, Naver 등)에 새 URL 생성을 알림.
    """
    if not urls:
        return
    
    host = "news.lego-sia.com"
    key = "bbd0d9a6843c450eb3e9d811a0fd504a"
    key_location = f"https://{host}/{key}.txt"
    
    # 주요 IndexNow 지원 엔드포인트
    endpoints = [
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow"
    ]
    
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls
    }

    print(f" [*] Sending {len(urls)} URLs to IndexNow...")
    
    for endpoint in endpoints:
        try:
            res = requests.post(endpoint, json=payload, timeout=10)
            if res.status_code == 200:
                print(f" [SUCCESS] Indexed at {endpoint}")
            else:
                print(f" [!] {endpoint} returned status {res.status_code}")
        except Exception as e:
            print(f" [ERROR] Could not notify {endpoint}: {e}")

if __name__ == "__main__":
    # Test call
    test_urls = ["https://news.lego-sia.com/posts/2026/04/test-article/"]
    notify_indexnow(test_urls)
