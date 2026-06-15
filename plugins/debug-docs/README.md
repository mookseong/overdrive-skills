# debug-docs

디버그/문제 분석을 **RCA 문서 + 상태색 원인-결과 트리**로 만들어 로컬 서버로 띄우는 plugin.

## 무엇이 들어 있나

| 컴포넌트 | 역할 |
|---|---|
| **Skill** `debug-docs` | RCA 문서 + 원인 트리(`debug.json`) 생성 + 뷰어 스캐폴딩 + 실행 안내 |
| **Viewer** (`viewer/serve.py` + `app/`) | 문서·원인트리 렌더(상태별 색), 노드 선택→증거, 상태 편집→저장(POST) |

상태 색: 가설=파랑, 조사중=주황, 기각=회색, 확정(근본원인)=빨강. 근거 프레임워크: 5 Whys + Fishbone + blameless postmortem.

## 설치

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install debug-docs@overdrive-skills
```

설치 후 Claude Code 재시작. 이후 "이 버그 원인 분석해서 트리로 보여줘"처럼 요청하면 스킬이 작동한다.

## 동작

스킬이 `<project>/docs/debug-docs/`에 `debug.json` + 뷰어를 만들고 `python3 docs/debug-docs/serve.py docs/debug-docs/debug.json`로 띄운다. 노드 클릭 시 증거 표시, 상태 변경 후 저장하면 파일로 영속된다.

## 한계

- 서버는 macOS/Linux `python3` 기준(Windows는 `python` PATH 필요).
- 자동 로그/스택트레이스 파싱은 하지 않는다(스킬이 작성을 안내).
- Mermaid/marked는 오프라인용으로 동봉.
