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

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Indstillinger")

    cols = st.number_input("Kolonner", min_value=120, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=120, max_value=400, value=120)
    cell_size = st.slider("Zoom (feltstørrelse)", 5, 60, 20)

    st.divider()
    uploaded = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])

    import_data = []
    if uploaded:
        img = Image.open(uploaded).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

    st.write("Klik udenfor panelet for at lukke")

# ---------- HTML ----------
html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

<style>
body {
    margin: 0;
    background: #f2f2f2;
    font-family: -apple-system, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.toolbar {
    position: sticky;
    top: 0;
    background: white;
    padding: 10px;
    border-bottom: 1px solid #ddd;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    z-index: 1000;
    justify-content: center;
}

button, select {
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #ccc;
    background: white;
    cursor: pointer;
    font-weight: 600;
}

button.primary { background: #007aff; color: white; border: none; }
button.active-tool { background: #5856d6; color: white; }

.grid-wrap {
    flex: 1;
    overflow: auto;
    -webkit-overflow-scrolling: touch;
    padding: 20px;
    background: #e5e5e5;
}

.grid {
    display: grid;
    gap: 1px;
    width: fit-content;
    margin: 0 auto;
    background: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.cell {
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    user-select: none;
    -webkit-print-color-adjust: exact;
}

.cell.active {
    background: black;
    color: white;
}

/* Pan-mode */
.pan-mode .cell {
    pointer-events: none;
    cursor: grab;
}
.grid-wrap.pan-active { cursor: grab; }
</style>
</head>

<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">Fyld</option>
        <option value="X">X</option>
        <option value="O">O</option>
        <option value="erase">Slet</option>
    </select>

    <button id="panBtn" onclick="togglePan()">Panorer</button>
    <button class="primary" onclick="exportPNG()">Gem PNG</button>
    <button onclick="window.print()">PDF</button>
    <button onclick="clearGrid()">Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT = __IMPORT__;

let isPan = false;
const grid = document.getElementById("grid");
const view = document.getElementById("view");

grid.style.gridTemplateColumns = "repeat(" + COLS + ", " + SIZE + "px)";

// Byg grid
for (let i = 0; i < ROWS * COLS; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.style.width = SIZE + "px";
    cell.style.height = SIZE + "px";
    cell.style.fontSize = (SIZE * 0.6) + "px";

    cell.onclick = function () {
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
            cell.textContent = cell.textContent === mode ? "" : mode;
        }
    };

    grid.appendChild(cell);
}

// Import billede
IMPORT.forEach(idx => {
    const c = idx % COLS;
    const r = Math.floor(idx / COLS);
    const cell = grid.children[r * COLS + c];
    if (cell) cell.classList.add("active");
});

function togglePan() {
    isPan = !isPan;
    document.getElementById("panBtn").classList.toggle("active-tool");
    grid.classList.toggle("pan-mode");
    view.classList.toggle("pan-active");
    view.style.touchAction = isPan ? "auto" : "none";
}

function clearGrid() {
    if (!confirm("Vil du slette alt?")) return;
    document.querySelectorAll(".cell").forEach(c => {
        c.textContent = "";
        c.classList.remove("active");
    });
}

// Pixel-perfekt eksport med margin
function exportPNG() {
    const MARGIN = 80;
    const SCALE = 3;

    html2canvas(grid, {
        backgroundColor: "#ffffff",
        scale: SCALE
    }).then(canvas => {
        const out = document.createElement("canvas");
        out.width = canvas.width + MARGIN * 2 * SCALE;
        out.height = canvas.height + MARGIN * 2 * SCALE;

        const ctx = out.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0,0,out.width,out.height);
        ctx.drawImage(canvas, MARGIN * SCALE, MARGIN * SCALE);

        const link = document.createElement("a");
        link.download = "design-grid.png";
        link.href = out.toDataURL("image/png");
        link.click();
    });
}
</script>

</body>
</html>
"""

final_html = (
    html.replace("__COLS__", str(cols))
        .replace("__ROWS__", str(rows))
        .replace("__SIZE__", str(cell_size))
        .replace("__IMPORT__", json.dumps(import_data))
)

components.html(final_html, height=1000, scrolling=False)

st.caption("Grid Designer Pro – pan, import og pixel-sikker eksport")
