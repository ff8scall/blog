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
            genai.configure(api_key=self.gemini_key)
            target_model = model_name if model_name else 'models/gemini-flash-lite-latest'
            model = genai.GenerativeModel(target_model)
            return model.generate_content(prompt).text
            
        elif provider == "deepseek":
            if not self.deepseek_key: return None
            try:
                target_model = model_name if model_name else "deepseek-chat"
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": target_model,
                        "messages": [{"role": "system", "content": "너는 프리미엄 테크 저널리스트이자 전문 번역가다."}, {"role": "user", "content": prompt}],
                        "temperature": 0.7
                    }), timeout=120
                )
                data = response.json()
                return data["choices"][0]["message"]["content"] if "choices" in data else None
            except: return None

        elif provider == "groq":
            if not self.groq_key: return None
            try:
                # Groq 초광속 LPU 연동 (Llama-3-70b 기본 사용)
                target_model = model_name if model_name else "llama3-70b-8192"
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": target_model,
                        "messages": [{"role": "system", "content": "너는 전광석화 같은 정확한 테크 뉴스 전문 에디터다."}, {"role": "user", "content": prompt}],
                        "temperature": 0.5
                    }), timeout=60
                )
                data = response.json()
                return data["choices"][0]["message"]["content"] if "choices" in data else None
            except Exception as e:
                print(f"[!] Groq Request Failed: {e}")
                return None
                
        elif provider == "openrouter":
            if not self.openrouter_key: return None
            target_model = model_name if model_name else "deepseek/deepseek-chat"
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openrouter_key.strip()}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": target_model,
                        "messages": [{"role": "user", "content": prompt}]
                    }), timeout=120
                )
                data = response.json()
                return data["choices"][0]["message"]["content"] if "choices" in data else None
            except: return None
        return None

    def generate_content(self, prompt, category="AI·신기술", model=None):
        """[V3.8] 4중 폴백: 제미나이 -> 딥시크 -> 그로그 -> 오픈라우터 순서로 시도"""
        # 1순위: 제미나이
        try:
            print(f"[*] Level 1 Attempt: Gemini...")
            res = self._generate_api_call(prompt, "gemini", model_name=model)
            if res: return res
        except: pass

        # 2순위: 딥시크
        try:
            print(f"[*] Level 2 Attempt: DeepSeek (Emergency/Fallback)...")
            res = self._generate_api_call(prompt, "deepseek")
            if res: return res
        except: pass

        # 3순위: 그로그 (초고속 요약/정리 특화)
        try:
            print(f"[*] Level 3 Attempt: Groq (LPU Speed Booster)...")
            res = self._generate_api_call(prompt, "groq")
            if res: return res
        except: pass

        # 4순위: 오픈라우터 (최후의 보루)
        try:
            print(f"[*] Level 4 Attempt: OpenRouter (Final Defense)...")
            res = self._generate_api_call(prompt, "openrouter")
            if res: return res
        except: pass

        return None

    def save_post(self, content, filename):
        if not content: return
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posts_dir = os.path.join(base_dir, "content", "posts")
        os.makedirs(posts_dir, exist_ok=True)
        clean_content = content.replace("```markdown", "").replace("```", "").strip()
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(clean_content)
