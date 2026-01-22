import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import base64
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
        # Behandl billede med PIL
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        # Find alle mørke pixels og lav en liste over deres index
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()
        st.success(f"Billede klar! {len(import_data)} felter fundet.")

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
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.grid-wrap {
    flex: 1; overflow: auto;
    padding: 40px; display: flex;
    justify-content: center; align-items: flex-start;
    -webkit-overflow-scrolling: touch;
}

.grid {
    display: grid;
    gap: 1px; 
    background-color: #999 !important;
    border: 1px solid #666;
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
    font-size: 14px; font-weight: 600;
}

.primary { background: #007aff !important; color: white !important; border: none; }
.btn-active { background: #5856d6 !important; color: white !important; }

#loading {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: white; display: flex; justify-content: center;
    align-items: center; z-index: 2000; font-weight: bold;
}

@media print {
    .toolbar { display: none !important; }
    .grid-wrap { overflow: visible; padding: 0; }
    .cell { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
</head>
<body>

<div id="loading">Bygger mønster...</div>

<div class="toolbar">
    <select id="mode">
        <option value="fill">⚫ Fyld</option>
        <option value="X">❌ X</option>
        <option value="O">⭕ O</option>
        <option value="erase">⚪ Slet</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="primary" onclick="exportPNG()">💾 Gem PNG</button>
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
const IMPORT_DATA = __IMPORT_DATA__; // Liste over index-numre der skal være sorte

let isPanMode = false;
const grid = document.getElementById("grid");

grid.style.setProperty('--sz', SIZE + "px");
grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

function generateGrid() {
    const fragment = document.createDocumentFragment();
    const total = ROWS * COLS;
    const importSet = new Set(IMPORT_DATA);

    for (let i = 0; i < total; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.style.width = SIZE + "px";
        cell.style.height = SIZE + "px";
        cell.style.fontSize = (SIZE * 0.7) + "px";

        if (importSet.has(i)) {
            cell.classList.add("active");
        }

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

setTimeout(generateGrid, 50);

function togglePan() {
    isPanMode = !isPanMode;
    document.getElementById("panBtn").classList.toggle("btn-active");
    document.getElementById("view").style.touchAction = isPanMode ? "auto" : "none";
}

function clearGrid() {
    if (confirm("Ryd alt?")) {
        document.querySelectorAll(".cell").forEach(c => {
            c.textContent = "";
            c.classList.remove("active");
        });
    }
}

function exportPNG() {
    const btn = event.target;
    const oldText = btn.textContent;
    btn.textContent = "Vent...";
    html2canvas(grid, { backgroundColor: "#ffffff", scale: 1 }).then(canvas => {
        const link = document.createElement("a");
        link.download = "moenster.png";
        link.href = canvas.toDataURL();
        link.click();
        btn.textContent = oldText;
    });
}
</script>
</body>
</html>
"""

# Indsæt værdier i HTML
final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT_DATA__", json.dumps(import_data))
)

components.html(final_html, height=1000, scrolling=False)
