import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image

# Konfiguration af siden
st.set_page_config(page_title="Design Grid Pro", layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR: INDSTILLINGER & IMPORT ---
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Bredde (felter)", 5, 500, 30)
    rows = st.number_input("Højde (felter)", 5, 500, 30)
    cell_size = st.slider("Feltstørrelse (Zoom) — basisstørrelse (px)", 6, 160, 25)

    st.divider()
    st.header("📥 Import")
    st.write("Tag et billede af din skitse eller upload en fil:")
    uploaded_file = st.file_uploader("Vælg billede", type=["png", "jpg", "jpeg"]) 

    st.divider()
    st.info("Tryk uden for denne menu for at lukke den på mobil.")

# --- LOGIK TIL BILLEDE-IMPORT ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    img = Image.open(uploaded_file).convert('L').resize((cols, rows), Image.NEAREST)
    grid_data = (np.array(img) < 128).astype(int)

# --- HOVEDSKÆRM ---
st.title("🎨 Multi-Grid Designer — Forbedret zoom & navigation")

# Beskyt mod alt for høje komponenthøjder i Streamlit
component_height = min(1200, rows * cell_size + 360)

# Byg HTML/JS med forbedringer: zoom (slider + +/-), pan (drag), fit-to-screen, keyboard navigation
# Bemærk: vi holder al styling + script i én string for at indsætte i components.html
cells_html = ''
for r in range(rows):
    for c in range(cols):
        idx = r * cols + c
        active = 'active' if grid_data.flatten()[idx] == 1 else ''
        # data-row/data-col for keyboard/pan logik, tabindex for fokus
        cells_html += f'<div class="cell {active}" data-index="{idx}" data-row="{r}" data-col="{c}" tabindex="0" aria-label="Række {r+1} Kolonne {c+1}" onclick="mark(this)"></div>'

grid_html = f"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root {{
  --cell-size: {cell_size}px;
  --cols: {cols};
  --rows: {rows};
  --gap: 1px;
  --scale: 1;
  --tx: 0px;
  --ty: 0px;
}}
html,body{{height:100%;margin:0;}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f6f7fb;
    padding: 12px;
}}

.toolbar {{
    display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px;background:white;padding:10px;border-radius:10px;box-shadow:0 3px 8px rgba(0,0,0,0.06);
}}

.viewport {{
    width:100%;
    height:calc(100vh - 220px);
    max-height:850px;
    border-radius:8px;
    background: #efefef;
    overflow: hidden; /* vi håndterer pan selv */
    position:relative;
    touch-action: none; /* så touch-drag virker pænt */
}}

/* wrapper vi transformerer (skalerer og translatere) */
.canvas-wrap {{
    transform-origin: 0 0;
    transform: translate(var(--tx), var(--ty)) scale(var(--scale));
    will-change: transform;
    transition: transform 120ms linear;
    padding: 12px;
}}

