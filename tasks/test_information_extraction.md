# Information Extraction 테스트 로그

## 1. 테스트 문서
- **문서:** IRS Form W-9 (미국 국세청 공개 배포본)
- **다운로드:**
  ```bash
  mkdir -p sample/documents
  curl -L -o sample/documents/irs-form-w9.pdf "https://www.irs.gov/pub/irs-pdf/fw9.pdf"
  ```
- **비고:** 저장소에는 원본 PDF를 커밋하지 않으며, 테스트 전마다 위 명령으로 직접 내려받습니다.

## 2. 환경 준비
- Upstage API 키를 `UPSTAGE_API_KEY` 환경 변수에 설정합니다. (테스트 후 `unset`으로 제거)
- 범용 정보 추출 SDK를 활용하기 위해 `langchain-upstage` 패키지를 설치했습니다.
  ```bash
  pip install langchain-upstage
  ```

## 3. 스키마 생성
`langchain_upstage`의 `UpstageUniversalInformationExtraction.generate_schema` 메서드를 사용해 W-9 문서에 맞는 JSON 스키마를 자동 생성했습니다.

```bash
python - <<'PY'
from langchain_upstage.universal_information_extraction import UpstageUniversalInformationExtraction
import json
extractor = UpstageUniversalInformationExtraction()
schema = extractor.generate_schema(["sample/documents/irs-form-w9.pdf"])
print(json.dumps(schema, ensure_ascii=False, indent=2))
PY
```

요약된 스키마 구조:
```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "document_schema",
    "schema": {
      "type": "object",
      "properties": {
        "formTitle": {"type": "string"},
        "revisionDate": {"type": "string"},
        "taxpayerIdentificationNumber": {"type": "string"},
        "name": {"type": "string"},
        "businessName": {"type": "string"},
        "taxClassification": {"type": "string"},
        "address": {"type": "string"},
        "exemptions": {"type": "array", "items": {"type": "string"}},
        "certification": {"type": "boolean"},
        "signature": {"type": "string"}
      }
    }
  }
}
```

## 4. 정보 추출 요청
스키마를 간소화해 W-9 핵심 필드만 남기고, `extractor.extract`를 호출했습니다.

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
message = json.loads(response["choices"][0]["message"]["content"])
confidence = json.loads(response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
print(json.dumps(message, ensure_ascii=False, indent=2))
print(json.dumps(confidence, ensure_ascii=False, indent=2))
PY
```

## 5. 응답 요약
- **모델:** `information-extract-250804`
- **토큰 사용량:** `prompt_tokens=14311`, `completion_tokens=186`, `total_tokens=14497`
- **추출 결과:**
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
- **신뢰도 메타데이터:** 모든 필드에 대해 `confidence: "low"`가 반환되었습니다. 빈 양식이라 값이 비어 있고, 인증 문단만 추출됐음을 확인했습니다.

## 6. 정리
- 테스트 종료 후 `unset UPSTAGE_API_KEY`로 환경 변수를 제거했습니다.
- W-9 샘플은 입력값이 없는 빈 서식이므로 핵심 필드 대부분이 공란으로 유지됩니다. 실제 작성된 양식을 사용하면 필드 값이 채워지는지 추가 검증이 필요합니다.
