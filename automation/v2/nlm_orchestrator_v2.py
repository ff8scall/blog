# -*- coding: utf-8 -*-
"""
[nlm_orchestrator_v2.py] V2 고밀도 뉴스 파이프라인 오케스트레이터
============================================================
전문 추출(Trafilatura) 및 메타데이터(Newspaper4k)가 적용된 V2 파이프라인을 실행합니다.
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime

# 부모 디렉토리를 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
automation_dir = os.path.dirname(current_dir)
if automation_dir not in sys.path:
    sys.path.append(automation_dir)

from notebooklm_prep import process_macro_synthesis_v2, NotebookLMApp
from notebooklm_publisher import NotebookLMPublisher
from common_utils import send_telegram_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(automation_dir, "nlm_orchestrator_v2.log"), encoding='utf-8')
    ]
)
logger = logging.getLogger("LegoSia.NLM_Orchestrator_V2")

def run_phase1_v2(mode="B", limit=5):
    """Phase 1: V2 수확(전문 추출) → NLM 트리거"""
    logger.info("=" * 60)
    logger.info(f"  [V2] PHASE 1: Data Enrichment & NLM Trigger (Mode {mode}, limit={limit})")
    logger.info("=" * 60)
    
    t0 = time.time()
    
    # [V2.1] NLM 로그인 세션 강제 활성화 (사용자 요청)
    app = NotebookLMApp()
    app.login()
    input("\n[PAUSE] 브라우저 로그인을 완료한 후 엔터(Enter) 키를 누르세요...")
    
    success = process_macro_synthesis_v2(limit_per_cat=limit, mode=mode)
    t1 = time.time()
    
    if success:
        logger.info(f"[V2 PHASE 1 OK] Completed in {t1-t0:.1f}s.")
    else:
        logger.error("[V2 PHASE 1 FAIL] V2 Processing failed.")
    return success

def run_phase2_v2():
    """Phase 2: V2 결과물 게시 (이미지 전략 적용됨)"""
    logger.info("=" * 60)
    logger.info("  [V2] PHASE 2: Enriched Content Publish")
    logger.info("=" * 60)
    
    t0 = time.time()
    publisher = NotebookLMPublisher()
    publisher.process_pending_jobs()
    t1 = time.time()
    
    logger.info(f"[V2 PHASE 2 OK] Completed in {t1-t0:.1f}s.")

def run_full_v2(mode="B", limit=5, poll=60, wait=900):
    """V2 전체 파이프라인"""
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║  NotebookLM V2 ENRICHED Pipeline Orchestrator             ║")
    logger.info(f"║  Mode: {mode} | Limit: {limit} | Full Content Enabled ║")
    logger.info("╚" + "═" * 58 + "╝")
    
    send_telegram_report(f"🚀 <b>[V2 Premium]</b> Start\nMode: {mode} | Limit: {limit}\n<i>Full-text enrichment active</i>")
    
    if not run_phase1_v2(mode=mode, limit=limit):
        return
        
    logger.info(f"\n[WAITING] NotebookLM generating enriched reports...")
    waited = 0
    while waited < wait:
        time.sleep(poll)
        waited += poll
        logger.info(f"[POLL] {waited}s elapsed. Checking V2 jobs...")
        
        publisher = NotebookLMPublisher()
        publisher.process_pending_jobs()
        
        # 모든 작업 완료 여부 체크 (premium_jobs.json 확인)
        try:
            with open("automation/premium_jobs.json", "r", encoding="utf-8") as f:
                jobs = json.load(f)
                if all(j.get("status") == "published" for j in jobs.values()):
                    logger.info("[V2 DONE] All enriched articles published!")
                    break
        except: pass

    send_telegram_report(f"✅ <b>[V2 Premium]</b> Finished!\nFull-text articles & Original images applied.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="B", choices=["A", "B", "C"])
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--phase", type=int, default=0)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    
    if args.full or args.phase == 0:
        run_full_v2(mode=args.mode, limit=args.limit)
    elif args.phase == 1:
        run_phase1_v2(mode=args.mode, limit=args.limit)
    elif args.phase == 2:
        run_phase2_v2()
