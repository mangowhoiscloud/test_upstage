# Document Digitization 테스트 로그

## 1. 테스트 문서 선정
- **출처:** 미국 국세청(IRS) 공식 사이트에서 제공하는 W-9 양식(https://www.irs.gov/pub/irs-pdf/fw9.pdf)
- **이유:** 정부 배포 문서로서 저작권 제약이 없으며, 표/필드가 촘촘히 배치되어 있어 Upstage Document Digitization 기능이 처리하기에 적합한 구조화된 양식입니다.

## 2. 다운로드 및 저장 경로
```bash
mkdir -p sample/documents
curl -L -o sample/documents/irs-form-w9.pdf "https://www.irs.gov/pub/irs-pdf/fw9.pdf"
```
- 저장 파일: `sample/documents/irs-form-w9.pdf`
- 저장소에는 바이너리 파일을 커밋하지 않으므로, 테스트할 때마다 위 명령으로 직접 내려받아 사용합니다.
- 파일 특성 확인:
  ```bash
  # (선택) `file` 유틸리티가 설치되어 있다면 포맷을 확인할 수 있습니다.
  # file sample/documents/irs-form-w9.pdf
  sha256sum sample/documents/irs-form-w9.pdf
  ```

## 3. 테스트 준비
- `server/test_api.py` 또는 `examples/langchain_upstage_quickstart.py`에서 문서 경로를 `sample/documents/irs-form-w9.pdf`로 지정해 실습할 수 있습니다.
- 실제 Upstage API 테스트 시, `multipart/form-data` 업로드가 필요하므로 아래와 같은 cURL 예시를 참고합니다.
  ```bash
  curl -X POST "https://api.upstage.ai/v1/document-digitization" \
       -H "Authorization: Bearer $UPSTAGE_API_KEY" \
       -F "document=@sample/documents/irs-form-w9.pdf" \
       -F "model=document-parse" \
       -F "output_format=markdown"
  ```

## 4. 실제 API 호출 결과 (2025-09-27)
- `UPSTAGE_API_KEY`를 환경 변수로 설정한 뒤 아래 명령으로 문서를 업로드했습니다.
  ```bash
  curl -X POST "https://api.upstage.ai/v1/document-digitization" \
       -H "Authorization: Bearer $UPSTAGE_API_KEY" \
       -F "document=@sample/documents/irs-form-w9.pdf" \
       -F "model=document-parse" \
       -F "output_format=markdown" \
       -o /tmp/ocr_response.json
  ```
- 응답 요약:
  - `usage.pages`: 6
  - `content.markdown` 필드에 W-9 주요 본문과 표가 Markdown 형태로 정리되어 반환됨 (예: 헤더, 안내문, 표 형태 필드 설명).
  - layout 요소에는 각 페이지의 세부 블록이 배열 형태로 포함되어 있어 좌표 기반 후처리에도 활용 가능합니다.
- 응답은 `/tmp/ocr_response.json` 및 `./content_markdown.md`에 저장함

## 5. 한계 및 메모
- 테스트에는 실 API 키를 사용했으며, 실행 후 즉시 환경 변수에서 제거했습니다. 자동화 환경에서는 GitHub Actions Secrets나 `.env` 파일을 통한 주입을 권장합니다.
- 문서 업데이트나 다른 테스트 자료 교체 시 이 로그를 확장해 주세요.
