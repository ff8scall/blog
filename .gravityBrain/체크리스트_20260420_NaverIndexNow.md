# 📋 체크리스트: 네이버 IndexNow 도메인별 통합 (News, Tool, Math)

## 🎯 목표
- 네이버 Search Advisor 가이드에 맞춰 `News`, `Tool`, `Math` 각 도메인별 고유 API Key 생성 및 배치
- 배포 파이프라인 종료 시 Naver IndexNow API를 호출하도록 자동화 스크립트 고도화

---

## 1단계: News 프로젝트 키 생성 및 파일 배치
- [x] **News**: Naver 전용 고유 키 생성 (32자리 HEX)
- [x] `News/static/c3a4f8e21d6b4927a7c5b1e0d3f4a6b2.txt` 저장 및 내용 확인 (완료)
- [ ] 배포 후 해당 텍스트 파일이 브라우저에서 접근 가능한지 확인 (배포 대기)

## 2단계: 공통 인덱싱 로직 고도화
- [x] `News/automation/indexnow_service.py` 수정 (완료)
    - [x] Naver 엔드포인트 추가 및 도메인별 키 매핑 (완료)
    - [x] 환경변수(.env) 기반 키 로드 로직 적용 (완료)
- [x] `nlm_orchestrator.py` 등 기존 파이프라인에서 자동 호출 확인 (완료)

## 3단계: 검증 및 모니터링
- [ ] 테스트 URL 수동 전송 후 Naver Search Advisor 응답 코드(200/202) 확인
- [ ] 텔레그램 알림에 Naver 전송 결과 포함 여부 확인

---

## 🛡️ MASC 분석 결과
- **PM**: 네이버 노출 속도 향상을 위해 3개 도메인 분리 대응 필수.
- **아키텍트**: 도메인별 키 관리를 위해 `.env` 파일에 `NAVER_INDEXNOW_KEY_NEWS`, `NAVER_INDEXNOW_KEY_TOOL` 등의 형태로 저장 권장.
- **보안**: 키 생성 규칙(16진수, 8-128자) 준수 확인.
