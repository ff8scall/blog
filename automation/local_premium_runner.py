# -*- coding: utf-8 -*-
import os
import time
import subprocess
import logging
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("local_premium_runner.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("PremiumRunner")

def run_pipeline():
    """nlm_orchestrator.py를 실행하여 전체 프리미엄 뉴스 파이프라인 가동"""
    logger.info("=" * 60)
    logger.info(f"🚀 [LOOP] Starting Premium News Pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # Phase 1 & 2 통합 실행 (모드 B, 카테고리당 10개)
        # --full 옵션으로 수집부터 게시까지 한 번에 처리
        cmd = ["py", "automation/nlm_orchestrator.py", "--mode", "B", "--full", "--limit", "10"]
        subprocess.run(cmd, check=True)
        logger.info("✅ [SUCCESS] Pipeline cycle completed successfully.")
    except Exception as e:
        logger.error(f"❌ [ERROR] Pipeline failed: {e}")

def main_loop():
    interval_hours = 3
    logger.info("=== [LEGO-SIA] Local Premium Runner Activated ===")
    logger.info(f"[*] Cycle Interval: Every {interval_hours} hours")
    
    while True:
        run_pipeline()
        
        next_run = datetime.now() + timedelta(hours=interval_hours)
        logger.info(f"💤 [SLEEP] Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 3시간 대기 (초 단위)
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    main_loop()
