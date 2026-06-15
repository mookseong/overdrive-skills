---
name: flow-docs
description: 기획·요구사항·기능/사용자 흐름·프로세스·절차·구조를 개발자용 HTML 문서 + 편집 가능한 흐름/구조 다이어그램으로 시각화해 로컬 서버로 띄울 때 사용. PRD 작성, "흐름/프로세스를 다이어그램으로 보여줘", "기획/요구사항을 흐름도로 시각화해줘", "이 구조 다이어그램으로 그려줘" 같은 요청에 발동. 노드를 클릭하면 그 단계 요구사항이 보이고 흐름을 편집·저장할 수 있다. 다이어그램·흐름도·구조도 전용이며 버그·장애의 원인 트리는 debug-docs가 담당한다. 기능 구현·API 작성·리팩터링이 아니라 흐름·프로세스를 문서·다이어그램으로 정리할 때만 쓴다. Use when creating a PRD or visualizing a feature/process/user/structure flow as an interactive HTML document or flow/structure diagram served locally, including when asked to lay a structure out as a diagram — not for implementing the feature or refactoring code.
---

# flow-docs — 상호작용형 PRD 뷰어

PRD를 개발자가 읽기 좋은 HTML + 편집 가능한 Mermaid 흐름으로 만들어 로컬 서버로 띄운다.

## 워크플로우

이 스킬의 디렉토리(로드 시 base 절대경로가 주어짐)에 `viewer/`가 들어 있다. 아래를 순서대로 한다.

1. **데이터 생성** — 사용자 프로젝트에 `docs/flow-docs/prd.json`을 아래 스키마로 작성한다. **내용은 아래 "PRD 작법(뼈대)"를 따른다.**
   - `title`: PRD 제목
   - `overview`: 문서 레벨 PRD (markdown)
   - `nodes`: `[{ "id", "label", "detail"(markdown 요구사항) }]`
   - `edges`: `[{ "from", "to", "label" }]` — from/to는 존재하는 노드 id

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

## PRD 작법 (뼈대)

문제를 먼저 못 박고, 측정 가능한 성공지표와 비목표를 명시한다. 간결하게(readable-docs 원칙). 이모지·이모티콘은 쓰지 않는다. 잘 알려진 PRD 프레임워크(Lenny 1-pager, Atlassian PRD, Amazon Working Backwards)가 수렴하는 뼈대다.

### `overview` — 문서 레벨 (이 순서의 markdown 헤딩으로)
- `## 문제` — 어떤 사용자/비즈니스 문제인가. **기능이 아니라 페인포인트로.**
- `## 왜 지금` — 진짜 문제라는 근거(데이터/관찰) / 지금 푸는 이유.
- `## 목표 / 비목표` — 달성할 것, 그리고 **명시적으로 안 할 것**(범위 누수 방지).
- `## 성공 지표` — 측정 가능한 지표 (예: 결제 완료율 70% → 85%).
- `## 대상` — 누구를 위해 (페르소나 / JTBD).

### `nodes[].detail` — 흐름 단계별 요구사항
각 노드는 사용자가 **결정/행동하는 한 단계**. detail에 markdown으로:
- `## 요구사항` — 유저스토리("사용자는 …하고 싶다") + 우선순위 `P0`(필수)/`P1`(중요)/`P2`(선택).
- `## 인수조건` — 체크 가능한 조건(Given/When/Then).
- `## 엣지케이스` — 실패·예외 처리.

### 흐름 분해
- 사용자가 결정/행동하는 지점마다 노드 1개.
- `edge` 라벨 = 그 전이의 행동/조건(분기).

참고 예시는 `examples/sample-prd.json`.

## self-check
- prd.json이 스키마에 맞는가(노드 id 유일, 엣지 from/to가 노드 참조)?
- `overview`에 문제 · 성공지표 · 비목표가 있는가?
- 노드 detail에 요구사항(+우선순위)과 인수조건이 있는가?
- 흐름이 실제 기능을 반영하는가?
- viewer가 프로젝트로 복사됐는가?
