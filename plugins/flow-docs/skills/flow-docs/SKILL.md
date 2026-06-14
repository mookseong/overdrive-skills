---
name: flow-docs
description: PRD나 기능/사용자 흐름을 개발자용 HTML 문서 + 편집 가능한 다이어그램으로 만들어 로컬 서버로 띄울 때 사용. 노드를 클릭하면 그 단계 요구사항이 보이고 흐름을 편집·저장할 수 있다. Use when creating a PRD or visualizing a feature/user flow as an interactive HTML document served locally.
---

# flow-docs — 상호작용형 PRD 뷰어

PRD를 개발자가 읽기 좋은 HTML + 편집 가능한 Mermaid 흐름으로 만들어 로컬 서버로 띄운다.

## 워크플로우

이 스킬의 디렉토리(로드 시 base 절대경로가 주어짐)에 `viewer/`가 들어 있다. 아래를 순서대로 한다.

1. **데이터 생성** — 사용자 프로젝트에 `docs/flow-docs/prd.json`을 아래 스키마로 작성한다.
   - `title`: PRD 제목
   - `overview`: 배경·목표 (markdown)
   - `nodes`: `[{ "id", "label", "detail"(markdown 요구사항) }]`
   - `edges`: `[{ "from", "to", "label" }]` — from/to는 존재하는 노드 id
   - PRD 내용은 간결·요약·구조 원칙(readable-docs)을 따른다.

2. **뷰어 스캐폴딩** — 이 스킬의 `viewer/`를 프로젝트로 복사한다(자기포함):
   ```bash
   mkdir -p <project>/docs/flow-docs
   cp -R "<이 스킬 base 경로>/viewer/." "<project>/docs/flow-docs/"
   ```
   (`viewer/serve.py`, `viewer/app/`, `viewer/README.md`가 복사된다. `prd.json`은 1에서 만든 것을 유지.)

3. **실행** — 서버를 띄우고 URL을 안내한다:
   ```bash
   python3 <project>/docs/flow-docs/serve.py <project>/docs/flow-docs/prd.json
   ```
   출력된 `http://localhost:8000`을 브라우저로 연다.

4. **사용법 안내** — 노드 클릭 시 요구사항 표시, 편집 패널에서 노드/엣지 추가·삭제·수정 후 "저장"이면 `prd.json`에 기록된다. `docs/flow-docs/` 폴더는 자기포함이라 그대로 커밋·공유하면 팀원도 `python3 docs/flow-docs/serve.py docs/flow-docs/prd.json`으로 실행할 수 있다.

## self-check
- prd.json이 스키마에 맞는가(노드 id 유일, 엣지 from/to가 노드 참조)?
- 노드마다 detail(요구사항)을 채웠는가?
- 흐름이 실제 기능을 반영하는가?
- viewer가 프로젝트로 복사됐는가?
