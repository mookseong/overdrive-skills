---
name: debug-docs
description: 버그·장애·에러·이상 동작을 디버깅하거나 코드 흐름·구조를 이해할 때, 상황에 맞는 다이어그램(시퀀스/클래스/상태/플로우차트/원인트리)으로 즉시 시각화하는 용도. "이 버그 왜 나는지 그림으로 보여줘", "이 호출 흐름 시퀀스로 그려줘", "이 코드 구조 다이어그램으로 정리해줘", "원인 분석해서 시각화해줘", "디버깅 상황을 한눈에 보게 해줘" 같은 요청에 발동. 코드와/또는 내 설명을 분석해 가장 맞는 Mermaid 다이어그램 1개 이상을 골라 HTML로 렌더하고 로컬 서버로 띄운다(빠른 보기 전용). 기획·요구사항·사용자 흐름 정리는 flow-docs가 담당하며, debug-docs는 버그·디버깅·코드 이해 쪽이다. 코드를 직접 고치는 핫픽스·패치가 아니라 이해를 위한 시각화일 때 쓴다. Use when debugging a bug/failure or understanding code flow/structure by visualizing it with the most fitting diagram (sequence, class, state, flowchart, or cause tree) rendered to HTML and served locally — not for patching the code itself.
---

# debug-docs — 상황 적응형 디버깅 다이어그램 뷰어

버그/장애를 디버깅하거나 코드 흐름·구조를 이해할 때, **상황에 가장 맞는 다이어그램**(시퀀스/클래스/상태/플로우차트/원인트리)을 골라 HTML로 바로 보여준다. 보기 전용(빠른 렌더)이라 편집·저장은 없다.

## 워크플로우

이 스킬 디렉토리(로드 시 base 절대경로 제공)에 `viewer/`가 있다.

1. **분석 + 데이터 생성** — 코드와/또는 사용자 설명을 분석해 `<project>/docs/debug-docs/debug.json`을 아래 스키마로 작성. 상황에 맞는 다이어그램 타입을 1개 이상 고른다(여러 관점이 필요하면 여러 개).
   - `title`, `overview`(markdown, 선택이지만 권장), `diagrams`(배열)
   - 각 diagram: `title`, `type`(라벨), `mermaid`(완전한 Mermaid 정의), `note`(markdown, 선택)

2. **뷰어 스캐폴딩** — `viewer/`를 프로젝트로 복사:
   ```bash
   mkdir -p <project>/docs/debug-docs
   cp -R "<이 스킬 base 경로>/viewer/." "<project>/docs/debug-docs/"
   ```

3. **실행** — `python3 <project>/docs/debug-docs/serve.py <project>/docs/debug-docs/debug.json` → 시작 시 출력되는 URL(기본 `http://localhost:8000`)을 안내. 8000이 사용 중이면 `--port 9000`처럼 포트를 바꾼다.

4. **사용법 안내** — 페이지에 분석 요약 + 다이어그램들이 순서대로 렌더된다. `docs/debug-docs/`는 자기포함이라 커밋·공유 가능(오프라인 동작).

## 데이터 스키마 (`debug.json`)

```json
{
  "title": "결제 승인 간헐 실패 분석",
  "overview": "## 상황\n...\n## 관찰\n...",
  "diagrams": [
    { "title": "호출 흐름", "type": "sequence", "mermaid": "sequenceDiagram\n  participant C as Client\n  C->>API: 요청\n  API-->>C: 500", "note": "선택 설명(markdown)" },
    { "title": "원인 트리", "type": "flowchart", "mermaid": "flowchart TD\n  a[\"증상\"] --> b[\"원인\"]", "note": "..." }
  ]
}
```

- `mermaid`는 스킬이 작성한 완전한 정의를 그대로 렌더한다(뷰어는 빌드/이스케이프하지 않음). 라벨에 따옴표·꺾쇠 등 특수문자가 있으면 Mermaid 규칙대로 안전하게 쓴다(예: 노드 텍스트는 `["..."]`로 감싸고, 필요하면 `#34;`/`#60;` 같은 엔티티 코드 사용).
- `type`은 화면 배지용 라벨일 뿐, 실제 렌더 종류는 `mermaid` 코드 첫 줄이 결정한다.
- 잘못된 다이어그램 1개는 그 카드에만 에러가 표시되고 나머지는 정상 렌더된다.

## 다이어그램 타입 선택 가이드

상황에 맞는 타입을 고른다(한 분석에 여러 개도 좋다):

- **sequence**(`sequenceDiagram`): 시간순 호출·메시지 흐름, 컴포넌트 간 상호작용, 순서/타이밍/레이스 버그.
- **class**(`classDiagram`): 모듈·클래스 구조와 관계, 의존성, 상속/구성 이슈.
- **state**(`stateDiagram-v2`): 상태 머신·상태 전이 버그(예: 주문/결제 상태가 잘못 전이).
- **flowchart**(`flowchart TD`): 제어 흐름·분기 로직, 또는 원인-결과 트리(왜-왜 RCA). 상태 강조가 필요하면 `classDef`로 색을 정적으로 칠한다(예: 기각=회색, 확정=빨강).
- **er**(`erDiagram`): 데이터 모델·스키마·관계 이슈.

## 원칙
- 데이터·코드 근거 기반(추측 최소화), 표면 아닌 핵심까지. 한 다이어그램에 너무 많이 담지 말고 관점별로 나눈다. 이모지 쓰지 않는다.

## self-check
- `diagrams`가 비어있지 않고 각 항목에 `title`·`mermaid`가 있는가?
- 고른 다이어그램 타입이 상황(흐름/구조/상태/원인)에 맞는가?
- 각 `mermaid`가 유효한가(첫 줄 키워드, 라벨 특수문자 처리)? viewer가 복사됐는가?
