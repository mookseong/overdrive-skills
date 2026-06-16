# debug-docs

디버깅 상황을 **상황에 맞는 다이어그램**(시퀀스/클래스/상태/플로우차트/원인트리)으로 즉시 시각화해 로컬 서버로 띄우는 plugin. 보기 전용(빠른 렌더).

## 무엇이 들어 있나

| 컴포넌트 | 역할 |
|---|---|
| **Skill** `debug-docs` | 코드/설명을 분석해 상황에 맞는 Mermaid 다이어그램(`debug.json`) 작성 + 뷰어 스캐폴딩 + 실행 안내 |
| **Viewer** (`viewer/serve.py` + `app/`) | 분석 요약 + 다이어그램 N종을 빠르게 렌더(보기 전용). 잘못된 다이어그램은 그 카드만 에러 표시 |

다이어그램 선택: 시퀀스(호출 흐름) / 클래스(구조) / 상태(상태 전이) / 플로우차트(로직·원인 트리) / ER(데이터). 한 분석에 여러 관점을 함께 담을 수 있다.

## 설치

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install debug-docs@overdrive-skills
```

설치 후 Claude Code 재시작. 이후 "이 버그 왜 나는지 그림으로 보여줘", "이 호출 흐름 시퀀스로 그려줘"처럼 요청하면 스킬이 작동한다.

## 동작

스킬이 `<project>/docs/debug-docs/`에 `debug.json` + 뷰어를 만들고 `python3 docs/debug-docs/serve.py docs/debug-docs/debug.json`로 띄운다. 코드와/또는 내 설명을 입력으로 받아 상황에 맞는 다이어그램을 그린다.

## 한계

- 서버는 macOS/Linux `python3` 기준(Windows는 `python` PATH 필요).
- 보기 전용(편집/저장 없음). Mermaid 정확성은 스킬이 작성 시 책임진다.
- 자동 코드 파싱 엔진은 아니다(스킬이 코드를 읽고 사람처럼 판단해 작성). Mermaid/marked는 오프라인용으로 동봉.
