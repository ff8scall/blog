import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

# 지침함 경로
INBOX_PATH = os.path.join(os.path.dirname(base_dir), '.gravityBrain', 'TELEGRAM_INBOX.md')

class TelegramBridge:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_report(self, message):
        """상세 작업 리포트를 전송합니다."""
        if not self.token or not self.chat_id:
            return False
        
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            # 텔레그램 메시지 길이 제한(4096자) 대응
            if len(message) > 4000:
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for chunk in chunks:
                    requests.post(url, json={"chat_id": self.chat_id, "text": chunk, "parse_mode": "Markdown"}, timeout=10)
            else:
                requests.post(url, json=payload, timeout=10)
            return True
        except Exception as e:
            print(f"Error sending report: {e}")
            return False

    def pull_instructions(self):
        """사용자의 최신 답장을 가져와 INBOX.md에 저장합니다."""
        url = f"{self.api_url}/getUpdates"
        try:
            res = requests.get(url, params={"limit": 5, "offset": -5}, timeout=10).json()
            if not res.get("ok"):
                return False

            updates = res.get("result", [])
            if not updates:
                return "새로운 지침이 없습니다."

            # 마지막 메시지만 추출 (사용자가 보낸 것만)
            new_msgs = []
            for up in updates:
                msg = up.get("message", {})
                sender_id = str(msg.get("from", {}).get("id", ""))
                if sender_id == str(self.chat_id):
                    text = msg.get("text")
                    date = datetime.fromtimestamp(msg.get("date")).strftime('%Y-%m-%d %H:%M:%S')
                    new_msgs.append(f"### [{date}]\n{text}\n")

            if new_msgs:
                # INBOX.md에 기록 (덮어쓰지 않고 추가)
                with open(INBOX_PATH, "a", encoding="utf-8") as f:
                    f.write("\n" + "\n".join(new_msgs))
                return f"{len(new_msgs)}개의 새로운 지침을 수신했습니다."
            
            return "최근 수신된 사용자 메시지가 없습니다."
        except Exception as e:
            return f"Error pulling instructions: {e}"

if __name__ == "__main__":
    bridge = TelegramBridge()
    # 실행 시 최신 메시지 수집
    print(bridge.pull_instructions())
