let data = null;

function escapeHtml(s) {
  return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

let renderSeq = 0;
// 다이어그램 1개를 카드로 렌더. mermaid 코드는 스킬이 작성한 그대로 렌더하며,
// 실패해도 이 카드에만 에러를 표시하고 다른 카드/페이지는 유지한다.
async function renderDiagram(d) {
  const card = document.createElement("section");
  card.className = "card diagram-card";
  const head = document.createElement("div");
  head.className = "diagram-head";
  const typeBadge = d.type ? `<span class="type">${escapeHtml(d.type)}</span>` : "";
  head.innerHTML = `<h2>${escapeHtml(d.title || "다이어그램")}</h2>${typeBadge}`;
  card.appendChild(head);

  const holder = document.createElement("div");
  holder.className = "diagram";
  card.appendChild(holder);

  if (d.note) {
    const note = document.createElement("div");
    note.className = "note";
    note.innerHTML = marked.parse(d.note);
    card.appendChild(note);
  }
  document.getElementById("diagrams").appendChild(card);

  const code = String(d.mermaid || "").trim();
  if (!code) {
    holder.innerHTML = '<pre class="error">mermaid 코드가 비어 있습니다.</pre>';
    return;
  }
  try {
    const { svg } = await mermaid.render("dbgGraph_" + (++renderSeq), code);
    holder.innerHTML = svg;
  } catch (err) {
    holder.innerHTML =
      '<pre class="error">다이어그램 렌더 실패\n' +
      escapeHtml(err && err.message) +
      "\n\n--- mermaid ---\n" +
      escapeHtml(code) +
      "</pre>";
  }
}

async function render() {
  document.getElementById("doc-title").textContent = data.title || "debug-docs";
  const ov = document.getElementById("overview");
  if (data.overview) {
    ov.innerHTML = marked.parse(data.overview);
  } else {
    ov.style.display = "none";
  }
  const wrap = document.getElementById("diagrams");
  wrap.innerHTML = "";
  const diagrams = Array.isArray(data.diagrams) ? data.diagrams : [];
  if (!diagrams.length) {
    wrap.innerHTML = '<section class="card"><p class="muted">표시할 다이어그램이 없습니다.</p></section>';
    return;
  }
  // 순서를 유지하기 위해 직렬 렌더(고유 id가 보장되고 카드 순서가 데이터 순서와 일치).
  for (const d of diagrams) {
    await renderDiagram(d);
  }
}

async function load() {
  const res = await fetch("/api/data");
  data = await res.json();
  render();
}

mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });
load();
