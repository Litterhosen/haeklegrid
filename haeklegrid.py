import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(
    page_title="Grid Designer Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 120)
    rows = st.number_input("Rækker", 5, 400, 120)
    cell_size = st.slider("Zoom (feltstørrelse)", 5, 60, 20)

    st.divider()
    st.header("📥 Import")
    uploaded_file = st.file_uploader("Konverter billede til net", type=["png", "jpg", "jpeg"])
    
    import_data = []
    if uploaded_file:
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        # Find index for mørke pixels (< 128)
        import_data = np.where(arr.flatten() < 128)[0].tolist()
        st.success(f"Billede klar til indlæsning!")

# ---------- HTML & JAVASCRIPT ----------
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

<style>
body {
    margin: 0; padding: 0;
    background: #e5e5e5;
    font-family: -apple-system, sans-serif;
    display: flex; flex-direction: column;
    height: 100vh; overflow: hidden;
}

.toolbar {
    position: sticky; top: 0;
    background: white; padding: 10px;
    border-bottom: 1px solid #ccc;
    display: flex; flex-wrap: wrap; gap: 8px;
    z-index: 1001; justify-content: center;
}

.grid-wrap {
    flex: 1; overflow: auto;
    padding: 30px; display: flex;
    justify-content: center; align-items: flex-start;
    -webkit-overflow-scrolling: touch;
}

/* GITTER SETUP */
.grid {
    display: grid;
    gap: 1px; 
    background-color: #999 !important; /* Gitter linje farve */
    border: 1px solid #333;
    width: fit-content;
    background-color: white;
}

.cell {
    background-color: white;
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; user-select: none; cursor: pointer;
    min-width: var(--sz); min-height: var(--sz);
}

.cell.active { background-color: black !important; color: white !important; }

button, select {
    padding: 10px 14px; border-radius: 8px;
    border: 1px solid #ccc; background: white;
    font-size: 13px; font-weight: 600; cursor: pointer;
}

.btn-png { background: #007aff; color: white; border: none; }
.btn-svg { background: #34c759; color: white; border: none; }
.btn-active { background: #5856d6 !important; color: white !important; }

#loading {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: white; display: flex; flex-direction: column;
    justify-content: center; align-items: center; z-index: 2000;
}

@media print {
    .toolbar { display: none !important; }
    .grid-wrap { overflow: visible; padding: 0; }
    .grid { gap: 0; border: 1px solid black; }
    .cell { 
        border: 0.1pt solid black !important;
        -webkit-print-color-adjust: exact; 
        print-color-adjust: exact; 
    }
}
</style>
</head>
<body>

<div id="loading">
    <div>Bygger gitter...</div>
    <div style="font-size: 12px; color: #666; margin-top: 10px;">Dette kan tage et øjeblik ved store mønstre</div>
</div>

<div class="toolbar">
    <select id="mode">
        <option value="fill">⚫ Sort</option>
        <option value="X">❌ X</option>
        <option value="O">⭕ O</option>
        <option value="erase">⚪ Slet</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="btn-png" onclick="exportPNG()">📸 Gem PNG</button>
    <button class="btn-svg" onclick="exportSVG()">📐 SVG</button>
    <button onclick="window.print()">🖨️ PDF</button>
    <button onclick="clearGrid()">🗑️ Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT_DATA = __IMPORT_DATA__;

let isPanMode = false;
const grid = document.getElementById("grid");

grid.style.setProperty('--sz', SIZE + "px");
grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

// Effektiv generering af celler
function generateGrid() {
    const fragment = document.createDocumentFragment();
    const importSet = new Set(IMPORT_DATA);
    const total = ROWS * COLS;

    for (let i = 0; i < total; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.style.width = SIZE + "px";
        cell.style.height = SIZE + "px";
        cell.style.fontSize = (SIZE * 0.7) + "px";

        if (importSet.has(i)) cell.classList.add("active");

        cell.onclick = function () {
            if (isPanMode) return;
            const mode = document.getElementById("mode").value;
            if (mode === "fill") {
                cell.textContent = "";
                cell.classList.toggle("active");
            } else if (mode === "erase") {
                cell.textContent = "";
                cell.classList.remove("active");
            } else {
                cell.classList.remove("active");
                cell.textContent = cell.textContent === mode ? "" : mode;
            }
        };
        fragment.appendChild(cell);
    }
    grid.appendChild(fragment);
    document.getElementById("loading").style.display = "none";
}

// Start process
setTimeout(generateGrid, 50);

function togglePan() {
    isPanMode = !isPanMode;
    document.getElementById("panBtn").classList.toggle("btn-active");
    // Ved panorerings-tilstand tillader vi touch-navigation
    document.getElementById("view").style.touchAction = isPanMode ? "auto" : "none";
}

function clearGrid() {
    if (confirm("Vil du rydde hele pladen?")) {
        document.querySelectorAll(".cell").forEach(c => {
            c.textContent = "";
            c.classList.remove("active");
        });
    }
}

function exportPNG() {
    html2canvas(grid, { backgroundColor: "#ffffff", scale: 2 }).then(canvas => {
        const link = document.createElement("a");
        link.download = "moenster-grid.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    });
}

function exportSVG() {
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${COLS * SIZE}" height="${ROWS * SIZE}">`;
    svg += `<rect width="100%" height="100%" fill="white"/>`;
    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, i) => {
        if (cell.classList.contains('active') || cell.textContent) {
            const x = (i % COLS) * SIZE;
            const y = Math.floor(i / COLS) * SIZE;
            if (cell.classList.contains('active')) {
                svg += `<rect x="${x}" y="${y}" width="${SIZE}" height="${SIZE}" fill="black"/>`;
            } else {
                svg += `<text x="${x + SIZE/2}" y="${y + SIZE/2 + SIZE*0.25}" font-family="Arial" font-size="${SIZE*0.7}" text-anchor="middle">${cell.textContent}</text>`;
            }
        }
    });
    // Gitterlinjer i SVG
    for(let i=0; i<=COLS; i++) svg += `<line x1="${i*SIZE}" y1="0" x2="${i*SIZE}" y2="${ROWS*SIZE}" stroke="#ccc" stroke-width="0.5"/>`;
    for(let i=0; i<=ROWS; i++) svg += `<line x1="0" y1="${i*SIZE}" x2="${COLS*SIZE}" y2="${i*SIZE}" stroke="#ccc" stroke-width="0.5"/>`;
    
    svg += "</svg>";
    const blob = new Blob([svg], {type: 'image/svg+xml'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "moenster.svg";
    link.click();
}
</script>
</body>
</html>
"""

# Indsæt alle data sikkert
final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT_DATA__", json.dumps(import_data))
)

components.html(final_html, height=1000, scrolling=False)
