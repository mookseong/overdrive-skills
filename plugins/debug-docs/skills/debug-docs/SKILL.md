---
name: debug-docs
description: 버그·장애·에러·이상 동작을 디버깅하거나 코드 흐름·구조를 이해할 때, 사람이 읽는 보고서 형태의 HTML 문서를 만들고 상황에 맞는 차트(순서도/시퀀스/클래스/상태/어골도/마인드맵 등)를 섹션 안에 곁들여 로컬 서버로 띄우는 용도. "이 버그 원인 분석해서 보고서로 정리해줘", "이 호출 흐름 시퀀스로 그려줘", "이 코드 구조 다이어그램으로 보여줘", "장애 분석 문서 만들어줘" 같은 요청에 발동. 코드와/또는 내 설명을 분석해 두괄식 보고서 + 상황에 맞는 Mermaid 차트를 작성하고 HTML로 렌더한다(보기 전용). 기획·요구사항·PRD는 flow-docs가 담당하고, debug-docs는 버그·디버깅·코드 이해 쪽이다. 코드를 직접 고치는 핫픽스·패치가 아니라 분석·설명을 위한 문서화일 때 쓴다. Use when debugging a bug/failure or understanding code, by writing a human-readable report with situation-appropriate diagrams rendered to HTML and served locally — not for patching the code itself.
---

# debug-docs — 디버깅 보고서 + 상황별 차트 뷰어

버그/장애를 디버깅하거나 코드 흐름·구조를 이해할 때, **사람이 읽는 보고서**를 쓰고 그 안에 **상황에 맞는 차트**를 곁들여 HTML로 보여준다. 보기 전용(빠른 렌더)이라 편집·저장은 없다.

## 워크플로우

이 스킬 디렉토리(로드 시 base 절대경로 제공)에 `viewer/`가 있다.

1. **분석 + 보고서 작성** — 코드와/또는 사용자 설명을 분석해 `<project>/docs/debug-docs/debug.json`을 아래 `blocks` 스키마로 작성. 글(markdown)과 차트(Mermaid)를 **읽는 순서대로** 배치한다. 한 섹션을 설명하는 글 바로 아래에 그 섹션의 차트를 둔다.

2. **뷰어 스캐폴딩** — `viewer/`를 프로젝트로 복사:
   ```bash
   mkdir -p <project>/docs/debug-docs
   cp -R "<이 스킬 base 경로>/viewer/." "<project>/docs/debug-docs/"
   ```

3. **실행** — `python3 <project>/docs/debug-docs/serve.py <project>/docs/debug-docs/debug.json` → 시작 시 출력되는 URL(기본 `http://localhost:8000`)을 안내. 8000이 사용 중이면 `--port 9000`처럼 포트를 바꾼다.

4. **사용법 안내** — 보고서가 위에서 아래로 읽히고, 각 섹션 아래 차트가 인라인으로 렌더된다. `docs/debug-docs/`는 자기포함이라 커밋·공유 가능(오프라인 동작).

## 데이터 스키마 (`debug.json`)

순서 있는 블록 배열로 구성한다. 블록은 글(`markdown`) 또는 차트(`chart`)다.

```json
{
  "title": "결제 승인 간헐 실패 분석 보고서",
  "blocks": [
    { "type": "markdown", "content": "## 개요\n결론부터: ..." },
    { "type": "chart", "title": "원인 분류(어골도)", "chartType": "fishbone", "mermaid": "flowchart LR\n  ...", "note": "선택 설명(markdown)" },
    { "type": "markdown", "content": "## 조치\n..." }
  ]
}
```

- `markdown` 블록: `content`(markdown). 보고서 본문·섹션 제목·표·목록.
- `chart` 블록: `mermaid`(완전한 Mermaid 정의, 스킬이 작성), `title`(선택), `chartType`(선택, 화면 배지 라벨), `note`(선택, markdown).
- 뷰어는 Mermaid를 빌드/이스케이프하지 않고 그대로 렌더한다. 라벨에 특수문자가 있으면 Mermaid 규칙대로 안전하게 쓴다(노드 텍스트는 `["..."]`로 감싸고, 필요하면 `#34;`/`#60;` 같은 엔티티 코드 사용).
- 잘못된 차트 1개는 그 figure에만 에러가 표시되고 보고서의 나머지는 정상이다.

## 차트 선택 가이드 (상황 → Mermaid)

상황에 맞는 차트를 고른다. 한 보고서에 여러 종류를 섞어도 좋다. 우리 뷰어의 Mermaid가 실제 렌더하는 형태로 매핑한다:

**1. 프로세스 및 흐름**
- 순서도(Flowchart): `flowchart TD/LR` — 논리·업무 절차(시작/처리/조건).
- 데이터 흐름도(DFD): `flowchart` — 처리는 `[..]`, 데이터 저장소는 `[(..)]`, 외부는 `((..))`로.
- 수영선도(Swimlane): `flowchart` + `subgraph 담당자` — 담당/부서별로 subgraph를 나눠 누가 무엇을 하는지 구분.

**2. 구조 및 조직**
- 조직도(Org Chart): `flowchart TD` 계층(상위→하위).
- 마인드맵(Mind Map): `mindmap` — 핵심 주제 중심으로 가지치기(Mermaid 네이티브).
- 사이트맵(Sitemap): `flowchart TD` 계층 — 화면/메뉴 구조.

**3. 관계 및 데이터**
- 어골도(Fishbone/Ishikawa): `flowchart LR` — 오른쪽에 문제 노드, 왼쪽에서 원인 가지가 모이게.
- 네트워크 다이어그램: `flowchart LR`(또는 `graph`) — 장비/노드를 `---`로 연결.
- 벤 다이어그램(Venn): **Mermaid 미지원**. 집합 비교는 markdown 표나 문장으로 대체한다.

**그 외 유용**: 시퀀스(`sequenceDiagram`, 호출·메시지 흐름/타이밍), 클래스(`classDiagram`, 구조·의존성), 상태(`stateDiagram-v2`, 상태 전이), ER(`erDiagram`, 데이터 모델), `pie`/`timeline`도 쓸 수 있다.

## 보고서 문체 (두괄식·자연스럽게)

목적은 차트 나열이 아니라 **사람이 이해하는 보고서**다. (readable-docs 작법과 같은 원칙)

- 두괄식: 각 섹션·문단은 결론/핵심을 첫 문장에 둔다("결론부터 말하면 ...").
- 자연스러운 완결 문장으로 쓴다(개조식 나열만 늘어놓지 않는다). 표·목록은 보조로.
- 차트는 글을 보조한다. 차트 앞 글에서 "무엇을·왜" 보는지 한 줄로 안내하고, 필요하면 `note`로 해석을 덧붙인다.
- 한 차트에 너무 많이 담지 말고 관점별로 나눈다. 데이터·코드 근거 기반, 추측은 최소화. 이모지는 쓰지 않는다.

## self-check
- `blocks`가 읽는 순서대로 배치됐는가(글로 안내 → 관련 차트가 바로 아래)?
- 각 섹션이 두괄식인가, 문장이 자연스러운가?
- 고른 차트 타입이 상황(흐름/구조/관계/원인)에 맞고, 각 `mermaid`가 유효한가(첫 줄 키워드, 라벨 특수문자 처리)?
- 벤 다이어그램이 필요하면 표/문장으로 대체했는가? viewer가 복사됐는가?
