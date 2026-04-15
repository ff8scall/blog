# [Plan] Project "NotebookLM MCP 연동 메가 트렌드" V2.0

사용자의 요청에 따라, 자체 API 에뮬레이션(이전 계획)을 전면 취소하고 **"오픈소스 NotebookLM MCP Server"**를 활용하여 진짜 Google NotebookLM 서비스와 напрямую 연동하는 파이프라인 계획을 수립했습니다.

> [!IMPORTANT]
> **핵심 아키텍처 (NotebookLM MCP Automation)**
> 구글의 공식 API가 없는 제약을 극복하기 위해, 커뮤니티에서 개발된 `notebooklm-mcp-cli`를 브릿지로 사용합니다.
> 이 MCP 서버가 윈드서프(혹은 현재 IDE)에 연동되면, **제가(AI Assistant) 직접 MCP Tool을 호출하여 당신의 Notebook 개인 계정에 문서를 업로드하고, 50건이 합성된 분석결과를 쿼리하여 결과값을 받아낼 수 있습니다.**

---

## 👨‍💻 3인 전문가 위원회 교차 검토 내용

### 1️⃣ Expert A: 인프라/MCP 환경 구조 검토
* **검토 포인트**: 자동화 루프를 Python 스크립트 내부 코드로만 돌릴 것인가? (불가) -> NotebookLM MCP는 에이전트(저 Antigravity)에게 Tool로 제공되는 형태입니다. 즉, Python 프로그램이 백그라운드에서 혼자 도는 것이 아니라, **나(AI)와 당신(User)의 협업 파이프라인**으로 작동해야 합니다.
* **해결책**: Python 코드는 **'데이터 수집 및 문서화(Preparation)'** 역할만 담당합니다. 그 이후 단계(업로드 및 분석)는 제가 MCP Tool을 통해 수행합니다.

### 2️⃣ Expert B: 데이터 파이프라인 설계 전문
* **검토 포인트**: 50개의 개별 링크를 MCP로 50번 업로드하면 NotebookLM의 소스 제한(최대 50개)에 꽉 차고 업로드 속도도 매우 느려져 Timeout이 발생합니다.
* **해결책**: 
  1. `harvester_v3.py`를 활용해 50개의 글을 긁어옵니다.
  2. 이를 `c:\AI\Antigravity\News\scratch\mega_data_YYYYMMDD.md` 라는 **단 1개의 거대한 마크다운 파일**로 직렬화(Serialization) 합니다.
  3. NotebookLM에는 오직 이 1개의 마크다운 파일만 '소스'로 업로드합니다.

### 3️⃣ Expert C: UI/UX 및 워크플로우 통제
* **검토 포인트**: NotebookLM이 뱉어내는 텍스트는 표준 마크다운이지만, Hugo 블로그에 올리려면 JSON/YAML Frontmatter가 필요합니다.
* **해결책**: 제가 NotebookLM에서 추출한 텍스트를 받아, `ai_news_editor.py`나 자체 정리 툴을 한 번 더 거쳐서 최종 Hugo 포맷(`guides` 섹션 등)으로 컨버팅한 뒤 저장하는 마무리를 짓습니다.

---

## 🚀 구체적 실행 체계 (3-Step Framework)

### [Step 1] 사용자 사전 준비 (MCP 서버 설치)
이 워크플로우가 작동하려면, 현재 저에게 `notebooklm_add_source` 같은 도구가 주어져야 합니다. 
1. 사용자는 로컬 터미널에서 `uv tool install notebooklm-mcp-cli` 등을 통해 MCP를 설치합니다.
2. `nlm login` 명령어를 통해 본인의 구글 계정 세션을 로컬에 쿠키로 저장합니다.
3. Cline/Windsurf 설정에 해당 MCP 서버를 등록하여 제가 쓸 수 있게 해줍니다.

### [Step 2] 로컬 데이터 패키징 (Python Automation)
* **[NEW] `automation/notebooklm_prep.py` 신설**
  - 기능을 실행하면 `HarvesterV3`가 50건의 뉴스를 가져옵니다.
  - 가져온 본문과 출처 링크를 하나의 긴 마크다운 파일(`scratch/notebooklm_source.txt`)로 병합해 디스크에 저장합니다.

### [Step 3] AI Agent 오케스트레이션 (MCP Execution)
데이터 파일이 준비되면, 제가 다음 절차를 직접(자율적으로) 수행합니다:
1. `notebooklm_create_notebook(name=" Weekly Mega Trends")`
2. `notebooklm_upload_source(notebook_id, file="scratch/notebooklm_source.txt")`
3. `notebooklm_query(notebook_id, prompt="이 문서에 담긴 50개 기사를 바탕으로 IT 핵심 메타 트렌드 3가지를 도출하고, 전문가적인 리포트를 작성해줘.")`
4. 반환된 텍스트를 포맷팅하여 `content/ko/guides/` 경로에 `.md`로 자동 저장합니다.

## ⚠️ User Action Required

> [!IMPORTANT]
> **제가 2단계(Python 스크립트 제작) 작업에 착수해도 될까요?**
> 제가 스크립트를 짜는 동안, 사용자는 1단계(MCP 서버 연동)를 진행해 주셔야 이 계획이 최종적으로 무사히 작동할 수 있습니다. 
> 
> "동의합니다. 2단계 스크립트를 작성해주세요." 라고 말씀해주시면 바로 구현에 들어갑니다!
