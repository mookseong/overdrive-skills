let data = null;
let selectedId = null;

function escapeHtml(s) {
  return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function escapeAttr(s) { return escapeHtml(s).replace(/"/g, "&quot;"); }

function nodesToMermaid(d) {
  const lines = ["flowchart TD"];
  for (const n of d.nodes) {
    const label = String(n.label || n.id).replace(/"/g, "'");
    lines.push(`  ${n.id}["${label}"]`);
  }
  for (const e of d.edges) {
    if (!e.from || !e.to) continue;
    const lbl = e.label ? `|${String(e.label).replace(/"/g, "'")}|` : "";
    lines.push(`  ${e.from} -->${lbl} ${e.to}`);
  }
  for (const n of d.nodes) {
    lines.push(`  click ${n.id} call selectNode("${n.id}")`);
  }
  return lines.join("\n");
}

let renderSeq = 0;
async function renderDiagram() {
  const el = document.getElementById("diagram");
  const def = nodesToMermaid(data);
  try {
    const { svg, bindFunctions } = await mermaid.render("flowGraph_" + (++renderSeq), def);
    el.innerHTML = svg;
    if (bindFunctions) bindFunctions(el);
  } catch (err) {
    el.innerHTML = '<pre class="error">다이어그램 렌더 실패\n' + escapeHtml(err && err.message) + "</pre>";
  }
}

function renderNodeList() {
  const ul = document.getElementById("node-list");
  ul.innerHTML = "";
  for (const n of data.nodes) {
    const li = document.createElement("li");
    li.className = "node-item" + (n.id === selectedId ? " selected" : "");
    li.textContent = `${n.label || ""} (${n.id})`;
    li.dataset.id = n.id;
    li.onclick = () => selectNode(n.id);
    ul.appendChild(li);
  }
}

function selectNode(id) {
  selectedId = id;
  const n = data.nodes.find((x) => x.id === id);
  const panel = document.getElementById("detail-panel");
  panel.innerHTML = n
    ? `<h3>${escapeHtml(n.label)}</h3>` + marked.parse(n.detail || "_요구사항 없음_")
    : '<p class="muted">노드를 선택하세요.</p>';
  renderNodeList();
}

function renderEditor() {
  const c = document.getElementById("editor-controls");
  c.innerHTML = "";
  const nh = document.createElement("div");
  nh.innerHTML = "<h3>노드</h3>";
  data.nodes.forEach((n, i) => {
    const row = document.createElement("div");
    row.className = "edit-row";
    row.innerHTML =
      `<input data-k="id" value="${escapeAttr(n.id)}" placeholder="id" readonly title="id는 내부 식별자(편집 불가)">` +
      `<input data-k="label" value="${escapeAttr(n.label)}" placeholder="label">` +
      `<textarea data-k="detail" placeholder="요구사항(markdown)">${escapeHtml(n.detail || "")}</textarea>` +
      `<button data-act="del">삭제</button>`;
    row.querySelectorAll("input,textarea").forEach((inp) => {
      inp.oninput = () => { n[inp.dataset.k] = inp.value; };
      inp.onchange = () => { renderDiagram(); renderNodeList(); };
    });
    row.querySelector('[data-act="del"]').onclick = () => { data.nodes.splice(i, 1); renderAll(); };
    nh.appendChild(row);
  });
  const addN = document.createElement("button");
  addN.textContent = "+ 노드";
  addN.onclick = () => {
    let k = data.nodes.length + 1;
    while (data.nodes.some((x) => x.id === "n" + k)) k++;
    data.nodes.push({ id: "n" + k, label: "새 단계", detail: "" });
    renderAll();
  };
  nh.appendChild(addN);
  c.appendChild(nh);

  const eh = document.createElement("div");
  eh.innerHTML = "<h3>엣지</h3>";
  data.edges.forEach((e, i) => {
    const row = document.createElement("div");
    row.className = "edit-row";
    row.innerHTML =
      `<input data-k="from" value="${escapeAttr(e.from)}" placeholder="from id">` +
      `<input data-k="to" value="${escapeAttr(e.to)}" placeholder="to id">` +
      `<input data-k="label" value="${escapeAttr(e.label || "")}" placeholder="label">` +
      `<button data-act="del">삭제</button>`;
    row.querySelectorAll("input").forEach((inp) => {
      inp.oninput = () => { e[inp.dataset.k] = inp.value; };
      inp.onchange = () => { renderDiagram(); };
    });
    row.querySelector('[data-act="del"]').onclick = () => { data.edges.splice(i, 1); renderAll(); };
    eh.appendChild(row);
  });
  const addE = document.createElement("button");
  addE.textContent = "+ 엣지";
  addE.onclick = () => { data.edges.push({ from: "", to: "", label: "" }); renderAll(); };
  eh.appendChild(addE);
  c.appendChild(eh);
}

function renderAll() { renderDiagram(); renderNodeList(); renderEditor(); }

function render() {
  document.getElementById("prd-title").textContent = data.title || "flow-docs";
  document.getElementById("overview").innerHTML = marked.parse(data.overview || "");
  renderAll();
}

async function save() {
  const status = document.getElementById("save-status");
  status.textContent = "저장 중...";
  try {
    const res = await fetch("/api/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const j = await res.json().catch(() => ({}));
    status.textContent = res.ok
      ? "저장됨 ✓"
      : "실패: " + (j.details ? j.details.join(", ") : j.error || res.status);
  } catch (e) {
    status.textContent = "실패: " + e.message;
  }
}

async function load() {
  const res = await fetch("/api/data");
  data = await res.json();
  render();
}

window.selectNode = selectNode;
mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });
document.getElementById("save-btn").onclick = save;
load();
