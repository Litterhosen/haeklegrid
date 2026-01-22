import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image

# =====================================================
# DESIGN GRID PRO — FINAL SAFE TEMPLATE
# ✔ Ingen f-strings i HTML/JS
# ✔ Zoom, pan, fit-to-screen
# ✔ PNG-eksport (html2canvas)
# ✔ Print / PDF
# =====================================================

st.set_page_config(page_title="Design Grid Pro", layout="wide")

with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Bredde (felter)", 5, 400, 30)
    rows = st.number_input("Højde (felter)", 5, 400, 30)
    cell_size = st.slider("Feltstørrelse (px)", 8, 80, 24)

    st.divider()
    uploaded_file = st.file_uploader("📥 Importér billede", type=["png", "jpg", "jpeg"])

# --- GRID DATA ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
    grid_data = (np.array(img) < 128).astype(int)

cells_html = ""
for r in range(rows):
    for c in range(cols):
        i = r * cols + c
        active = "active" if grid_data.flatten()[i] == 1 else ""
        cells_html += f'<div class="cell {active}" data-row="{r}" data-col="{c}" tabindex="0" onclick="mark(this)"></div>'

# ================================
# SAFE HTML TEMPLATE
# ================================

grid_html = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
:root {
  --cell-size: __CELL_SIZE__px;
  --cols: __COLS__;
}

body {
  margin:0;
  font-family: system-ui, sans-serif;
  background:#f3f4f6;
  padding:10px;
}

.toolbar {
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  background:white;
  padding:10px;
  border-radius:10px;
  margin-bottom:10px;
  position:sticky;
  top:0;
  z-index:10;
}

.viewport {
  height:80vh;
  background:#e5e7eb;
  overflow:hidden;
  border-radius:10px;
  position:relative;
  touch-action:none;
}

.canvas {
  transform-origin:0 0;
}

.grid {
  display:grid;
  grid-template-columns: repeat(var(--cols), var(--cell-size));
  gap:1px;
  background:#999;
}

.cell {
  width:var(--cell-size);
  height:var(--cell-size);
  background:white;
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:bold;
  user-select:none;
}

.cell.active { background:black; color:white; }
.cell:focus { outline:2px solid #2563eb; }

button, select {
  padding:6px 10px;
  font-weight:600;
}

@media print {
  .toolbar { display:none; }
  body { background:white; }
  .cell.active { background:black !important; }
}
</style>
</head>
<body>

<div class="toolbar">
  <select id="mode">
    <option value="fill">⚫ Fyld</option>
    <option value="X">❌ X</option>
    <option value="O">⭕ O</option>
    <option value="erase">⚪ Slet</option>
  </select>
  <button onclick="zoomIn()">＋</button>
  <button onclick="zoomOut()">－</button>
  <button onclick="fit()">Fit</button>
  <button onclick="download()">💾 PNG</button>
  <button onclick="window.print()">🖨️ PDF</button>
</div>

<div class="viewport" id="viewport">
  <div class="canvas" id="canvas">
    <div class="grid" id="grid">
      __CELLS__
    </div>
  </div>
</div>

<script>
let scale = 1;
let tx = 0, ty = 0;
let dragging = false;
let lx = 0, ly = 0;

const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

function apply() {
  canvas.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
}

function zoomIn(){ scale = Math.min(4, scale + 0.1); apply(); }
function zoomOut(){ scale = Math.max(0.2, scale - 0.1); apply(); }

function fit(){ scale = 1; tx = 0; ty = 0; apply(); }

viewport.addEventListener('pointerdown', e=>{ dragging = true; lx = e.clientX; ly = e.clientY; });
viewport.addEventListener('pointermove', e=>{
  if(!dragging) return;
  tx += e.clientX - lx;
  ty += e.clientY - ly;
  lx = e.clientX; ly = e.clientY;
  apply();
});
viewport.addEventListener('pointerup', ()=> dragging=false);

viewport.addEventListener('wheel', e=>{
  if(e.ctrlKey){ e.preventDefault(); scale *= e.deltaY < 0 ? 1.1 : 0.9; apply(); }
}, {passive:false});

function mark(el){
  const mode = document.getElementById('mode').value;
  if(mode==='fill') el.classList.toggle('active');
  if(mode==='erase'){ el.classList.remove('active'); el.innerHTML=''; }
  if(mode==='X' || mode==='O'){
    el.classList.remove('active');
    el.innerHTML = el.innerHTML===mode ? '' : mode;
  }
}

function download(){
  const grid = document.getElementById('grid');
  html2canvas(grid, {scale:2, backgroundColor:'#ffffff'}).then(c=>{
    const a = document.createElement('a');
    a.download = 'design-grid.png';
    a.href = c.toDataURL('image/png');
    a.click();
  });
}
</script>

</body>
</html>
"""

# --- PLACEHOLDER ERSTATNING ---
grid_html = (grid_html
    .replace("__COLS__", str(cols))
    .replace("__CELL_SIZE__", str(cell_size))
    .replace("__CELLS__", cells_html)
)

components.html(grid_html, height=900, scrolling=False)

st.caption("Design Grid Pro — Final SAFE template med zoom, pan, PNG & PDF eksport")
