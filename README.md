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
- **Information Extraction** – 범용 추출 모델(`information-extract`)을 사용하면 W-9와 같은 문서에서 원하는 필드를 JSON으로 받을 수 있습니다.
  1. 의존성을 설치합니다. `pip install langchain-upstage`
  2. `export UPSTAGE_API_KEY="<your-upstage-api-key>"`
  3. 아래 스니펫으로 스키마를 생성하거나 수정한 뒤 추출을 실행합니다.

     ```bash
     python - <<'PY'
     from langchain_upstage.universal_information_extraction import UpstageUniversalInformationExtraction
     import json

     extractor = UpstageUniversalInformationExtraction()
     schema = {
         "type": "json_schema",
         "json_schema": {
             "name": "w9_form",
             "schema": {
                 "type": "object",
                 "properties": {
                     "name": {"type": "string", "description": "Name shown on line 1."},
                     "businessName": {"type": "string", "description": "Business/disregarded entity name on line 2."},
                     "taxClassification": {"type": "string", "description": "Selected federal tax classification."},
                     "address": {"type": "string", "description": "Address including city, state, ZIP."},
                     "tin": {"type": "string", "description": "Taxpayer identification number (SSN or EIN)."},
                     "certification": {"type": "string", "description": "Certification text summary."}
                 }
             }
         }
     }

     response = extractor.extract(["sample/documents/irs-form-w9.pdf"], response_format=schema)
     print(json.dumps(json.loads(response["choices"][0]["message"]["content"]), ensure_ascii=False, indent=2))
     PY
     ```

     빈 W-9 양식으로 테스트했을 때 결과는 다음과 같습니다. 비어 있는 필드는 공란으로 유지되고, 인증 문단만 전체 텍스트가 추출됩니다.

     ```json
     {
       "name": "",
       "businessName": "",
       "taxClassification": "",
       "address": "",
       "tin": "",
       "certification": "Under penalties of perjury, I certify that:\n1. The number shown on this form is my correct taxpayer identification number (or I am waiting for a number to be issued to me); and\n2. I am not subject to backup withholding because (a) I am exempt from backup withholding, or (b) I have not been notified by the Internal Revenue Service (IRS) that I am subject to backup withholding as a result of a failure to report all interest or dividends, or (c) the IRS has notified me that I am no longer subject to backup withholding; and\n3. I am a U.S. citizen or other U.S. person (defined below); and\n4. The FATCA code(s) entered on this form (if any) indicating that I am exempt from FATCA reporting is correct."
     }
     ```

     자세한 실행 로그는 `tasks/test_information_extraction.md`에서 확인할 수 있습니다.
상세한 테스트 절차와 평가 내용은 `tasks` 및 `EVALUATION.md`를 참고하세요.
