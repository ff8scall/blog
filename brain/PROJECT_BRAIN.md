# 🧠 PROJECT BRAIN - 프로젝트 헌법 (Core System & Workflow v2.0)

> **[경고: 절대 규칙]** 이 파일은 프로젝트의 최상위 운영 규칙이자 헌법입니다. 절대 삭제하거나 임의로 수정하지 마십시오. 프로젝트에 참여하는 모든 AI 에이전트는 사용자의 요구사항을 처리하기 전, **반드시 이 문서를 최우선으로 읽고 어떠한 예외도 없이 엄격하게 준수**해야 합니다.

---

## 📌 제1장. 최상위 핵심 원칙 (8 Core Principles)

1. **Korean Language Default (한국어 기본 원칙)**
   - 대화, 코드 주석, 기획서, 설계서, 체크리스트 등 **모든 산출물과 파일명은 100% 한국어**로 작성한다.

2. **Documentation First (문서 우선 원칙)**
   - 모든 작업은 문서 생성으로 시작한다. 코드보다 문서가 먼저 존재해야 한다.

3. **No Code Before Design Approval (설계 승인 전 코딩 금지)**
   - **[MASC 모드]**를 거쳐 설계 문서를 산출하고, 사용자의 승인을 받은 후에만 코딩을 시작한다.

4. **Checklist Driven Execution (체크리스트 기반 실행)**
   - 모든 작업은 체크리스트 파일로 철저히 관리한다. (`/checklists/` 폴더 활용)

5. **Task Decomposition (작업의 원자적 분해)**
   - 실행 가능한 최소 단위로 분해하며, 명확한 입/출력과 완료 조건을 가진다.

6. **Risk Analysis Mandatory (리스크 분석 필수)**
   - 성능, 보안, 유지보수 측면의 리스크 분석을 반드시 포함한다.

7. **Iterative Improvement (반복 개선 원칙)**
   - '문제 탐지 → 개선안 제안 → 개선 적용' 사이클을 최소 1회 수행한다.

8. **Korean Context Localization (한국 사용자 특화)**
   - 한국의 기술 표준, 사용자 정서, 로컬라이제이션 표준을 최우선으로 한다.

---

## 📌 제2장. MASC 모드 (Multi-Agent Simulation & Consensus)

새로운 기능 개발 시 AI는 단독 코딩하지 않고 4인을 활성화하여 분석 및 토론한다.
- **UX/UI 기획자 / 시스템 아키텍트 / 프론트엔드 엔지니어 / 보안 및 QA 심사역**

---

## 📌 제3장. 디렉토리 구조 및 상태 관리 규칙

- `/brain`: 헌법 및 핵심 지식 보관소
- `/docs`: MASC 설계 문서 및 회의록
- `/checklists`: 진행 중인 단위 작업 체크리스트
- `/automation` (src): 엔진 소스 코드
- `/completed`: 완료된 작업 아카이빙 폴더

---

## 🏛️ [추가] 레고-시아 뉴스 엔진 특화 규칙 (V3.0.18 안정화 버전)

1. **데이터 격리 및 대량 수확**: KO/EN 데이터 분리 및 Search(NewsAPI) + RSS 하이브리드 모드 사용. (최소 20건 이상 수확 가능 환경 구축)
2. **이미지 무결성**: 발행 시 `FALLBACK_MAP`을 통과하여 404를 방지한다.
3. **내부 링크**: DB에 저장된 `local_url`을 기반으로 실시간 sitelink를 생성한다.
4. **투명한 진단 (Diagnostic Logging)**: `Cancellation Breakdown` 시스템을 통해 중복(Duplicate), 심사탈락(Review), 예산초과(Budget)를 실시간으로 모니터링한다. 중복률이 높은 것은 정상적인 필터링 결과임(100% 중복 방지 로직).

🧾 [문서 정보]
Version: 2.1 (Stability & Massive Sniper Logic Integrated)
Status: Core Production Workflow
Last Adjusted: 2026-04-12
