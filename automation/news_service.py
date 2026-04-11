import os
import time
import subprocess
import sys
from datetime import datetime

class NewsService:
    def __init__(self, interval_seconds=3600):
        self.interval = interval_seconds
        self.log_path = "automation/logs/service.log"
        os.makedirs("automation/logs", exist_ok=True)

    def log(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_msg = f"{timestamp} {message}"
        try:
            print(log_msg)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except:
            # Silent fail for terminal/file encoding issues to keep the loop alive
            pass

    def run_once(self):
        """news_main.py를 한 번 실행하고 결과를 로그에 남김"""
        self.log("Starting Hourly News Harvest Cycle...")
        try:
            # news_main.py 실행 (주간/상시 모드)
            result = subprocess.run([sys.executable, "automation/news_main.py"], 
                                    capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.log("SUCCESS: Cycle Completed Successfully.")
            else:
                self.log(f"FAILED: Cycle Failed with return code {result.returncode}")
                # 에러 로그는 별도 기록
                if result.stderr:
                    error_msg = f"Error: {result.stderr[:500]}"
                    self.log(error_msg)
                
        except Exception as e:
            self.log(f"ERROR: Global Service Error: {str(e)}")

    def start(self):
        self.log("=== [Lego-sia] Autonomous News Service V1.1 Started ===")
        print("Magazine engine is now online. Running every hour.")
        
        while True:
            start_time = time.time()
            self.run_once()
            
            elapsed = time.time() - start_time
            wait_time = max(0, self.interval - elapsed)
            
            self.log(f"SLEEP: Sleeping for {int(wait_time/60)} minutes until next cycle...")
            time.sleep(wait_time)

if __name__ == "__main__":
    service = NewsService(interval_seconds=3600)
    service.start()
