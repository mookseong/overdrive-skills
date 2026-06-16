# flow-docs

기획·요구사항·PRD를 **사람이 읽는 보고서 형태의 HTML 문서**로 만들고, 상황에 맞는 차트를 섹션 안에 곁들여 로컬 서버로 띄우는 plugin. 보기 전용(빠른 렌더).

## 무엇이 들어 있나

| 컴포넌트 | 역할 |
|---|---|
| **Skill** `flow-docs` | 두괄식 보고서 + 상황에 맞는 Mermaid 차트(`prd.json`) 작성 + 뷰어 스캐폴딩 + 실행 안내 |
| **Viewer** (`viewer/serve.py` + `app/`) | 보고서 본문 + 인라인 차트를 빠르게 렌더(보기 전용). 잘못된 차트는 그 자리만 에러 표시 |

PRD 구성: 1 문서정보 / 2 개요 / 3 문제정의(데스크리서치·발굴·검증·정의) / 4 해결방안(해결안·ASIS-TOBE·예상성과). 차트: 순서도/수영선도/마인드맵/조직도/사이트맵/시퀀스 등 상황에 맞게.

## 설치

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install flow-docs@overdrive-skills
```

설치 후 Claude Code 재시작. 이후 "이 기획 PRD로 정리해줘", "사용자 흐름 다이어그램으로 보여줘"처럼 요청하면 스킬이 작동한다.

## 동작

스킬이 `<project>/docs/flow-docs/`에 `prd.json` + 뷰어를 만들고 `python3 docs/flow-docs/serve.py docs/flow-docs/prd.json`로 띄운다. 보고서가 위에서 아래로 읽히고 각 섹션 아래 차트가 인라인으로 표시된다.

## 한계

- 서버는 macOS/Linux `python3` 기준(Windows는 `python` PATH 필요).
- 보기 전용(편집/저장 없음). Mermaid 정확성은 스킬이 작성 시 책임진다.
- 벤 다이어그램은 Mermaid 미지원(표/문장으로 대체). Mermaid/marked는 오프라인용으로 동봉.
