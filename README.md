# overdrive-skills

AI 워크플로우를 Claude Code plugin으로 패키징한 미니 marketplace.

## 수록 plugin

| plugin | 설명 | 자세히 |
|---|---|---|
| **readable-docs** | 읽기 좋은 한국어 기술/API 문서 작법을 skill로 강제하고, 문서 저장 시 구조 누락을 잡는 hook을 둔다. | [README](plugins/readable-docs/README.md) |
| **flow-docs** | 기획·요구사항·PRD를 사람이 읽는 보고서 HTML로 만들고, 상황에 맞는 차트(순서도/수영선도/마인드맵 등)를 섹션 안에 곁들여 로컬 서버로 띄운다(보기 전용). | [README](plugins/flow-docs/README.md) |
| **debug-docs** | 디버깅 상황을 상황에 맞는 다이어그램(시퀀스/클래스/상태/플로우차트/원인트리)으로 즉시 시각화해 로컬 서버로 띄운다. 코드/설명을 분석해 가장 맞는 Mermaid 다이어그램을 그린다(보기 전용). | [README](plugins/debug-docs/README.md) |

## 설치

GitHub에서 마켓플레이스를 등록하고 plugin을 설치한다:

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install readable-docs@overdrive-skills
/plugin install flow-docs@overdrive-skills
/plugin install debug-docs@overdrive-skills
```

> private 레포면 본인 GitHub 계정에 접근 권한이 있어야 한다. 로컬에서 바로 테스트하려면 클론 경로로 등록할 수도 있다: `/plugin marketplace add <클론-경로>`.

설치 후 Claude Code를 재시작한다.
