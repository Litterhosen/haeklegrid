import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image

# ================================
# DESIGN GRID PRO - OPTIMERET VERSION
# ================================

st.set_page_config(page_title="Design Grid Pro", layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Bredde (felter)", 5, 500, 30)
    rows = st.number_input("Højde (felter)", 5, 500, 30)
    cell_size = st.slider("Feltstørrelse (px)", 10, 80, 24)

    st.divider()
    uploaded_file = st.file_uploader("📥 Importér billede", type=["png", "jpg", "jpeg"])
    
    st.divider()
    st.info("Brug 'Panorer' værktøjet i appen for at bevæge dig rundt på mobilen.")

# --- GRID DATA GENERERING ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
    grid_data = (np.array(img) < 128).astype(int)

cells_html = ""
for r in range(rows):
    for c in range(cols):
        i = r * cols + c
        active = "active" if grid_data.flatten()[i] == 1 else ""
        cells_html += f'<div class="cell {active}" onclick="mark(this)"></div>'

# ================================
# HTML TEMPLATE (MED EKSPORT & PAN)
# ================================

grid_html = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
:root {
  --cell-size: __CELL_SIZE__px;
  --cols: __COLS__;
}

body {
  margin:0;
  font-family: -apple-system, system-ui, sans-serif;
  background:#f3f4f6;
  padding:10px;
  display: flex;
  flex-direction: column;
  height: 95vh;
}

.toolbar {
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  background:white;
  padding:12px;
  border-radius:12px;
  margin-bottom:10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  justify-content: center;
}

.viewport {
  flex: 1;
  background:#e5e7eb;
  overflow:hidden;
  border-radius:12px;
  position:relative;
  touch-action:none; /* Vigtigt for custom pan */
  border: 1px solid #ccc;
}

.canvas {
  transform-origin:0 0;
  position: absolute;
}

.grid {
  display:grid;
  grid-template-columns: repeat(var(--cols), var(--cell-size));
  gap:1px;
  background:#bbb;
  padding: 5px;
  background-color: white;
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
  font-size: calc(var(--cell-size) * 0.6px);
  user-select:none;
  -webkit-print-color-adjust: exact;
}

.cell.active { background:black !important; color:white; }

/* Værktøjs-knapper */
button, select { 
    padding:8px 12px; 
    font-weight:600; 
    border-radius:8px; 
    border:1px solid #ddd;
    background: white;
}

.btn-active { background: #2563eb !important; color: white !important; border-color: #1e40af; }
.btn-save { background: #059669; color: white; }

@media print {
    .toolbar { display: none !important; }
    body { background: white; }
    .viewport { overflow: visible; height: auto; }
    .canvas { transform: none !important; position: static; }
    .cell { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
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
  
  <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
  <button onclick="zoomIn()">＋</button>
  <button onclick="zoomOut()">－</button>
  <button class="btn-save" onclick="exportImage()">💾 Gem Foto</button>
  <button onclick="window.print()">🖨️ PDF</button>
</div>

<div class="viewport" id="viewport">
  <div class="canvas" id="canvas">
    <div class="grid" id="grid-to-export">
      __CELLS__
    </div>
  </div>
</div>

<script>
let scale = 1;
let tx = 0, ty = 0;
let isPanning = false;
let dragging = false;
let lx = 0, ly = 0;

const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

function apply() {
  canvas.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
}

function zoomIn(){ scale *= 1.2; apply(); }
function zoomOut(){ scale /= 1.2; apply(); }

function togglePan() {
    isPanning = !isPanning;
    document.getElementById('panBtn').classList.toggle('btn-active');
    viewport.style.cursor = isPanning ? 'grab' : 'default';
}

viewport.addEventListener('pointerdown', e=>{
  dragging = true; 
  lx = e.clientX; 
  ly = e.clientY;
  if(isPanning) viewport.style.cursor = 'grabbing';
});

window.addEventListener('pointermove', e=>{
  if(!dragging || !isPanning) return;
  tx += e.clientX - lx;
  ty += e.clientY - ly;
  lx = e.clientX; ly = e.clientY;
  apply();
});

window.addEventListener('pointerup', ()=>{ 
    dragging = false; 
    if(isPanning) viewport.style.cursor = 'grab';
});

function mark(el){
  if(isPanning) return; // Tegn ikke hvis vi panorerer
  const mode = document.getElementById('mode').value;
  if(mode==='fill') {
      el.classList.toggle('active');
      el.innerHTML = '';
  }
  if(mode==='erase'){ 
      el.classList.remove('active'); 
      el.innerHTML=''; 
  }
  if(mode==='X' || mode==='O'){
    el.classList.remove('active');
    el.innerHTML = el.innerHTML===mode ? '' : mode;
  }
}

async function exportImage() {
    const grid = document.getElementById('grid-to-export');
    const btn = event.target;
    btn.innerHTML = "Vent...";
    
    html2canvas(grid, {
        backgroundColor: "#ffffff",
        scale: 2, // Højere opløsning
        logging: false,
        useCORS: true
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = 'mit-design.png';
        link.href = canvas.toDataURL("image/png");
        link.click();
        btn.innerHTML = "💾 Gem Foto";
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

components.html(grid_html, height=850, scrolling=False)

st.caption("Design Grid Pro v3.0 – Med Panorering, Foto-eksport og PDF-fix.")