.grid-container {{
    display: grid;
    grid-template-columns: repeat(var(--cols), var(--cell-size));
    gap: var(--gap);
    background-color: #cfcfcf;
    border: 2px solid #444;
    width: fit-content;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

.cell {{
    width: var(--cell-size);
    height: var(--cell-size);
    background: white;
    display:flex;align-items:center;justify-content:center;
    font-weight:600;
    font-size: calc(var(--cell-size) * 0.6);
    cursor: pointer;
    user-select:none;
    outline: none;
}}

.cell:hover {{
    box-shadow: inset 0 0 0 2px rgba(0,0,0,0.04);
}}

.cell.active {{
    background: black;color:white;
}}

/* fokusstil for keyboard navigation */
.cell:focus {{
    box-shadow: 0 0 0 3px rgba(0,122,255,0.18);
    z-index:10; /* så den ligger ovenpå ved zoom */
}}

.btn {{padding:8px 12px;border-radius:8px;border:none;font-weight:600;cursor:pointer}}
.btn-save {{background:#007aff;color:#fff}}
.btn-print {{background:#5856d6;color:#fff}}
.btn-clear {{background:#ff3b30;color:#fff}}

.zoom-controls {{display:flex;gap:8px;align-items:center}}
input[type=range] {{width:220px}}

@media print {{
  .toolbar {{display:none}}
  body {{background: white !important}}
  .cell.active {{background: black !important}}
}}
</style>
</head>
<body>

<div class="toolbar">
  <select id="mode" style="padding:8px;border-radius:8px;font-weight:600">
    <option value="fill">⚫ Fyld felt</option>
    <option value="X">❌ Tegn X</option>
    <option value="O">⭕ Tegn O</option>
    <option value="erase">⚪ Viskelæder</option>
  </select>
  <div class="zoom-controls">
    <button class="btn" onclick="setZoom(scaleFactor - 0.1)">-</button>
    <input type="range" id="zoomRange" min="0.2" max="3.5" step="0.05" value="1">
    <button class="btn" onclick="setZoom(scaleFactor + 0.1)">+</button>
    <button class="btn" onclick="fitToScreen()">Fit</button>
    <button class="btn btn-save" onclick="download()">💾 Gem til Fotos</button>
    <button class="btn btn-print" onclick="window.print()">🖨️ PDF / Print</button>
    <button class="btn btn-clear" onclick="clearAll()">🗑️ Ryd</button>
  </div>
</div>

<div class="viewport" id="viewport">
  <div class="canvas-wrap" id="canvasWrap">
    <div class="grid-container" id="mainGrid">
      {cells_html}
    </div>
  </div>
</div>

<script>
const cols = {cols};
const rows = {rows};
const cellSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--cell-size'));
let scaleFactor = 1;
let tx = 0, ty = 0;
let isPanning = false, lastX = 0, lastY = 0;
const viewport = document.getElementById('viewport');
const canvasWrap = document.getElementById('canvasWrap');
const zoomRange = document.getElementById('zoomRange');

// Update CSS variables used for transform
function applyTransform() {
  canvasWrap.style.transform = `translate(${tx}px, ${ty}px) scale(${scaleFactor})`;
  // keep range synced
  zoomRange.value = scaleFactor;
}

function setZoom(val) {
  // clamp
  scaleFactor = Math.max(0.2, Math.min(3.5, Number(val)));
  applyTransform();
}

zoomRange.addEventListener('input', (e) => setZoom(e.target.value));

// Fit-to-screen: beregn scale så hele grid passer viewport
function fitToScreen() {
  const gridWidth = cols * cellSize + (cols - 1) * 1 + 24; // inkl padding
  const gridHeight = rows * cellSize + (rows - 1) * 1 + 24;
  const vw = viewport.clientWidth;
  const vh = viewport.clientHeight;
  const s = Math.min(vw / gridWidth, vh / gridHeight, 1.0);
  scaleFactor = Math.max(0.2, s);
  // center
  tx = (vw - gridWidth * scaleFactor) / 2;
  ty = (vh - gridHeight * scaleFactor) / 2;
  applyTransform();
}

// Initial fit
window.addEventListener('load', () => fitToScreen());
window.addEventListener('resize', () => {/* keep scale, but could refit: fitToScreen(); */});

// Pan handling (pointer events for good touch/mouse support)
viewport.addEventListener('pointerdown', (ev) => {
  if (ev.target.closest('.toolbar')) return; // don't pan from toolbar
  isPanning = true; viewport.setPointerCapture(ev.pointerId);
  lastX = ev.clientX; lastY = ev.clientY;
});

viewport.addEventListener('pointermove', (ev) => {
  if (!isPanning) return;
  const dx = ev.clientX - lastX;
  const dy = ev.clientY - lastY;
  lastX = ev.clientX; lastY = ev.clientY;
  tx += dx; ty += dy;
  applyTransform();
});
viewport.addEventListener('pointerup', (ev) => { isPanning = false; try{ viewport.releasePointerCapture(ev.pointerId);}catch(e){} });
viewport.addEventListener('pointercancel', () => { isPanning = false; });

// Wheel to zoom (ctrl + wheel) or pan
viewport.addEventListener('wheel', (ev) => {
  if (ev.ctrlKey) {
    ev.preventDefault();
    const delta = -ev.deltaY * 0.0015;
    setZoom(scaleFactor * (1 + delta));
  } else {
    // normal wheel -> vertical pan
    ty -= ev.deltaY;
    applyTransform();
  }
}, {passive: false});

// Mark/cell interaction
function mark(el) {
  const mode = document.getElementById('mode').value;
  if (mode === 'fill') {
    el.innerHTML = '';
    el.classList.toggle('active');
  } else if (mode === 'erase') {
    el.innerHTML = '';
    el.classList.remove('active');
  } else {
    el.classList.remove('active');
    if (el.innerHTML === mode) {
      el.innerHTML = '';
    } else {
      el.innerHTML = mode;
    }
  }
}

// keyboard navigation: arrow keys move focus
const cells = Array.from(document.querySelectorAll('.cell'));
cells.forEach((cell, idx) => {
  cell.addEventListener('keydown', (ev) => {
    let r = parseInt(cell.dataset.row,10);
    let c = parseInt(cell.dataset.col,10);
    if (ev.key === 'ArrowRight') { c = Math.min(cols-1, c+1); cells[r*cols + c].focus(); ev.preventDefault(); }
    else if (ev.key === 'ArrowLeft') { c = Math.max(0, c-1); cells[r*cols + c].focus(); ev.preventDefault(); }
    else if (ev.key === 'ArrowDown') { r = Math.min(rows-1, r+1); cells[r*cols + c].focus(); ev.preventDefault(); }
    else if (ev.key === 'ArrowUp') { r = Math.max(0, r-1); cells[r*cols + c].focus(); ev.preventDefault(); }
    else if (ev.key === ' ' || ev.key === 'Enter') { mark(cell); ev.preventDefault(); }
  });
});

// Clear all
function clearAll(){
  if(!confirm('Vil du slette hele dit mønster?')) return;
  cells.forEach(c=>{c.innerHTML=''; c.classList.remove('active');});
}

// Download — html2canvas. We temporarily reset transforms for a clean capture and restore after.
function download(){
  const area = document.getElementById('mainGrid');
  // gem gamle transform state
  const oldTransform = canvasWrap.style.transform;
  const oldTransition = canvasWrap.style.transition;
  // reset transforms so html2canvas får den rigtige størrelse
  canvasWrap.style.transition = 'none';
  canvasWrap.style.transform = 'translate(0px, 0px) scale(1)';
  html2canvas(area, {scale:2, backgroundColor:'#ffffff', logging:false}).then(canvas => {
    const link = document.createElement('a');
    link.download = 'mit-design-grid.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
    // restore
    canvasWrap.style.transform = oldTransform;
    canvasWrap.style.transition = oldTransition;
  }).catch(e=>{ alert('Fejl ved generering: '+e); canvasWrap.style.transform = oldTransform; canvasWrap.style.transition = oldTransition; });
}

// Hjælpefunktion: dobbeltklik på viewport nulstiller zoom og centrerer
viewport.addEventListener('dblclick', () => { scaleFactor = 1; tx = 0; ty = 0; applyTransform(); });

</script>

<!-- Load html2canvas (ude fra CDN) -->
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
</body>
</html>
"""

# Indsæt komponenten
components.html(grid_html, height=component_height, scrolling=True)

st.caption("Design Grid Pro v2.1 - Forbedret zoom/pan, keyboard navigation og fit-to-screen. Udviklet til hækling, strik og broderi.")
