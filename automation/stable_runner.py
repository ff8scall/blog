import os
import time
import random
import sys

# 현재 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_writer import AIWriter

TOPIC_POOLS = [
    ("Faceless YouTube automation with AI", "수익화 전략"),
    ("Making money with PromptBase and niche prompts", "수익화 전략"),
    ("AI-driven drop-shipping optimization", "수익화 전략"),
    ("Micro-SaaS development using OpenAI API", "수익화 전략"),
    ("AI blog flipping strategy for passive income", "수익화 전략"),
    ("AutoGen and Multi-agent systems explained", "AI 에이전트"),
    ("Running Local LLMs with Ollama for privacy", "AI 에이전트"),
    ("Next-gen Assistant: GPT-5.5 vs Claude 4.6", "AI·신기술"),
    ("NVIDIA Blackwell GPU impact analysis", "AI·신기술"),
    ("Sora's evolution into enterprise tools", "AI·신기술"),
    ("Apple Intelligence security vulnerabilities", "AI·신기술"),
    ("AI-based camping route optimization", "캠핑"),
    ("Smart camping gear: 2026 Tech Review", "캠핑"),
    ("Technical camping for digital nomads", "캠핑")
]

def run():
    writer = AIWriter()
    print("--- Engine Started (Stable Mode) ---")
    
    while True:
        # 무작위 주제 선정
        topic, category = random.choice(TOPIC_POOLS)
        print(f"[*] Task: {topic} ({category})")
        
        try:
            content = writer.generate_content(keyword=topic, category=category)
            if content:
                filename = f"auto-{int(time.time())}.md"
                writer.save_post(content, filename)
                print(f"[OK] Saved: {filename}")
            
            # API 보호를 위한 넉넉한 휴식 (2~3분)
            sleep_time = random.randint(120, 180)
            print(f"[*] Sleeping for {sleep_time}s...")
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"[!] Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    run()
