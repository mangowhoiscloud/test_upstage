# Upstage 제품 사용 테스트

이 저장소는 Upstage의 Chat/Reasoning, Document Digitization, Information Extraction 제품을 실제 API를 통해 체험한 과정을 기록합니다.

## 실행 준비

1. Upstage 콘솔에서 API 키를 발급받고 로컬 환경 변수에 설정합니다.

   ```bash
   export UPSTAGE_API_KEY="<your-upstage-api-key>"
   ```

   > Git 저장소에는 API 키를 절대 커밋하지 마세요. 로컬 테스트 후에는 `unset UPSTAGE_API_KEY` 또는 `.env`/GitHub Actions Secrets를 활용한 안전한 주입 방식으로 되돌리세요.

2. 스트리밍 데모와 직접 호출 예제는 `openai` 파이썬 패키지에 의존하므로 필요한 경우 아래 명령으로 설치합니다.

   ```bash
   pip install openai
   ```

## 빠른 체험 가이드

- **Chat/Reasoning** – `examples/upstage_stream_demo.py`를 실행하면 `solar-pro2` 모델의 스트리밍 응답을 확인할 수 있습니다. CLI 헬퍼(`server/test_api.py --endpoint chat`) 역시 기본값으로 `solar-pro2` 모델과 `--reasoning-effort high` 구성을 사용하므로 스니펫과 동일한 환경을 재현할 수 있습니다.
- **Document Digitization** – `server/test_api.py --mode direct --endpoint ocr --file sample/documents/irs-form-w9.pdf` 명령으로 실제 문서 파싱 결과를 받을 수 있습니다. 실행 전 아래와 같이 공개 배포본을 직접 내려받아 `sample/documents/` 폴더에 저장하세요.

  ```bash
  curl -L -o sample/documents/irs-form-w9.pdf "https://www.irs.gov/pub/irs-pdf/fw9.pdf"
  ```
- **Information Extraction** – 프록시 서버(`server/upstage_proxy.py`)를 가동한 뒤 `server/test_api.py`를 이용해 구조화된 추출 응답을 검증할 수 있습니다.

상세한 테스트 절차와 평가 내용은 `tasks` 및 `EVALUATION.md`를 참고하세요.
