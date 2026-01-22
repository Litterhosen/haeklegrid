import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(
    page_title="Grid Designer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Skjul Streamlit UI
st.markdown("<style>header, footer, .stDeployButton {display:none !important;} [data-testid='stHeader'] {display:none !important;}</style>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Indstillinger")
    cols = st.number_input("Kolonner", min_value=5, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=5, max_value=400, value=120)
    cell_size = st.slider("Zoom (feltstørrelse)", 5, 60, 20)

    st.divider()
    uploaded = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])

    import_data = []
    if uploaded:
        img = Image.open(uploaded).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

# ---------- HTML & JAVASCRIPT ----------
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
body { margin: 0; background: #f2f2f2; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; }
.toolbar { position: sticky; top: 0; background: white; padding: 10px; border-bottom: 1px solid #ddd; display: flex; flex-wrap: wrap; gap: 8px; z-index: 1000; justify-content: center; }
button, select { padding: 10px 14px; border-radius: 8px; border: 1px solid #ccc; background: white; cursor: pointer; font-weight: 600; }
button.primary { background: #007aff; color: white; border: none; }
button.active-tool { background: #5856d6 !important; color: white !important; }
.grid-wrap { flex: 1; overflow: auto; padding: 40px; background: #e5e5e5; display: flex; justify-content: center; }
.grid { display: grid; gap: 1px; background: #bbb; border: 1px solid #999; width: fit-content; }
.cell { background: white; width: var(--sz); height: var(--sz); display: flex; align-items: center; justify-content: center; font-weight: bold; user-select: none; }
.cell.active { background: black !important; }
.pan-active .cell { pointer-events: none; }
.pan-active { cursor: grab; }

/* Print regler er nu simplificeret til kun at vise det genererede billede */
@media print {
    body * { visibility: hidden; }
    #print-image, #print-image * { visibility: visible; }
    #print-image { position: absolute; left: 0; top: 0; width: 100%; }
}
</style>
</head>
<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">Sort Felt</option>
        <option value="X">Symbol X</option>
        <option value="O">Symbol O</option>
        <option value="erase">Slet</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="primary" onclick="generateAndExport('png')">📸 Gem Billede</button>
    <button class="primary" style="background:#34c759" onclick="generateAndExport('pdf')">🖨️ PDF / Print</button>
    <button onclick="clearGrid()">🗑️ Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<img id="print-image" style="display:none;">

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT = __IMPORT__;

let isPan = false;
const grid = document.getElementById("grid");
const view = document.getElementById("view");

grid.style.setProperty('--sz', SIZE + "px");
grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

const fragment = document.createDocumentFragment();
for (let i = 0; i < ROWS * COLS; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.style.fontSize = (SIZE * 0.7) + "px";
    cell.onclick = function() {
        if (isPan) return;
        const mode = document.getElementById("mode").value;
        if (mode === "fill") {
            cell.textContent = "";
            cell.classList.toggle("active");
        } else if (mode === "erase") {
            cell.textContent = "";
            cell.classList.remove("active");
        } else {
            cell.classList.remove("active");
            cell.textContent = (cell.textContent === mode) ? "" : mode;
        }
    };
    fragment.appendChild(cell);
}
grid.appendChild(fragment);

IMPORT.forEach(idx => {
    if(grid.children[idx]) grid.children[idx].classList.add("active");
});

function togglePan() {
    isPan = !isPan;
    document.getElementById("panBtn").classList.toggle("active-tool");
    view.classList.toggle("pan-active");
    view.style.touchAction = isPan ? "auto" : "none";
}

function clearGrid() {
    if (confirm("Vil du slette alt?")) {
        document.querySelectorAll(".cell").forEach(c => {
            c.textContent = "";
            c.classList.remove("active");
        });
    }
}

// NY FUNKTION: Genererer et billede der bruges til BÅDE download og PDF
function generateAndExport(type) {
    const btn = event.target;
    const oldLabel = btn.textContent;
    btn.textContent = "Vent...";
    
    const MARGIN = 120; 
    const SCALE = 2; 
    const drawSize = SIZE * SCALE;
    
    const out = document.createElement("canvas");
    out.width = (COLS * drawSize) + (MARGIN * 2);
    out.height = (ROWS * drawSize) + (MARGIN * 2);
    const ctx = out.getContext("2d");
    
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, out.width, out.height);
    
    const cells = grid.children;
    for (let i = 0; i < cells.length; i++) {
        const r = Math.floor(i / COLS);
        const c = i % COLS;
        const x = MARGIN + (c * drawSize);
        const y = MARGIN + (r * drawSize);
        
        if (cells[i].classList.contains("active")) {
            ctx.fillStyle = "#000000";
            ctx.fillRect(x, y, drawSize, drawSize);
        } else {
            ctx.strokeStyle = "#dddddd";
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, drawSize, drawSize);
            
            const txt = cells[i].textContent;
            if (txt) {
                ctx.fillStyle = "#000000";
                ctx.font = `bold ${drawSize * 0.7}px Arial`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(txt, x + drawSize/2, y + drawSize/2);
            }
        }
    }
    
    const imgData = out.toDataURL("image/png");

    if (type === 'png') {
        const link = document.createElement("a");
        link.download = "moenster.png";
        link.href = imgData;
        link.click();
        btn.textContent = oldLabel;
    } else {
        // PDF-løsning: Vis billedet i en ny fane og print dérfra
        const printWindow = window.open('', '_blank');
        printWindow.document.write('<html><head><title>Print Mønster</title></head><body style="margin:0; display:flex; justify-content:center;">');
        printWindow.document.write('<img src="' + imgData + '" style="max-width:100%; height:auto;">');
        printWindow.document.write('<script>setTimeout(function(){window.print();window.close();}, 500);<\\/script>');
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        btn.textContent = oldLabel;
    }
}
</script>
</body>
</html>
"""

final_html = (
    html_code.replace("__COLS__", str(cols))
        .replace("__ROWS__", str(rows))
        .replace("__SIZE__", str(cell_size))
        .replace("__IMPORT__", json.dumps(import_data))
)

components.html(final_html, height=1000, scrolling=False)
