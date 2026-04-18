# -*- coding: utf-8 -*-
import os
import sys
import logging
from harvester_v3 import HarvesterV3
from quality_filter import QualityFilter

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestV5Pipeline")

def test_pipeline():
    logger.info("--- [V5 Pipeline Test Start] ---")
    
    # 1. Harvester 초기화
    harvester = HarvesterV3()
    
    # 2. 뉴스 수집 및 필터링 테스트 (카테고리당 2개만 선별하도록 설정)
    logger.info("Step 1: Harvesting & Filtering...")
    try:
        # fetch_all 내부에서 QualityFilter가 실행됨
        articles, stats = harvester.fetch_all(limit_per_cat=2)
        
        logger.info(f"Total High-Quality Articles Selected: {len(articles)}")
        for cat, count in stats.items():
            logger.info(f" - {cat}: {count} items")
            
        if not articles:
            logger.error("No articles survived the pipeline. Check logs/API status.")
            return

        # 3. 마크다운 덤프 테스트
        logger.info("Step 2: Dumping to Category Files...")
        output_files = harvester.dump_to_category_files(limit_per_cat=2)
        
        for cat, path in output_files.items():
            if os.path.exists(path):
                logger.info(f" [OK] {cat} dump created: {path}")
                # 파일 내용 살짝 확인
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "## 📰 [" in content and "Quality Score:" in content:
                        logger.info(f"      Content structure verified for {cat}")
                    else:
                        logger.warning(f"      Content structure check FAILED for {cat}")
            else:
                logger.error(f" [FAIL] {cat} dump missing at {path}")

    except Exception as e:
        logger.error(f"Pipeline Test Error: {e}", exc_info=True)

    logger.info("--- [V5 Pipeline Test End] ---")

if __name__ == "__main__":
    test_pipeline()
