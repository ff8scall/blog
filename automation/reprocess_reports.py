import os
import logging
from datetime import datetime

# [V1.1] 긴급 환경 대응: 특정 파이썬 환경에서 dotenv가 없을 경우 대비
try:
    import news_main as nm
except ImportError:
    # news_main.py 내부의 from dotenv import load_dotenv가 실패할 경우
    # 직접 가짜 nm 객체를 만들거나, news_main.py를 임포트하기 전 패치를 시도
    import sys
    from unittest.mock import MagicMock
    sys.modules["dotenv"] = MagicMock()
    import news_main as nm

from nlm_parser import parse_structured_articles, parse_editorial_markdown
from image_manager import get_tiered_image
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Reprocessor")

REPORTS_DIR = "scratch/premium_reports"
OUTPUT_KO = "content/ko/posts"

def reprocess_article(article):
    """단일 기사를 강제로 재발행 (덮어쓰기 보장)"""
    # 1. 슬러그 생성 로직 (notebooklm_publisher와 동일)
    raw_title = article.get("eng_title") or article.get("kor_title") or f"Article {article.get('id', 'Unknown')}"
    cluster = article.get("cluster", "tech")
    raw_slug = nm.sanitize_slug(raw_title)
    
    if raw_slug and not raw_slug.isdigit():
        slug = f"{cluster}-{raw_slug}"[:50].strip('-')
    else:
        article_id = str(article.get("id", "0")).zfill(2)
        category = article.get("category", "news")
        slug = f"{cluster}-{category}-{article_id}"
    
    article["sync_slug"] = slug
    article["original_url"] = article.get("original_url", "")
    article["original_image_url"] = article.get("original_image")
    article["source_name"] = "NotebookLM Premium (Reprocessed)"
    
    # 2. 이미지 폴백/생성 로직
    # 기존 이미지가 깨졌을 가능성이 높으므로 강제로 다시 매핑 시도
    img_url = get_tiered_image(article, slug)
    article["thumbnail_image"] = img_url
    
    # 3. 발행 (덮어쓰기 방해되는 체크 없음)
    try:
        nm.create_hugo_post(article, lang='ko')
        nm.create_hugo_post(article, lang='en')
        logger.info(f" [OK] Force Published: {slug}")
        return True
    except Exception as e:
        logger.error(f" [FAIL] Failed to reprocess {slug}: {e}")
        return False

def main():
    if not os.path.exists(REPORTS_DIR):
        logger.error(f"Reports directory not found: {REPORTS_DIR}")
        return

    logger.info("Starting emergency reprocessing of NLM reports...")
    
    report_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith("_report.md")]
    total_processed = 0

    for filename in report_files:
        filepath = os.path.join(REPORTS_DIR, filename)
        logger.info(f"Processing report file: {filename}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Mode B(구조화 데이터)로 가정하고 파싱 시도 (대부분의 문제가 여기서 발생)
        articles = parse_structured_articles(content)
        
        if not articles:
            # Mode A(사설)일 가능성 체크
            logger.info(f" No structured articles in {filename}, trying Mode A...")
            parts = filename.split("_")
            cat = parts[0] if parts else "general"
            article = parse_editorial_markdown(content, category=cat)
            if article:
                articles = [article]
        
        if not articles:
            logger.warning(f" Could not parse any articles from {filename}")
            continue
            
        for article in articles:
            if reprocess_article(article):
                total_processed += 1

    logger.info(f"Reprocessing finished. Total articles updated: {total_processed}")

if __name__ == "__main__":
    main()
