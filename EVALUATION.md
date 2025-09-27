# Upstage 제품 체험 피드백

## 공통 준비 및 테스트 환경
- Linux (Ubuntu 22.04) 기반 컨테이너에서 Python 표준 라이브러리를 활용해 로컬 프록시 서버(`server/upstage_proxy.py`)를 구성했습니다. 해당 서버는 Upstage API 호출을 우회하여 API 키를 안전하게 관리할 수 있도록 설계했습니다.
- Upstage 콘솔에서 발급받은 `UPSTAGE_API_KEY`를 환경 변수로 설정해 실제 API를 호출했습니다. 테스트 후에는 키를 즉시 환경 변수에서 제거하고, 문서에는 GitHub Actions Secrets 또는 `.env` 기반 주입을 권장한다고 명시했습니다.

## Chat / Reasoning
- `openai` Python SDK의 OpenAI 호환 클라이언트를 사용해 `solar-pro2` 모델 스트리밍을 검증했습니다. (`examples/upstage_stream_demo.py` 참고)
- 장점: OpenAI 호환 인터페이스 덕분에 스트리밍 콜백이 바로 동작하며, `reasoning_effort`와 같은 파라미터도 동일한 형태로 전달할 수 있었습니다.
- 개선 제안: 공식 문서에 스트리밍 응답 구조와 샘플 코드가 추가되면 온보딩이 더욱 매끄러울 것 같습니다.

## Document Digitization
- `server/test_api.py --mode direct --endpoint ocr --output-format markdown --file sample/documents/irs-form-w9.pdf` 명령을 통해 공개 배포본(W-9)을 내려받아 `sample/documents/` 폴더에 둔 뒤 업로드했고, 6페이지 분량의 Markdown 결과를 확인했습니다.
- 장점: 표/본문이 Markdown으로 깔끔하게 정리되어 후속 파이프라인에 투입하기 용이했습니다. layout 배열에는 좌표 정보가 함께 포함되어 시각적 하이라이트 작업에도 활용 가치가 높습니다.
- 개선 제안: 업로드 필드명이 `document`임을 강조하고, 대용량 응답 처리에 대한 모범 사례(페이지 필터링, partial fetch 등)가 문서에 추가되면 좋겠습니다.

## Information Extraction
- `/extraction` 엔드포인트는 간단한 인보이스 텍스트를 예제로 사용하는 JSON 페이로드를 전송하도록 구현했습니다.
- 장점: 자유 형식 텍스트에서도 구조화된 정보를 추출할 수 있다는 점이 비즈니스 자동화에 적합해 보입니다.
- 개선 제안: 스키마 정의 및 필드 매핑 예제가 더 다양하게 제공되면 빠르게 프로토타이핑하는 데 도움이 될 것입니다.

## 전반적인 소감
- Playground UI 체험은 여전히 계정 인증이 필요하지만, API 호출만으로도 제품 품질을 충분히 가늠할 수 있었습니다.
- 공식 문서(`https://console.upstage.ai/docs/getting-started`)는 섹션 구성이 잘 되어 있으나, 실제 사용자들은 multipart 업로드나 스트리밍 예제를 빠르게 참고하고 싶어 합니다. 해당 내용을 문서에 보강하면 초기 설정 시간이 더 단축될 것입니다.
- 프록시 서버 샘플과 직접 호출 스크립트를 통해 로컬·CI 환경 모두에서 키를 안전하게 다루면서 제품 기능을 검증할 수 있다는 확신을 얻었습니다.
