import sys
import os
from telegram_bridge import TelegramBridge

def main():
    bridge = TelegramBridge()
    
    if len(sys.argv) < 2:
        # 인자 없으면 Pull 모드
        print(bridge.pull_instructions())
        return

    # 첫 번째 인자가 'pull'이면 수신 모드
    cmd = sys.argv[1].lower()
    if cmd == "pull":
        print(bridge.pull_instructions())
    else:
        # 그 외에는 메시지 전송
        message = sys.argv[1]
        if bridge.send_report(message):
            print(f"Message sent: {message[:30]}...")
        else:
            print("Failed to send message.")

if __name__ == "__main__":
    main()
