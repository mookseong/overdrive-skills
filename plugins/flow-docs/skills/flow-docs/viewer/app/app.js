let data = null;

function escapeHtml(s) {
  return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// marked 출력을 안전화해 host에 직접 채운다. inert한 DOMParser 문서로 파싱하므로(라이브 DOM 아님)
// 이미지 로드·스크립트가 실행되지 않는다. 위험 요소/이벤트 핸들러/style/나쁜 스킴을 제거한 뒤,
// 직렬화→재파싱(문자열 innerHTML) 없이 노드를 importNode로 그대로 채택한다 → mutation-XSS 표면 제거.
// (marked는 raw HTML 블록을 통과시키므로 <img onerror>·외부 url(style) 등을 여기서 차단한다.)
const SAFE_URL = /^(https?:|mailto:|#|\/|\.)/i;
function sanitizeInto(host, md) {
  const doc = new DOMParser().parseFromString(marked.parse(md || ""), "text/html");
  doc.querySelectorAll("script,iframe,object,embed,link,meta,style,base,form,input,button").forEach((el) => el.remove());
  doc.querySelectorAll("*").forEach((el) => {
    for (const attr of [...el.attributes]) {
      const name = attr.name.toLowerCase();
      if (name.startsWith("on") || name === "style") { el.removeAttribute(attr.name); continue; }
      if ((name === "href" || name === "src" || name === "xlink:href") && !SAFE_URL.test(attr.value.trim())) {
        el.removeAttribute(attr.name);
      }
    }
  });
  host.replaceChildren(...Array.from(doc.body.childNodes).map((n) => document.importNode(n, true)));
}

let renderSeq = 0;
// 차트 블록 1개를 figure로 렌더. mermaid 코드는 스킬이 작성한 그대로 렌더하며,
// 실패해도 이 figure에만 에러를 표시하고 보고서의 나머지는 유지한다.
async function renderChart(b, host) {
  const fig = document.createElement("figure");
  fig.className = "chart";
  if (b.title) {
    const cap = document.createElement("figcaption");
    const typeBadge = b.chartType ? `<span class="type">${escapeHtml(b.chartType)}</span>` : "";
    cap.innerHTML = `<span class="chart-title">${escapeHtml(b.title)}</span>${typeBadge}`;
    fig.appendChild(cap);
  }
  const holder = document.createElement("div");
  holder.className = "diagram";
  fig.appendChild(holder);
  if (b.note) {
    const note = document.createElement("div");
    note.className = "note";
    sanitizeInto(note, b.note);
    fig.appendChild(note);
  }
  host.appendChild(fig);

  const code = String(b.mermaid || "").trim();
  if (!code) {
    holder.innerHTML = '<pre class="error">mermaid 코드가 비어 있습니다.</pre>';
    return;
  }
  const gid = "dbgGraph_" + (++renderSeq);
  try {
    const { svg } = await mermaid.render(gid, code);
    holder.innerHTML = svg;
  } catch (err) {
    // mermaid가 렌더 실패 시 <body> 아래 남기는 임시 컨테이너(id="d"+gid)를 정리한다.
    document.getElementById("d" + gid)?.remove();
    holder.innerHTML =
      '<pre class="error">차트 렌더 실패\n' +
      escapeHtml(err && err.message) +
      "\n\n--- mermaid ---\n" +
      escapeHtml(code) +
      "</pre>";
  }
}

function renderMarkdown(b, host) {
  const sec = document.createElement("section");
  sec.className = "md";
  sanitizeInto(sec, b.content);
  host.appendChild(sec);
}

async function render() {
  document.getElementById("doc-title").textContent = data.title || "report";
  const host = document.getElementById("report");
  host.innerHTML = "";
  const blocks = Array.isArray(data.blocks) ? data.blocks : [];
  if (!blocks.length) {
    host.innerHTML = '<p class="muted">표시할 내용이 없습니다.</p>';
    return;
  }
  // 순서대로(위에서 아래로) 렌더: 마크다운 섹션과 차트가 보고서 흐름에 인라인으로 배치된다.
  for (const b of blocks) {
    if (b && b.type === "chart") {
      await renderChart(b, host);
    } else if (b && (b.type === "markdown" || typeof b.content === "string")) {
      renderMarkdown(b, host);
    } else {
      const warn = document.createElement("section");
      warn.className = "md";
      warn.innerHTML = '<pre class="error">알 수 없는 블록(무시됨)</pre>';
      host.appendChild(warn);
    }
  }
}

async function load() {
  const host = document.getElementById("report");
  try {
    const res = await fetch("/api/data");
    data = await res.json();
  } catch (err) {
    host.innerHTML =
      '<pre class="error">데이터를 불러오지 못했습니다(JSON 오류일 수 있음)\n' +
      escapeHtml(err && err.message) +
      "</pre>";
    return;
  }
  render();
}

// 보기 전용이라 클릭 바인딩이 없다 → securityLevel을 strict로 둬 라벨 내 HTML/스크립트를 인코딩(XSS 표면 축소).
mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
load();
