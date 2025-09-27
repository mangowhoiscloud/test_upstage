# Upstage Proxy Server

이 디렉터리에는 Upstage API 테스트를 위한 간단한 프록시 서버 예제가 포함되어 있습니다. 서버는 로컬에서 실행되며, 클라이언트는 API 키를 노출하지 않고도 Chat/Reasoning, Document Digitization, Information Extraction API를 호출할 수 있습니다. `test_api.py` 스크립트를 통해 프록시로 요청을 보낼 수도 있고, 필요한 경우 Upstage 공식 엔드포인트로 직접 요청을 전달할 수도 있습니다.

## 요구 사항
- Python 3.9+
- (선택) `pip install -r requirements.txt`
- Upstage에서 발급받은 API 키 (`UPSTAGE_API_KEY` 환경변수로 설정)

## API 키 발급 및 준비
이 저장소는 외부 네트워크 자격 증명을 직접 발급받을 수 없습니다. Upstage Console에 로그인해 **My Page → API Keys** 메뉴에서 키를 발급받은 뒤, 아래와 같이 환경 변수에 설정해 주세요.

```bash
export UPSTAGE_API_KEY="<발급받은 키>"
```

필요하다면 `--api-key` 옵션으로 키를 직접 넘겨줄 수도 있습니다.

## 실행 방법
```bash
python upstage_proxy.py
```

서버는 기본적으로 `http://0.0.0.0:8080`에서 실행되며 다음 엔드포인트를 제공합니다.

| HTTP Method | 경로         | 설명                                |
|-------------|--------------|-------------------------------------|
| `GET`       | `/healthz`   | 서버 상태 확인용 엔드포인트         |
| `POST`      | `/chat`      | Upstage Chat/Reasoning API 프록시    |
| `POST`      | `/ocr`       | Document Digitization API 프록시     |
| `POST`      | `/extraction`| Information Extraction API 프록시    |

## 요청 예시
프록시로 채팅을 보낼 때는 다음과 같은 JSON을 전송합니다.

```bash
curl -X POST http://localhost:8080/chat \
     -H 'Content-Type: application/json' \
     -d '{
          "model": "solar-pro2",
           "messages": [
             {"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": "안녕하세요?"}
           ]
         }'
```

## 테스트 스크립트
`test_api.py`는 서버가 실행 중일 때 간단한 요청을 보내는 스크립트입니다. 또한 `--mode direct` 옵션을 주면 로컬 프록시를 거치지 않고 Upstage API로 직접 요청을 전송할 수 있습니다. 이때 채팅 엔드포인트는 OpenAI 호환 경로인 `https://api.upstage.ai/v1/chat/completions`로 전송됩니다.

- `--endpoint chat` 요청은 기본적으로 `solar-pro2` 모델을 사용하며, 필요하면 `--model`, `--temperature`, `--reasoning-effort` 옵션으로 세부 값을 조정할 수 있습니다. (`reasoning-effort` 기본값은 `high`)

- `--endpoint ocr` 와 `--mode direct`를 함께 사용하면 샘플 문서를 `multipart/form-data`로 업로드합니다. 기본 파일 경로는 `sample/documents/irs-form-w9.pdf`이며, 실행 전 아래 명령으로 IRS Form W-9 공개 배포본을 다운로드해 두어야 합니다. 필요하면 `--file` 옵션으로 다른 경로를 지정할 수 있습니다.

  ```bash
  curl -L -o sample/documents/irs-form-w9.pdf "https://www.irs.gov/pub/irs-pdf/fw9.pdf"
  ```
- `--output-format` 옵션을 활용하면 `markdown`, `html`, `text` 등 원하는 결과 포맷을 지정할 수 있습니다.

```bash
# 프록시 서버를 대상으로 테스트
python test_api.py --endpoint chat --message "테스트 메시지"

# Upstage 엔드포인트를 직접 호출 (API 키 필요)
python test_api.py --mode direct --endpoint chat --message "테스트 메시지"
```

이 스크립트는 네트워크 오류를 우아하게 처리하며, 실제 응답 대신 오류 메시지를 출력할 수도 있습니다. 직접 호출 모드에서 API 키가 설정되어 있지 않으면 친절하게 경고를 출력합니다.
