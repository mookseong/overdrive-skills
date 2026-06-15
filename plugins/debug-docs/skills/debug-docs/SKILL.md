---
name: debug-docs
description: 버그/장애/문제를 분석할 때 사용. RCA(근본원인 분석) 문서를 쓰고 증상→가설→근본원인을 상태색 원인-결과 트리로 HTML 시각화해 로컬 서버로 띄운다. 노드를 클릭하면 증거가 보이고 상태(가설/조사중/기각/확정)를 편집·저장한다. Use when debugging or doing root cause analysis of a problem.
---

# debug-docs — RCA 원인 분석 뷰어

버그/장애를 RCA 문서 + 상태색 원인-결과 트리로 만들어 로컬 서버로 띄운다.

## 워크플로우

이 스킬 디렉토리(로드 시 base 절대경로 제공)에 `viewer/`가 있다.

1. **데이터 생성** — `<project>/docs/debug-docs/debug.json`을 아래 스키마 + RCA 뼈대로 작성.
   - `title`, `overview`(markdown), `nodes`(`id`/`label`/`status`/`detail`), `edges`(`from`/`to`/`label`)
   - `status`: `가설` / `조사중` / `기각` / `확정`(근본원인)

2. **뷰어 스캐폴딩** — `viewer/`를 프로젝트로 복사:
   ```bash
   mkdir -p <project>/docs/debug-docs
   cp -R "<이 스킬 base 경로>/viewer/." "<project>/docs/debug-docs/"
   ```

3. **실행** — `python3 <project>/docs/debug-docs/serve.py <project>/docs/debug-docs/debug.json` → 출력된 `http://localhost:8000` 안내.

4. **사용법 안내** — 노드 클릭 시 증거, 상태 색으로 진척 표시, 편집 후 "저장"이면 `debug.json`에 기록. `docs/debug-docs/`는 자기포함이라 커밋·공유 가능.

## RCA 작성 뼈대 (5 Whys + Fishbone + blameless postmortem)

### `overview` (문서 레벨, markdown 헤딩)
- `## 증상` — 무엇이/언제/어디서 관측됐나
- `## 영향` — 범위·심각도(가능하면 정량)
- `## 재현` — 절차·환경·빈도
- `## 타임라인` (선택) — 주요 이벤트 시간순
- `## 근본원인` — 확정 원인 요약
- `## 수정` — 임시(containment) + 근본(corrective)
- `## 재발방지` — 액션아이템(담당·기한·우선순위 P0/P1/P2)

### 원인 트리(nodes/edges)
- 루트 = 증상. 가지 = 가설(Fishbone). 깊이 = 왜-왜(5 Whys). 확정 노드 = 근본원인.
- `node.detail`: `## 증거`(찬/반 데이터) + `## 판단`(왜 기각/확정).
- `status`로 진척 표시(가설→조사중→기각/확정).

### 원칙
- 데이터 기반(추측 금지), blameless(사람 아닌 시스템), 표면 아닌 근본까지. 이모지 쓰지 않는다.

## self-check
- debug.json이 스키마에 맞는가(노드 id 유일, 엣지가 존재 노드 참조)?
- overview에 증상·근본원인·재발방지가 있는가?
- 가설마다 증거와 status가 있는가?
- 확정 노드(근본원인)가 있는가? viewer가 복사됐는가?
