# Build & CI/CD 구성 메모

## GitHub Actions 파이프라인
- 워크플로: `.github/workflows/tests.yml`
- 주요 단계
  1. `UPSTAGE_API_KEY` 시크릿 유효성 확인 (비어 있으면 실패).
  2. `python -m py_compile server/*.py`로 문법 검증.
  3. `python server/test_api.py --mode direct --endpoint chat --message "안녕하세요"` 스모크 테스트 수행.

## 환경 변수 관리
- `.env.example` 제공: 로컬 사용자는 복사하여 실제 키를 입력.
- `.gitignore`에 `.env` 추가하여 실 키가 버전에 포함되지 않도록 차단.
- `server/env_utils.py`가 `.env`를 읽고 `UPSTAGE_API_KEY`를 로드.

## 프록시/테스트 클라이언트 개선
- 프록시(`server/upstage_proxy.py`)
  - OpenAI 호환 `/chat/completions` 엔드포인트와 기타 제품군 경로 지원.
  - 헤더·페이로드 검증 강화 및 오류 메시지 정리.
- CLI(`server/test_api.py`)
  - 엔드포인트별 필수 인자(`--model`) 검증.
  - 테스트 명령에서 실패 응답도 로그로 남겨 조사 가능하도록 처리.

## 후속 계획
- Upstage 모델 카탈로그 확보 시 자리 표시자 모델명을 실제 값으로 치환.
- 비 JSON 응답 처리 및 테스트 자동화를 위한 추가 예외 처리 개선 예정.
