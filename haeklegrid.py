import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v7 (Mobilmenu + bedre PDF)", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
.main .block-container {padding: 0px !important;}
body { background: #1a252f; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

html_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
  .line-mode-instructions {
    position: fixed;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 6px 12px;
    font-size: 13px;
    border-radius: 8px;
    display: none;
    z-index: 9999;
  }
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
  <div class="topbar">
    <button class="btn-text" onclick="togglePanel()" title="Åbn/luk menu">☰ Menu</button>

    <select id="mode" class="mode" title="Vælg hvad du vil tegne">
      <option value="fill">⚫ Fyld (sort)</option>
      <option value="X">❌ X-maske</option>
      <option value="O">⭕ O-maske</option>
      <option value="erase">🧽 Viskelæder</option>
      <option value="line">📏 Streg</option>
    </select>

    <select id="symbolPicker" class="symbol-picker" title="Specialsymboler">
      <option value="">🔣</option>
      <option value="▪">▪</option>
      <option value="▓">▓</option>
      <option value="↘">↘</option>
      <option value="✶">✶</option>
      <option value="⋆">⋆</option>
      <option value="✿">✿</option>
    </select>

    <input type="color" id="colorPicker" class="color-pick" title="Vælg farve" value="#000000" />

    <button class="btn-icon" onclick="undo()" title="Fortryd">↩️</button>
    <button class="btn-icon" onclick="redo()" title="Gendan">↪️</button>
    <div class="spacer"></div>
    <button class="btn-text btn-green" onclick="exportPDF()" title="Gem som PDF">📄 PDF</button>
    <button class="btn-icon" onclick="toggleHelp()" title="Hjælp">❓</button>
  </div>
</div>

<div class="line-mode-instructions" id="lineHint">Tryk to steder for at tegne streg mellem felter</div>

<script>
  const modeSelect = document.getElementById("mode");
  const symbolSelect = document.getElementById("symbolPicker");
  const colorInput = document.getElementById("colorPicker");
  const lineHint = document.getElementById("lineHint");

  let lineStart = null;

  symbolSelect.addEventListener("change", () => {
    if (symbolSelect.value) {
      modeSelect.value = symbolSelect.value;
    }
  });

  colorInput.addEventListener("change", () => {
    if (modeSelect.value === "fill") {
      modeSelect.value = colorInput.value;
    }
  });

  modeSelect.addEventListener("change", () => {
    if (modeSelect.value === "line") {
      lineHint.style.display = "block";
    } else {
      lineHint.style.display = "none";
      lineStart = null;
    }
  });

  function drawLine(r1, c1, r2, c2, value) {
    const dr = Math.abs(r2 - r1);
    const dc = Math.abs(c2 - c1);
    const steps = Math.max(dr, dc);

    for (let i = 0; i <= steps; i++) {
      const r = Math.round(r1 + ((r2 - r1) * i) / steps);
      const c = Math.round(c1 + ((c2 - c1) * i) / steps);
      gridData[r][c] = value;
    }
  }

  canvas.addEventListener("pointerdown", (e) => {
    const mode = modeSelect.value;
    if (mode !== "line") return;

    const cell = getCellFromClient(e.clientX, e.clientY);
    if (cell.r >= 0 && cell.c >= 0 && cell.r < ROWS && cell.c < COLS) {
      if (!lineStart) {
        lineStart = cell;
      } else {
        saveHistory();
        drawLine(lineStart.r, lineStart.c, cell.r, cell.c, "✶");
        draw(); autoSave();
        lineStart = null;
      }
    }
  });
</script>

</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
