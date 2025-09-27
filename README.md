# Upstage API Proxy 테스트 가이드

## 준비 사항
- `.env.example`을 복사해 `.env`에 `UPSTAGE_API_KEY`를 채웁니다.
- GitHub Actions에서는 동일한 이름의 시크릿을 등록하면 워크플로(`.github/workflows/tests.yml`)가 자동으로 주입합니다.

## 검증에 사용한 명령과 결과

### 1. Python 문법 검증
```bash
python -m py_compile server/*.py
```
```text
성공 (오류 없음)
```

### 2. Chat Completions 직접 호출
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
- 제공된 메시지에 대해 200 응답과 자연어 답변을 확인했습니다.

## 추가 자료
- 상세 테스트 기록: `tasks/test_generative.md`
- CI/CD 구성 메모: `tasks/build_CICD.md`
