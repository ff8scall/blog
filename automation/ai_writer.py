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
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # 디버깅: 키 로드 상태 확인 (V3.8 Quad-AI 구성)
        if self.gemini_key: print(f"[*] Gemini Key Loaded: {self.gemini_key[:5]}***")
        if self.deepseek_key: print(f"[*] DeepSeek Key Loaded: {self.deepseek_key[:5]}***")
        if self.groq_key: print(f"[*] Groq Key Loaded: {self.groq_key[:5]}***")
        if self.openrouter_key: print(f"[*] OpenRouter Key Loaded: {self.openrouter_key[:5]}***")

    def _generate_api_call(self, prompt, provider="gemini", model_name=None):
        """[V3.8] 멀티 AI 통합 호출 (제미나이, 딥시크, 그로그, 오픈라우터)"""
        if provider == "gemini":
            if not self.gemini_key: return None
            try:
                genai.configure(api_key=self.gemini_key)
                # [V10.9] 하드코딩 제거: 전달받은 모델명 사용
                model = genai.GenerativeModel(model_name if model_name else 'models/gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
                return None
            except Exception as e:
                print(f" [!] Gemini Failure: {e}")
                return None
            
        elif provider == "deepseek":
            if not self.deepseek_key: return None
            try:
                target_model = model_name if model_name else "deepseek-chat"
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": target_model,
                        "messages": [{"role": "system", "content": "Output ONLY JSON."}, {"role": "user", "content": prompt}],
                        "temperature": 0.3
                    }), timeout=60
                )
                data = response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    return None
            except: return None

        elif provider == "groq":
            if not self.groq_key: return None
            try:
                target_model = model_name if model_name else "llama-3.1-8b-instant"
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": target_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    }), timeout=30
                )
                data = response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f" [!] groq Error Body: {data}")
                    return None
            except Exception as e:
                print(f" [!] groq Failure: {e}")
                return None
                
        elif provider == "openrouter":
            if not self.openrouter_key: return None
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openrouter_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}]
                    }), timeout=60
                )
                data = response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f" [!] openrouter Error Body: {data}")
                    return None
            except Exception as e:
                print(f" [!] openrouter Failure: {e}")
                return None
        return None

    def generate_content(self, prompt, category="AI·신기술", model=None):
        """[V10.9 Production] 안정 최우선: 15초 간격으로 가용 모델 순회"""
        candidates = [
            ("groq", "llama-3.1-8b-instant"),
            ("openrouter", "openai/gpt-4o-mini"),
            ("gemini", "models/gemini-2.0-flash"),
            ("gemini", "models/gemini-flash-latest")
        ]
        
        for provider, model_name in candidates:
            try:
                res = self._generate_api_call(prompt, provider, model_name=model_name)
                if res and len(res.strip()) > 10:
                    return res
            except Exception as e:
                print(f" [!] {provider} mode skip: {e}")
            
            # [USER RULE] 무료 API 보호를 위한 15초 대기
            time.sleep(15)
            
        return None

    def save_post(self, content, filename):
        if not content: return
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posts_dir = os.path.join(base_dir, "content", "posts")
        os.makedirs(posts_dir, exist_ok=True)
        clean_content = content.replace("```markdown", "").replace("```", "").strip()
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(clean_content)
