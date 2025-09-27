# Generative & AI 제품 테스트 기록

## 환경 설정
- `.env`에서 `UPSTAGE_API_KEY`를 로드하도록 `server/env_utils.py`를 구성.
- GitHub Actions는 리포지터리 시크릿 `UPSTAGE_API_KEY`를 읽어 테스트 전 검증.

## 실행 명령 및 결과

### Chat Completions (`/chat/completions`)
```bash
python server/test_api.py --mode direct --endpoint chat --message "테스트 케이스"
```
```json
{
  "id": "d436ef2d-4aeb-426d-94c5-cd77c9434c43",
  "object": "chat.completion",
  "created": 1758995606,
  "model": "solar-mini-250422",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "테스트 케이스는 소프트웨어 개발에서 프로그램의 기능을 검증하고 오류나 버그를 찾기 위해 사용되는 입력 데이터, 실행 조건, 기대 결과의 집합입니다. ..."
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 23,
    "completion_tokens": 293,
    "total_tokens": 316
  }
}
```
- 제공된 메시지에 대해 200 응답과 자연어 답변을 수신함.

### Embeddings (`/embeddings`)
```bash
python server/test_api.py --mode direct --endpoint embeddings --message "Upstage embeddings test" --model dummy-model
```
```text
HTTP error 400: {"error":{"message":"The requested model is invalid or no longer supported. You can find the list of available models on our models page at https://console.upstage.ai/docs/models.","type":"invalid_request_error","param":"","code":"invalid_request_body"}}
```
- 모델명이 필수이며 자리 표시자(`dummy-model`)는 거부됨.

### Document Digitization (`/document-digitization`)
```bash
python server/test_api.py --mode direct --endpoint ocr --model dummy-model
```
```text
HTTP error 400: {"error":{"message":"The requested model is invalid or no longer supported. You can find the list of available models on our models page at https://console.upstage.ai/docs/models.","type":"invalid_request_error","param":"","code":"invalid_request_body"}}
```
- 유효한 모델 목록 확보 필요.

### Information Extraction (`/information-extraction`)
```bash
python server/test_api.py --mode direct --endpoint extraction --model dummy-model
```
```text
HTTP error 400: {"error":{"message":"The requested model is invalid or no longer supported. You can find the list of available models on our models page at https://console.upstage.ai/docs/models.","type":"invalid_request_error","param":"","code":"invalid_request_body"}}
```
- 문서 기반 정보 추출 역시 모델 파라미터 검증 실패.
