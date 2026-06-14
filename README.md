# claude-skills

사내 AI-native 워크플로우를 Claude Code plugin으로 패키징한 미니 marketplace.

## 수록 plugin

- **readable-docs** — AI가 만든 기술/API 문서가 장황하고 요약이 안 되는 문제를 푼다. 읽기 좋은 한국어 기술문서 작법을 skill로 인코딩하고, 문서 저장 시 구조 누락을 잡는 hook을 둔다.

## 로컬 설치 (테스트)

```bash
/plugin marketplace add /Users/limseongmuk/IdeaProjects/claude-skills
/plugin install readable-docs@claude-skills
```

> 다른 경로에 클론했다면 `marketplace add`의 경로를 본인 클론 경로로 바꾸세요. 팀 공유 시에는 사내 marketplace에 이 레포 URL을 등록합니다.

설치 후 Claude Code를 재시작한다.
