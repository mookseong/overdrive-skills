# flow-docs

PRD를 **개발자가 읽기 좋은 HTML 문서 + 편집 가능한 흐름 다이어그램**으로 만들어 로컬 서버로 띄우는 plugin.

## 무엇이 들어 있나

| 컴포넌트 | 역할 |
|---|---|
| **Skill** `flow-docs` | `prd.json` 생성 + 번들 뷰어를 프로젝트로 복사 + 서버 실행 안내 |
| **Viewer** (`viewer/serve.py` + `app/`) | 문서·Mermaid 흐름 렌더, 노드 선택→요구사항, 편집→저장(POST) |

## 설치

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install flow-docs@overdrive-skills
```

설치 후 Claude Code 재시작. 이후 "이 기능 PRD를 흐름 다이어그램으로 만들어줘"처럼 요청하면 스킬이 작동한다.

## 동작

스킬이 `<project>/docs/flow-docs/`에 `prd.json` + 뷰어를 만들고 `python3 docs/flow-docs/serve.py docs/flow-docs/prd.json`로 띄운다. 노드 클릭 시 요구사항 표시, 흐름 편집 후 저장하면 파일로 영속된다.

## 한계

- 서버는 macOS/Linux `python3` 기준(Windows는 `python` PATH 필요).
- 다이어그램은 Mermaid `flowchart TD` 자동 레이아웃(드래그-드롭 편집은 아님; 편집은 패널 폼).
- Mermaid/marked는 오프라인용으로 동봉.
