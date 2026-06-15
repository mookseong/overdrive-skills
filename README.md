# overdrive-skills

사내 AI-native 워크플로우를 Claude Code plugin으로 패키징한 미니 marketplace.

## 수록 plugin

| plugin | 설명 | 자세히 |
|---|---|---|
| **readable-docs** | 읽기 좋은 한국어 기술/API 문서 작법을 skill로 강제하고, 문서 저장 시 구조 누락을 잡는 hook을 둔다. | [README](plugins/readable-docs/README.md) |
| **flow-docs** | PRD를 개발자용 HTML 문서 + 편집 가능한 흐름 다이어그램으로 만들어 로컬 서버로 띄운다. 노드 클릭 시 그 단계 요구사항을 보여주고, 흐름 편집을 파일로 저장한다. | [README](plugins/flow-docs/README.md) |

## 설치

GitHub에서 마켓플레이스를 등록하고 plugin을 설치한다:

```bash
/plugin marketplace add mookseong/overdrive-skills
/plugin install readable-docs@overdrive-skills
/plugin install flow-docs@overdrive-skills
```

> private 레포면 본인 GitHub 계정에 접근 권한이 있어야 한다. 로컬에서 바로 테스트하려면 클론 경로로 등록할 수도 있다: `/plugin marketplace add <클론-경로>`.

설치 후 Claude Code를 재시작한다.
