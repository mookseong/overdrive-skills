---
name: flow-docs
description: 기획·요구사항·PRD를 쓰거나 기능/사용자 흐름·프로세스·구조를 정리할 때, 사람이 읽는 보고서 형태의 HTML 문서를 만들고 상황에 맞는 차트(순서도/수영선도/마인드맵/조직도/사이트맵 등)를 섹션 안에 곁들여 로컬 서버로 띄우는 용도. "PRD 써줘", "이 기획을 문서로 정리해줘", "사용자 흐름을 다이어그램으로 보여줘", "요구사항을 흐름도로 시각화해줘" 같은 요청에 발동. 두괄식 보고서 + 상황에 맞는 Mermaid 차트를 작성해 HTML로 렌더한다(보기 전용). 버그·장애·코드 디버깅 분석은 debug-docs가 담당하고, flow-docs는 기획·요구사항·프로세스 쪽이다. 기능 구현·API 작성·리팩터링이 아니라 기획·흐름을 문서로 정리할 때 쓴다. Use when writing a PRD or organizing requirements/feature/user flows as a human-readable report with situation-appropriate diagrams rendered to HTML and served locally — not for implementing the feature or refactoring code.
---

# flow-docs — 기획/PRD 보고서 + 상황별 차트 뷰어

기획·요구사항·PRD를 **사람이 읽는 보고서**로 쓰고, 그 안에 **상황에 맞는 차트**(흐름도·수영선도·마인드맵 등)를 곁들여 HTML로 보여준다. 보기 전용(빠른 렌더)이라 편집·저장은 없다.

## 워크플로우

이 스킬 디렉토리(로드 시 base 절대경로 제공)에 `viewer/`가 있다.

1. **보고서 작성** — `<project>/docs/flow-docs/prd.json`을 아래 `blocks` 스키마로 작성. 글(markdown)과 차트(Mermaid)를 **읽는 순서대로** 배치한다. PRD는 아래 "PRD 구성"을 따른다.

2. **뷰어 스캐폴딩** — `viewer/`를 프로젝트로 복사:
   ```bash
   mkdir -p <project>/docs/flow-docs
   cp -R "<이 스킬 base 경로>/viewer/." "<project>/docs/flow-docs/"
   ```

3. **실행** — `python3 <project>/docs/flow-docs/serve.py <project>/docs/flow-docs/prd.json` → 시작 시 출력되는 URL(기본 `http://localhost:8000`)을 안내. 8000이 사용 중이면 `--port 9000`처럼 바꾼다.

4. **사용법 안내** — 보고서가 위에서 아래로 읽히고, 각 섹션 아래 차트가 인라인으로 렌더된다. `docs/flow-docs/`는 자기포함이라 커밋·공유 가능(오프라인 동작).

## 데이터 스키마 (`prd.json`)

순서 있는 블록 배열로 구성한다. 블록은 글(`markdown`) 또는 차트(`chart`)다.

```json
{
  "title": "PT 예약 노쇼 감소 기능 PRD",
  "blocks": [
    { "type": "markdown", "content": "## 2. 개요\n결론부터: ..." },
    { "type": "chart", "title": "사용자 흐름", "chartType": "flowchart", "mermaid": "flowchart TD\n  ...", "note": "선택 설명" }
  ]
}
```

- `markdown` 블록: `content`(markdown). 섹션 제목·본문·표·목록.
- `chart` 블록: `mermaid`(완전한 Mermaid 정의), `title`(선택), `chartType`(선택, 배지 라벨), `note`(선택, markdown).
- 뷰어는 Mermaid를 그대로 렌더한다(빌드/이스케이프 안 함). 라벨 특수문자는 Mermaid 규칙대로 안전하게 쓴다(노드 텍스트 `["..."]`, 필요 시 `#34;`/`#60;` 엔티티).
- 잘못된 차트 1개는 그 figure에만 에러가 표시되고 나머지는 정상.

## PRD 구성 (이 항목 순서로)

PRD를 만들 때는 아래 구조를 markdown 블록 제목으로 따른다(섹션마다 두괄식).

- **1. 문서 정보** — 작성자·버전·상태 등(표로).
- **2. 개요** — 무엇을 왜 만드는지 한 문단으로(결론 먼저).
- **3. 문제 정의**
  - 3.1 데스크리서치 — 시장·경쟁·선행 사례 조사.
  - 3.2 문제 발굴 — 사용자/제도/시스템 등 관점별 원인 발굴(마인드맵 등으로 시각화).
  - 3.3 문제 검증 — 데이터·인터뷰로 문제가 실재함을 입증.
  - 3.4 문제 정의 — 핵심 문제를 한 문장으로 못 박음.
- **4. 해결 방안 및 방향**
  - 4.1 해결 방안 — 해결의 뼈대(사용자 흐름 등으로 시각화).
  - 4.2 ASIS - TOBE — 컨셉·타겟·비즈니스 모델 및 가격 정책·기능·디자인을 현행/개선으로 비교(표 + 흐름도).
  - 4.3 예상 성과 — 측정 가능한 정량 지표와 검증 방법.

## 차트 선택 가이드 (상황 → Mermaid)

상황에 맞는 차트를 고른다. 우리 뷰어의 Mermaid가 실제 렌더하는 형태로 매핑한다:

**1. 프로세스 및 흐름**
- 순서도(Flowchart): `flowchart TD/LR` — 사용자 흐름·업무 절차.
- 데이터 흐름도(DFD): `flowchart` — 처리 `[..]`, 저장소 `[(..)]`, 외부 `((..))`.
- 수영선도(Swimlane): `flowchart` + `subgraph 담당자/부서` — 누가 무엇을 하는지 구분.

**2. 구조 및 조직**
- 조직도(Org Chart): `flowchart TD` 계층.
- 마인드맵(Mind Map): `mindmap` — 주제 중심 가지치기(Mermaid 네이티브).
- 사이트맵(Sitemap): `flowchart TD` 계층 — 화면/메뉴 구조.

**3. 관계 및 데이터**
- 어골도(Fishbone): `flowchart LR` — 오른쪽 문제 노드로 원인 가지가 모이게.
- 네트워크 다이어그램: `flowchart LR` — 노드를 `---`로 연결.
- 벤 다이어그램(Venn): **Mermaid 미지원**. 집합 비교는 markdown 표나 문장으로 대체.

**그 외 유용**: 시퀀스(`sequenceDiagram`), 상태(`stateDiagram-v2`), ER(`erDiagram`), `pie`/`timeline`/`journey`.

## 보고서 문체 (두괄식·자연스럽게)

목적은 차트 나열이 아니라 **사람이 이해하는 보고서**다. (readable-docs 작법과 같은 원칙)

- 두괄식: 각 섹션·문단은 결론/핵심을 첫 문장에 둔다.
- 자연스러운 완결 문장으로 쓴다(개조식 나열만 늘어놓지 않는다). 표·목록은 보조로.
- 차트는 글을 보조한다. 차트 앞 글에서 무엇을·왜 보는지 한 줄로 안내한다.
- 데이터·근거 기반. 이모지는 쓰지 않는다.

참고 예시는 `examples/sample-prd.json`.

## self-check
- PRD 구성(1 문서정보 ~ 4.3 예상성과)을 순서대로 담았는가?
- 각 섹션이 두괄식인가, 문장이 자연스러운가?
- `blocks`가 읽는 순서대로인가(글 안내 → 관련 차트가 바로 아래)?
- 차트 타입이 상황에 맞고 각 `mermaid`가 유효한가? viewer가 복사됐는가?
