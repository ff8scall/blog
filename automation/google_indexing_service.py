import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# 설정 로드
load_dotenv()

logger = logging.getLogger("LegoSia.GoogleIndexing")

def notify_google_indexing(urls, action="URL_UPDATED"):
    """
    Google Indexing API를 호출하여 URL 색인을 요청합니다.
    action: "URL_UPDATED" (생성/수정) 또는 "URL_DELETED" (삭제)
    """
    if not urls:
        return

    # 1. JSON 키 파일 경로 (상대 경로로 설정)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    JSON_KEY_PATH = os.path.join(current_dir, "keys", "google_indexing_key.json")
    
    if not os.path.exists(JSON_KEY_PATH):
        logger.error(f"Google Indexing Key not found at {JSON_KEY_PATH}")
        print(f" [!] Google Indexing Key not found at {JSON_KEY_PATH}")
        return

    # 2. 인증 설정
    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    try:
        credentials = service_account.Credentials.from_service_account_file(
            JSON_KEY_PATH, scopes=SCOPES
        )
        # 3. 서비스 객체 빌드
        service = build("indexing", "v3", credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to initialize Google Indexing service: {e}")
        print(f" [ERROR] Google Indexing Init Failed: {e}")
        return

    print(f" [*] Notifying {len(urls)} URLs to Google Indexing API...")

    for url in urls:
        # 4. 요청 본문 작성
        body = {
            "url": url,
            "type": action
        }

        # 5. API 호출
        try:
            response = service.urlNotifications().publish(body=body).execute()
            url_res = response.get('urlNotificationMetadata', {}).get('latestUpdate', {}).get('url', url)
            print(f" [SUCCESS] Google Indexing accepted: {url_res}")
            logger.info(f"Google Indexing success: {url}")
        except Exception as e:
            print(f" [!] Google Indexing failed for {url}: {e}")
            logger.warning(f"Google Indexing failed for {url}: {e}")

if __name__ == "__main__":
    # 테스트 호출
    logging.basicConfig(level=logging.INFO)
    test_urls = ["https://news.lego-sia.com/posts/2026/04/test-article/"]
    notify_google_indexing(test_urls)
