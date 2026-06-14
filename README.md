# claude-skills

 워크플로우를 Claude Code plugin으로 패키징한 미니 marketplace.

## 수록 plugin

| plugin | 설명 | 자세히 |
|---|---|---|
| **readable-docs** | 읽기 좋은 한국어 기술/API 문서 작법을 skill로 강제하고, 문서 저장 시 구조 누락을 잡는 hook을 둔다. | [README](plugins/readable-docs/README.md) |
| **flow-docs** | PRD를 개발자용 HTML 문서 + 편집 가능한 흐름 다이어그램으로 만들어 로컬 서버로 띄운다. 노드 클릭 시 그 단계 요구사항을 보여주고, 흐름 편집을 파일로 저장한다. | [README](plugins/flow-docs/README.md) |

## 로컬 설치 (테스트)

```bash
/plugin marketplace add /Users/limseongmuk/IdeaProjects/claude-skills
/plugin install readable-docs@claude-skills
/plugin install flow-docs@claude-skills
```

> 다른 경로에 클론했다면 `marketplace add`의 경로를 본인 클론 경로로 바꾸세요. 팀 공유 시에는 사내 marketplace에 이 레포 URL을 등록합니다.

설치 후 Claude Code를 재시작한다.
