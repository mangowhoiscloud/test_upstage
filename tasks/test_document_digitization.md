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
- 전체 응답은 `/tmp/ocr_response.json`에 저장했고, 필요 시 `jq -r '.content.markdown' /tmp/ocr_response.json | head` 명령으로 일부만 확인했습니다.

### 4.1 `content.markdown` 전체 본문
# Form W-9 (Rev. October 2018)
## Request for Taxpayer Identification Number and Certification
### Department of the Treasury  Internal Revenue Service

> ▶ Go to www.irs.gov/FormW9 for instructions and the latest information.
> ▶ Give Form to the requester. Do not send to the IRS.

| Print or type | See Specific Instructions on page 3. |
| --- | --- |
| 1 Name (as shown on your income tax return). Name is required on this line; do not leave this line blank. | |
| 2 Business name/disregarded entity name, if different from above | |
| 3 Check appropriate box for federal tax classification of the person whose name is entered on line 1. Check only one of the following seven boxes. | \[ \] Individual/sole proprietor or single-member LLC  \[ \] C Corporation  \[ \] S Corporation  \[ \] Partnership  \[ \] Trust/estate  \[ \] Limited liability company. Enter the tax classification (C=C corporation, S=S corporation, P=partnership) ➤ ____  \[ \] Other (see instructions) ➤ ____ |
| 4 Exemptions (codes apply only to certain entities, not individuals; see instructions on page 3): | Exempt payee code (if any) _______  Exemption from FATCA reporting code (if any) _______ |
| 5 Address (number, street, and apt. or suite no.) | |
| 6 City, state, and ZIP code | |
| 7 List account number(s) here (optional) | |

### Part I Taxpayer Identification Number (TIN)
Provide your TIN in the appropriate box. The TIN provided must match the name given on line 1 to avoid backup withholding. For individuals, this is generally your social security number (SSN). However, for a resident alien, sole proprietor, or disregarded entity, see the instructions for Part I, later. For other entities, it is your employer identification number (EIN). If you do not have a number, see How to get a TIN, later.

| Social security number | Employer identification number |
| --- | --- |
| \_\_\_ - \_\_ - \_\_\_\_ | \_\_ - \_\_\_\_\_\_ |

### Part II Certification
Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number (or I am waiting for a number to be issued to me); and
2. I am not subject to backup withholding because: (a) I am exempt from backup withholding, or (b) I have not been notified by the Internal Revenue Service (IRS) that I am subject to backup withholding as a result of a failure to report all interest or dividends, or (c) the IRS has notified me that I am no longer subject to backup withholding; and
3. I am a U.S. citizen or other U.S. person (defined below); and
4. The FATCA code(s) entered on this form (if any) indicating that I am exempt from FATCA reporting is correct.

**Certification instructions.** You must cross out item 2 above if you have been notified by the IRS that you are currently subject to backup withholding because you have failed to report all interest and dividends on your tax return. For real estate transactions, item 2 does not apply. For mortgage interest paid, acquisition or abandonment of secured property, cancellation of debt, contributions to an individual retirement arrangement (IRA), and generally, payments other than interest and dividends, you are not required to sign the certification, but you must provide your correct TIN. See the instructions for Part II, later.

Signature of U.S. person ➤ ___________________________    Date ➤ ____________

---

## General Instructions
Section references are to the Internal Revenue Code unless otherwise noted.
Future developments. For the latest information about developments related to Form W-9 and its instructions, such as legislation enacted after they were published, go to www.irs.gov/FormW9.

Purpose of Form. A person who is required to file an information return with the IRS must obtain your correct taxpayer identification number (TIN) to report, for example, income paid to you, real estate transactions, mortgage interest you paid, acquisition or abandonment of secured property, cancellation of debt, or contributions you made to an IRA.

A. Definition of a U.S. person. For federal tax purposes, you are considered a U.S. person if you are:
- An individual who is a U.S. citizen or U.S. resident alien;
- A partnership, corporation, company, or association created or organized in the United States or under the laws of the United States;
- An estate (other than a foreign estate); or
- A domestic trust (as defined in Regulations section 301.7701-7).

B. The requester of Form W-9 must withhold 24% of reportable payments for backup withholding if you do not furnish your TIN.

## Specific Instructions
See page 3 of the official form for detailed line-by-line directions including:
- Line 1 name requirements for disregarded entities
- Federal tax classification definitions for LLCs and corporations
- Exemption code lists for payments subject to backup withholding
- Guidance on Part I TIN entry and Part II certification scenarios

## Sign Here
Signature of U.S. person ➤ ___________________________    Date ➤ ____________

## 5. 한계 및 메모
- 테스트에는 실 API 키를 사용했으며, 실행 후 즉시 환경 변수에서 제거했습니다. 자동화 환경에서는 GitHub Actions Secrets나 `.env` 파일을 통한 주입을 권장합니다.
- 문서 업데이트나 다른 테스트 자료 교체 시 이 로그를 확장해 주세요.
