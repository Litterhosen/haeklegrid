import streamlit as st
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(
    page_title="Grid Designer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Indstillinger")

    # Opdateret til dine ønskede værdier (>100)
    cols = st.number_input("Kolonner", min_value=5, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=5, max_value=400, value=120)
    cell_size = st.slider("Zoom (feltstørrelse)", 5, 60, 20)

    st.divider()
    st.write("Klik udenfor panelet for at lukke")

# ---------- HTML ----------
html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

<style>
body {
    margin: 0;
    padding: 0;
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
    font-size: 14px;
    font-weight: 600;
}

button.primary { background: #007aff; color: white; border: none; }
button.active-tool { background: #5856d6; color: white; }

/* Container der tillader scroll i begge retninger */
.grid-wrap {
    flex: 1;
    overflow: auto;
    -webkit-overflow-scrolling: touch;
    padding: 20px;
    background: #e5e5e5;
}

.grid {
    display: grid;
    background: #bbb;
    gap: 1px;
    width: fit-content;
    margin: 0 auto;
    background-color: white;
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
    print-color-adjust: exact;
}

.cell.active {
    background: black !important;
    color: white !important;
}

/* Panorerings-tilstand */
.pan-mode .cell {
    cursor: grab;
    pointer-events: none; /* Deaktiverer klik-logik når vi panorerer */
}

.grid-wrap.pan-active {
    cursor: grab;
}

@media print {
    .toolbar { display: none !important; }
    .grid-wrap { overflow: visible; padding: 0; background: white; }
    body { background: white; }
    .cell { border: 0.1pt solid #eee; -webkit-print-color-adjust: exact; }
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
    <button class="primary" onclick="exportPNG()">💾 Gem PNG</button>
    <button onclick="window.print()">🖨️ PDF</button>
    <button onclick="clearGrid()">🗑️ Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = """ + str(cols) + """;
const ROWS = """ + str(rows) + """;
const SIZE = """ + str(cell_size) + """;

let isPanMode = false;
const grid = document.getElementById("grid");
const view = document.getElementById("view");

grid.style.gridTemplateColumns = "repeat(" + COLS + ", " + SIZE + "px)";

// Generer celler
for (let i = 0; i < ROWS * COLS; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.style.width = SIZE + "px";
    cell.style.height = SIZE + "px";
    cell.style.fontSize = (SIZE * 0.6) + "px";

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

    grid.appendChild(cell);
}

function togglePan() {
    isPanMode = !isPanMode;
    document.getElementById("panBtn").classList.toggle("active-tool");
    grid.classList.toggle("pan-mode");
    view.classList.toggle("pan-active");
    // Ved pan-mode tillader vi naturlig touch-scroll på mobilen
    view.style.touchAction = isPanMode ? "auto" : "none";
}

function clearGrid() {
    if (!confirm("Vil du slette alt?")) return;
    document.querySelectorAll(".cell").forEach(c => {
        c.textContent = "";
        c.classList.remove("active");
    });
}

function exportPNG() {
    const btn = event.target;
    btn.textContent = "Vent...";
    html2canvas(grid, {
        backgroundColor: "#ffffff",
        scale: 2
    }).then(canvas => {
        const link = document.createElement("a");
        link.download = "design-grid.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
        btn.textContent = "💾 Gem PNG";
    });
}
</script>

</body>
</html>
"""

components.html(html, height=1000, scrolling=False)

st.caption("Grid Designer Pro – Optimeret til mobil navigation og eksport")
