# News Project SEO Optimization Task Board

뉴스 사이트(`news.lego-sia.com`)의 검색 엔진 최적화 및 기술적 결함 해결을 위한 체크리스트입니다.

## 🏁 태스크 체크리스트

### 1. 크롤링 차단 해제 (Critical)
- [x] `layouts/robots.txt` 수정: `Disallow: /tags/` 제거 및 `Allow: /tags/` 추가 (완료: 2026-04-12)
- [x] `static/robots.txt`와 일관성 확인 (완료: 2026-04-12)

### 2. 다중 H1 태그 해결 (Notice)
- [x] **홈 화면**: `header.html`의 로고 `h1` 태그 제거 (완료: 2026-04-12)
- [x] **홈 화면**: `index.html` 본문의 지능 지수 섹션을 유일한 `h1`으로 유지 (검색기 결과 유일함 확인)
- [x] **포스트 페이지**: AI가 본문 마크다운 첫 줄에 생성하는 `# Title` 제거 로직 구현 (`ai_news_editor.py`에 반영)
- [x] **기존 포스트 정리**: 이미 생성된 마크다운 파일들(184개 중 11개 수정)에서 중복 `# 제목` 삭제 스크립트 실행 완료

### 3. 제목 길이 최적화 (Warning)
- [x] `ai_news_editor.py` 프롬프트 수정: 제목 길이를 공백 포함 영문 65자(한글 35자) 이내로 제한 (완료)
- [x] `ai_news_editor.py`에 제목 길이 강제 트리밍 로직 추가 (완료)

### 4. 배포 및 검증
- [x] 로컬 빌드 테스트 (`hugo`)로 결과물 HTML 구조 검사 (완료: 빌드 성공 및 H1 유일성 확인)
- [ ] 변경 사항 배포 (GitHub Actions) - 커밋 필요
- [ ] Bing Webmaster Tools에서 URL 재검사 요청

---
*시작 시간: 2026-04-12 12:51*
*상태: 주요 기술적 이슈 해결 완료. 배포 대기 중.*
