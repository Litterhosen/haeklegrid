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

    cols = st.number_input("Kolonner", min_value=120, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=120, max_value=400, value=120)
    cell_size = st.slider("Zoom (feltstørrelse)", 10, 60, 20)

    st.divider()
    st.write("Klik udenfor panelet for at lukke")

# ---------- GRID DATA ----------
grid_data = np.zeros((rows, cols), dtype=int)

# ---------- HTML ----------
html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

<style>
body {
    margin: 0;
    padding: 10px;
    background: #f2f2f2;
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.toolbar {
    position: sticky;
    top: 0;
    background: white;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 8px;
    display: flex;
    gap: 8px;
    z-index: 1000;
}

button, select {
    padding: 8px 12px;
    border-radius: 6px;
    border: none;
    background: #ddd;
    cursor: pointer;
    font-size: 14px;
}

button.primary {
    background: #007aff;
    color: white;
}

.grid-wrap {
    overflow: auto;
    max-width: 100vw;
    max-height: 80vh;
}

.grid {
    display: grid;
    background: #bbb;
    gap: 1px;
}

.cell {
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    user-select: none;
    cursor: pointer;
}

.cell.active {
    background: black;
    color: white;
}
</style>
</head>

<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">Fill</option>
        <option value="X">X</option>
        <option value="O">O</option>
        <option value="erase">Erase</option>
    </select>

    <button class="primary" onclick="exportPNG()">Export PNG</button>
    <button onclick="clearGrid()">Clear</button>
</div>

<div class="grid-wrap">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = """ + str(cols) + """;
const ROWS = """ + str(rows) + """;
const SIZE = """ + str(cell_size) + """;

const grid = document.getElementById("grid");
grid.style.gridTemplateColumns = "repeat(" + COLS + ", " + SIZE + "px)";

for (let i = 0; i < ROWS * COLS; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.style.width = SIZE + "px";
    cell.style.height = SIZE + "px";

    cell.onclick = function () {
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

function clearGrid() {
    if (!confirm("Clear everything?")) return;
    document.querySelectorAll(".cell").forEach(c => {
        c.textContent = "";
        c.classList.remove("active");
    });
}

function exportPNG() {
    html2canvas(grid, {
        backgroundColor: "#ffffff",
        scale: 2
    }).then(canvas => {
        const link = document.createElement("a");
        link.download = "grid.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    });
}
</script>

</body>
</html>
"""

components.html(html, height=900, scrolling=True)

st.caption("Grid Designer – safe template")
