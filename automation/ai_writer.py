import os
import requests
import json
import time
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# [V3.2] 절대 경로 기반 .env 로드 (윈도우 호환성 극대화)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

class AIWriter:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # 디버깅: 키가 로드됐는지 확인 (첫 5자만)
        if self.gemini_key:
            print(f"[*] Gemini Key Loaded: {self.gemini_key[:5]}***")
        else:
            print("[!] CRITICAL: Gemini Key NOT FOUND in .env")

    def _generate_api_call(self, prompt, provider="gemini", model_name=None):
        if provider == "gemini":
            if not self.gemini_key:
                raise ValueError("Gemini API Key is missing.")
            genai.configure(api_key=self.gemini_key)
            target_model = model_name if model_name else 'models/gemini-flash-lite-latest'
            model = genai.GenerativeModel(target_model)
            return model.generate_content(prompt).text
        else:
            if not self.openrouter_key:
                raise ValueError("OpenRouter API Key is missing.")
            target_model = model_name if model_name else "deepseek/deepseek-chat"
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openrouter_key.strip()}"},
                data=json.dumps({
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": "너는 한국어 뉴스를 전문적으로 요약하고 분석하는 최고 수준의 AI 편집장이다. 반드시 전문적이고 자연스러운 '존댓말 한국어'로만 응답하라."},
                        {"role": "user", "content": prompt}
                    ]
                }),
                timeout=180
            )
            return response.json()["choices"][0]["message"]["content"]

    def generate_content(self, prompt_or_keyword, category="AI·신기술", model=None, is_direct_prompt=True):
        prompt = prompt_or_keyword
        max_retries = 3
        for attempt in range(max_retries):
            try:
                res = self._generate_api_call(prompt, "gemini", model_name=model)
                if res: return res
            except Exception as e:
                print(f"[!] Gemini Attempt {attempt+1} Failed: {e}")
                # 429 에러 등을 대비한 잠시 휴식
                time.sleep(5)
                try:
                    print(f"[*] Switching to OpenRouter (Emergency)...")
                    res = self._generate_api_call(prompt, "openrouter")
                    if res: return res
                except Exception as e2:
                    print(f"[!] OpenRouter Attempt {attempt+1} Failed: {e2}")
                    time.sleep(70)
        return None

    def save_post(self, content, filename):
        if not content: return
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posts_dir = os.path.join(base_dir, "content", "posts")
        os.makedirs(posts_dir, exist_ok=True)
        clean_content = content.replace("```markdown", "").replace("```", "").strip()
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(clean_content)
