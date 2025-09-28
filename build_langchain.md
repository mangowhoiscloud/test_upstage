# LangChain 환경 구성 가이드

업스테이지 API 제품을 LangChain 예제와 함께 실습하기 위한 환경 구축 절차와 기본 사용법을 정리했습니다. 아래 과정을 따르면 Linux 환경(예: Ubuntu 22.04) 기준으로 Chat/Reasoning, Document Digitization, Information Extraction 시나리오를 LangChain에서 손쉽게 테스트할 수 있습니다.

## 1. 사전 준비물
- Python 3.10 이상 (예시는 3.12 기준)
- 업스테이지 API 키 (환경 변수 `UPSTAGE_API_KEY` 로 설정)
- Git 및 `make`, `curl` 등 기본 CLI 도구

## 2. 가상환경 생성
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

> **Tip:** 시스템 Python 에 직접 설치하면 다른 프로젝트와 충돌할 수 있으므로 가상환경 사용을 권장합니다.

## 3. 필수 패키지 설치
LangChain 최신 릴리스와 `langchain-upstage` 확장을 동시에 사용하려면 아래 조합이 안정적입니다.

```bash
pip install "langchain==0.3.7" "langchain-upstage==0.7.3"
```

`langchain-upstage` 패키지는 Upstage Chat/Document/Information Extraction 통합을 포함하고 있으며, 설치 시 `langchain-openai`, `langsmith`, `pypdf` 등 필요한 하위 의존성을 함께 내려받습니다.

### 선택 패키지
- `jupyterlab`: 노트북 환경에서 실험하고 싶을 때
- `python-dotenv`: `.env` 파일로 API 키 관리 시 유용

## 4. 환경 변수 설정
```bash
export UPSTAGE_API_KEY="sk-..."
```

`.env` 파일을 쓰는 경우 `python-dotenv`를 이용해 자동으로 로드할 수 있습니다.

## 5. 예제 스크립트 실행 방법
이 저장소에는 Upstage + LangChain 예제 스크립트가 `examples/langchain_upstage_quickstart.py` 로 제공됩니다. 명령형 인터페이스로 세 가지 대표 시나리오를 실습할 수 있습니다.

```bash
# 1) Chat/Reasoning
python examples/langchain_upstage_quickstart.py chat "태양 전지의 효율을 높이는 방법을 설명해 줘"
# (기본 모델은 solar-pro2이며, `--model` 옵션으로 다른 모델을 시도할 수 있습니다.)

# 2) Document Digitization (PDF, 이미지 등 업로드)
# 먼저 공개 배포본을 내려받아 `sample/documents/` 폴더에 저장하세요.
curl -L -o sample/documents/irs-form-w9.pdf "https://www.irs.gov/pub/irs-pdf/fw9.pdf"
python examples/langchain_upstage_quickstart.py parse ./sample/documents/irs-form-w9.pdf --split page --format markdown

# 3) Information Extraction
python examples/langchain_upstage_quickstart.py extract "총 금액은 120만원이고 납품일은 2024-12-01 입니다." --schema ./schemas/invoice.json
```
- 저장소에는 샘플 PDF가 포함되지 않습니다. 위 `curl` 명령으로 IRS Form W-9 공개 문서를 내려받아 `sample/documents/` 폴더에 위치시키면 곧바로 실습을 진행할 수 있습니다.

- `parse` 명령은 LangChain의 `UpstageDocumentParseLoader` 를 통해 문서를 업로드하고, 지정한 형식/분할 옵션에 맞춰 LangChain `Document` 리스트를 반환합니다.
- `extract` 명령은 Universal Information Extraction 모델에 자유 형태 텍스트와 JSON 스키마를 입력하여 결과를 JSON 으로 출력합니다.

샘플 스키마(`schemas/invoice.json`)는 아래 형태를 참고하여 직접 작성하면 됩니다.

```json
{
  "fields": [
    {"name": "total_amount", "type": "string", "description": "총 금액"},
    {"name": "delivery_date", "type": "string", "description": "납품일"}
  ]
}
```

## 6. LangChain 기본 개념 요약
- **LLM(대규모 언어 모델)**: `ChatUpstage` 처럼 언어 모델을 추상화한 객체입니다. `invoke` 또는 `stream` 메서드로 답변을 받을 수 있습니다.
- **PromptTemplate / ChatPromptTemplate**: 프롬프트를 체계적으로 구성하는 도구입니다. 자리표시자를 넣고 `.format()` 또는 체이닝으로 값을 주입합니다.
- **Chain**: 여러 컴포넌트를 파이프라인 형태로 연결해 반복 코드를 줄여줍니다. 예제 스크립트에서는 `prompt | llm | StrOutputParser()` 방식으로 체인을 정의했습니다.
- **Loader & Document**: 외부 데이터(문서, 웹 등)를 LangChain `Document` 객체로 변환하여 후속 처리에 사용합니다. `UpstageDocumentParseLoader` 가 대표적입니다.
- **Tool & Agent**: LangChain 에이전트가 외부 도구(예: 정보 추출 API)를 필요 시 호출하도록 구성할 수 있습니다. Upstage 정보 추출 모델을 LangChain 도구로 래핑하여 에이전트 워크플로에 통합할 수 있습니다.

## 7. 문제 해결 가이드
| 증상 | 점검 항목 |
| --- | --- |
| `401 Unauthorized` | `UPSTAGE_API_KEY` 값이 올바른지, 토큰에 필요한 권한이 있는지 확인 |
| `langchain_core` 버전 오류 | 설치된 `langchain` 버전이 0.3.x 인지 재확인하고, `pip install --upgrade "langchain==0.3.7"` 재실행 |
| SSL 또는 프록시 오류 | 회사망 프록시 설정이 필요하면 `HTTP_PROXY`, `HTTPS_PROXY` 환경 변수를 설정 |

## 8. 추가 학습 자료
- [LangChain 문서](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Upstage 통합 가이드](https://pypi.org/project/langchain-upstage/)
- [Upstage API 레퍼런스](https://console.upstage.ai/docs/getting-started)

위 과정을 완료하면 로컬 Linux 환경에서 LangChain 기반으로 업스테이지 주요 제품을 빠르게 체험하고, 자체 시나리오에 맞게 스크립트를 수정하거나 노트북에서 확장 실습을 진행할 수 있습니다.
