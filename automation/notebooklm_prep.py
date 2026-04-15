import os
import json
import time
import subprocess
import logging
from datetime import datetime
from harvester_v3 import HarvesterV3

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NotebookLM_Prep")

class NotebookLMApp:
    """Python wrapper for the notebooklm-mcp CLI tool (nlm)"""
    def __init__(self):
        # We assume nlm is available in exactly the same way user types it
        self.cmd_base = ["nlm"]
    
    def run_cmd(self, args, use_json=True):
        cmd = self.cmd_base + args
        if use_json:
            cmd.append("--json")
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if use_json:
                return json.loads(res.stdout.strip())
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"[NLM ERROR] Command failed: {' '.join(cmd)}\n{e.stderr}")
            return None
        except Exception as e:
            logger.error(f"[NLM ERROR] {e}")
            return None

    def create_notebook(self, title):
        logger.info(f"Creating notebook: {title}")
        return self.run_cmd(["create", "notebook", title])

    def add_source(self, notebook_id, filepath):
        logger.info(f"Adding source to {notebook_id}: {filepath}")
        return self.run_cmd(["add", "source", notebook_id, "--file", filepath])

    def create_editorial_report(self, notebook_id):
        logger.info(f"Creating Editorial Report for notebook {notebook_id}")
        prompt = (
            "당신은 TechCrunch와 Wired의 수석 에디터입니다. 제공된 모든 기사 소스들을 바탕으로, "
            "이 분야의 가장 중요하고 치명적인 기술적 변화를 다루는 1,500단어 이상의 '심층 사설(Editorial Feature)'형식의 기사를 작성하세요. "
            "절대 개조식(글머리 기호)을 남용하지 말고, 독자를 끌어당기는 후킹한 서론, 탄탄한 서술형 본문, "
            "그리고 미래를 전망하는 통찰력 있는 결론으로 구성하세요. 매우 전문적이고 저널리즘 원칙에 맞게 작성하세요."
        )
        return self.run_cmd(["create", "report", notebook_id, "--format", "Create Your Own", "--prompt", prompt])

    def create_audio_podcast(self, notebook_id):
        logger.info(f"Creating Audio Podcast Overview for notebook {notebook_id}")
        return self.run_cmd(["create", "audio", notebook_id])
        
    def check_status(self, notebook_id):
        return self.run_cmd(["status", "artifacts", notebook_id])

def process_macro_synthesis(limit_per_cat=15):
    logger.info("==============================================")
    logger.info("  [START] Premium Macro-Synthesis Pipeline    ")
    logger.info("==============================================")
    logger.info(" [1] Harvesting raw articles from RSS...")
    harvester = HarvesterV3()
    category_files = harvester.dump_to_category_files(limit_per_cat=limit_per_cat)
    
    jobs_file = "automation/premium_jobs.json"
    active_jobs = {}
    
    if not category_files:
        logger.error(" [!] No category files generated.")
        return False
        
    logger.info(f" [2] Bootstrapping NLM Automation... ({len(category_files)} categories)")
    app = NotebookLMApp()
    
    for cat, filepath in category_files.items():
        # Step 2a: Create notebook
        title = f"{datetime.now().strftime('%Y-%m-%d')} {cat} MegaTrend"
        notebook = app.create_notebook(title)
        
        if not notebook or 'notebook' not in notebook:
            logger.error(f" Failed to create notebook for {cat}")
            continue
            
        nb_id = notebook['notebook']['id']
        logger.info(f" [OK] Notebook created: {nb_id}")
        
        # Step 2b: Add source (the raw dump)
        source_res = app.add_source(nb_id, filepath)
        logger.info(f" [OK] Source added. Starting generation...")
        
        
        # Step 2c: Trigger Studio Generation (Editorial Report)
        report_res = app.create_editorial_report(nb_id)
        if report_res:
            logger.info(f" [OK] Triggered Journalistic Editorial for {cat}")
            active_jobs[cat] = {
                "notebook_id": nb_id,
                "title": title,
                "status": "pending",
                "triggered_at": datetime.now().isoformat()
            }
            
        # Step 2d: Trigger Audio Generation (Podcast)
        # [DISABLED] 오디오 파일은 무료 서버 트래픽/대역폭 한도 초과 우려가 있으므로 임시 비활성화합니다.
        # audio_res = app.create_audio_podcast(nb_id)
        # if audio_res:
        #     logger.info(f" [OK] Triggered Audio Podcast for {cat}")
    
    # Save jobs for the Publisher phase
    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(active_jobs, f, indent=4, ensure_ascii=False)
            
    logger.info(f"\n[PIPELINE PHASE 1 COMPLETE] {len(active_jobs)} Journalistic Editorials are generating.")
    logger.info("Next Step: Download the outputs and package them into the Hugo markdown templates.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()
    
    process_macro_synthesis(limit_per_cat=args.limit)
