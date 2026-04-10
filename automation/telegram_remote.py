import os
import time
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# .env 로드
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class TelegramRemote:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.last_update_id = 0
        self.last_run_hour = -1 # 시간당 한 번만 실행되도록 체크

    def send_resp(self, text):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        requests.post(url, json={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"})

    def run_scheduled_harvest(self, hour):
        """새벽 시간당 정밀 수집 (1 AM ~ 6 AM)"""
        self.send_resp(f"🌃 **[SYSTEM] 새벽 {hour}시 정밀 수집을 시작합니다.** (시간당 40선 타격)")
        # 주간 모드처럼 10개 내외로 가져오되, 새벽에는 빌드/배포까지 자동 수행
        subprocess.run(["python", "automation/news_main.py", "--night"])

    def handle_command(self, cmd):
        if cmd == "/news":
            self.send_resp("🛰️ **뉴스 수집 명령 수신!** 현재 기사 데이터 선별 중...")
            subprocess.run(["python", "automation/news_main.py"])
        
        elif cmd == "/night":
            self.send_resp("🌃 **수동 야간 모드 가동!** (대량 수집 및 배포)")
            subprocess.run(["python", "automation/news_main.py", "--night"])

        elif cmd == "/status":
            post_count = 0
            for root, dirs, files in os.walk("content/posts"):
                post_count += len([f for f in files if f.endswith(".md")])
            self.send_resp(f"📊 **Lego-sia 블로그 현황**\n\n- 전체 정예 기사: {post_count}개\n- 시스템 상태: 분산 수집 모드 가동 중 ⚙️\n- 다음 정기 수집: 매시 정각 (01:00~06:00)")
            
        elif cmd == "/deploy":
            self.send_resp("🚀 **배포 명령 수신!** 사이트를 빌드하고 전송합니다...")
            subprocess.run(["C:\\hugo_tmp\\hugo.exe", "--gc", "--cleanDestinationDir"])
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", "Remote Deploy via Telegram"])
            subprocess.run(["git", "push", "origin", "main"])
            self.send_resp("✨ **배포 완료!**")

    def listen(self):
        print("[*] Telegram Remote & Hourly Scheduler Started...")
        self.send_resp("🎮 **Lego-sia 통합 제어기 (새벽 분산 수집 모드) 가동 시작.**")
        
        while True:
            # 1. 분산 스케줄러 (새벽 1시 ~ 6시 정각 체크)
            now = datetime.now()
            if now.hour in [1, 2, 3, 4, 5, 6] and now.minute == 0:
                if self.last_run_hour != now.hour:
                    self.run_scheduled_harvest(now.hour)
                    self.last_run_hour = now.hour
            
            # 다음 날을 위한 시간 초기화
            if now.hour == 0: self.last_run_hour = -1

            # 2. 텔레그램 명령 체크
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates?offset={self.last_update_id + 1}&timeout=10"
                res = requests.get(url, timeout=15).json()
                for update in res.get("result", []):
                    self.last_update_id = update["update_id"]
                    if "message" in update and str(update["message"]["chat"]["id"]) == self.chat_id:
                        text = update["message"].get("text", "")
                        print(f"[*] Command: {text}")
                        self.handle_command(text)
            except Exception as e:
                print(f"[ERROR] Logic error: {e}")
                time.sleep(10)
            
            time.sleep(1)

if __name__ == "__main__":
    remote = TelegramRemote()
    remote.listen()
