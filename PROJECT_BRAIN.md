# 🧠 PROJECT BRAIN: 뉴스 엔진 고도화 기록

## 2026-04-13: 엔진 지능 및 다양성 강화 (V3.0.32)

### ✅ 완료된 주요 작업
1.  **AI Writer V3.5 (Free-First 전략)**
    *   기존 Gemini 의존도를 낮추기 위해 로컬 Ollama (`gemma4:latest`) 기반으로 전환.
    *   `NewsEditor` 호환을 위한 `role` 인자 및 `is_all_exhausted` 메서드 추가.
2.  **Harvester V2.5 (회복 탄력성 강화)**
    *   NewsAPI 할당량 소진 시 `GNews`로 자동 전환되는 Fallback Sniper 로직 구현.
    *   12개 카테고리 전체에 대한 고른 수확 보장.
3.  **Engine Stability Fix**
    *   `news_main.py`의 비동기 `await` 호출 오류(Harvester) 수정.
    *   `.env` 자동 로드 누락 수정.
    *   `ai-tools` 카테고리 누락으로 인한 KeyError 해결.

### 📊 테스트 결과 요약
*   **12개 카테고리 스캔**: GNews Fallback을 통해 모든 카테고리에서 소스 식별 확인.
*   **중복 제어**: `Today-Only` 필터와 `.news_cache` 시스템이 정상적으로 중복 뉴스 처리를 차단함.
*   **전략 가이드**: 기사 점수 및 키워드 기반의 전략 가이드 생성 로직이 Gemma4 모델에서 정상 작동 확인.

---
**상태**: 🚀 배포 준비 완료 (Visual Audit 단계 진행 중)
