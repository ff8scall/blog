import os
import time
import random
import sys
from ai_writer import AIWriter

# 인코딩 문제 해결 (Windows용)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 기획된 주제 리스트 (카테고리 매칭 포함)
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

def run_infinite_loop():
    writer = AIWriter()
    post_count = 0
    
    print("=== [ Unlimited Automation Engine Started ] ===")
    
    random.shuffle(TOPIC_POOLS)
    
    for topic, category in TOPIC_POOLS:
        post_count += 1
        print(f"\n[{post_count}/{len(TOPIC_POOLS)}] Processing: {topic} ({category})")
        
        try:
            # 글 생성
            content = writer.generate_content(keyword=topic, category=category)
            
            if content:
                # 파일명 생성
                safe_title = topic.lower().replace(" ", "-").replace(":", "").replace("'", "")[:30]
                filename = f"{int(time.time())}-{safe_title}.md"
                
                # 저장
                writer.save_post(content, filename)
                print(f"[SUCCESS] Saved: {filename}")
            
            # API 보호를 위한 대기 (60~120초)
            wait_time = random.randint(60, 120)
            print(f"[WAIT] Waiting {wait_time}s for next task...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"[ERROR] Failed {topic}: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    run_infinite_loop()
