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

# Skjul Streamlit UI
st.markdown("""
<style>
header, footer, .stDeployButton {display:none !important;}
[data-testid="stHeader"] {display:none !important;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Indstillinger")

    cols = st.number_input("Kolonner", min_value=120, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=120, max_value=400, value=120)
    cell_size = st.slider("Zoom (feltstørrelse)", 8, 40, 20)

    st.divider()
    uploaded_file = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])

    import_data = []
    if uploaded_file:
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

# ---------------- HTML ----------------
html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">

<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #e0e0e0;
    height: 100vh;
    overflow: hidden;
}

.toolbar {
    background: #fff;
    padding: 10px;
    display: flex;
    gap: 8px;
    justify-content: center;
    border-bottom: 2px solid #bbb;
    flex-wrap: wrap;
}

button, select {
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-weight: bold;
}

.primary {
    background: #007aff;
    color: white;
    border: none;
}

.viewport {
    flex: 1;
    overflow: hidden;
    position: relative;
}

.canvas-wrap {
    position: absolute;
    left: 0;
    top: 0;
    transform-origin: 0 0;
}

canvas {
    background: #fff;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
    touch-action: none;
}
</style>
</head>

<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">Sort</option>
        <option value="X">X</option>
        <option value="O">O</option>
        <option value="erase">Ryd</option>
    </select>
    <button class="primary" onclick="exportPNG()">Gem billede</button>
    <button onclick="clearGrid()">Ryd alt</button>
</div>

<div class="viewport" id="viewport">
    <div class="canvas-wrap" id="wrap">
        <canvas id="canvas"></canvas>
    </div>
</div>

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT = __IMPORT__;

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = COLS * SIZE;
canvas.height = ROWS * SIZE;

let grid = Array.from({length: ROWS}, () => Array(COLS).fill(null));

IMPORT.forEach(i => {
    const r = Math.floor(i / COLS);
    const c = i % COLS;
    grid[r][c] = "fill";
});

// -------- PAN & ZOOM --------
let scale = 1;
let tx = 0, ty = 0;
let dragging = false;
let lastX = 0, lastY = 0;

const wrap = document.getElementById("wrap");

function updateTransform() {
    wrap.style.transform =
        "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
}

document.getElementById("viewport").addEventListener("wheel", e => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 1.1 : 0.9;
    scale = Math.min(5, Math.max(0.3, scale * delta));
    updateTransform();
}, { passive: false });

wrap.addEventListener("mousedown", e => {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
});

window.addEventListener("mousemove", e => {
    if (!dragging) return;
    tx += e.clientX - lastX;
    ty += e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
    updateTransform();
});

window.addEventListener("mouseup", () => dragging = false);

// -------- DRAW --------
function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    for (let r=0;r<ROWS;r++) {
        for (let c=0;c<COLS;c++) {
            const x = c*SIZE;
            const y = r*SIZE;

            ctx.strokeStyle = "#ccc";
            ctx.strokeRect(x,y,SIZE,SIZE);

            if (grid[r][c] === "fill") {
                ctx.fillStyle = "#000";
                ctx.fillRect(x,y,SIZE,SIZE);
            }
            if (grid[r][c] === "X" || grid[r][c] === "O") {
                ctx.fillStyle = "#000";
                ctx.font = "bold " + (SIZE*0.7) + "px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(grid[r][c], x+SIZE/2, y+SIZE/2);
            }
        }
    }
}

canvas.addEventListener("click", e => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / scale;
    const y = (e.clientY - rect.top) / scale;

    const c = Math.floor(x / SIZE);
    const r = Math.floor(y / SIZE);

    const mode = document.getElementById("mode").value;
    if (mode === "erase") grid[r][c] = null;
    else if (mode === "fill") grid[r][c] = grid[r][c] ? null : "fill";
    else grid[r][c] = grid[r][c] === mode ? null : mode;

    draw();
});

// -------- EXPORT (PIXEL SAFE + MARGIN) --------
function exportPNG() {
    const MARGIN = 100;
    const SCALE = 3;

    const out = document.createElement("canvas");
    out.width = (canvas.width + MARGIN*2) * SCALE;
    out.height = (canvas.height + MARGIN*2) * SCALE;

    const octx = out.getContext("2d");
    octx.imageSmoothingEnabled = false;

    octx.fillStyle = "#ffffff";
    octx.fillRect(0,0,out.width,out.height);

    octx.scale(SCALE, SCALE);
    octx.drawImage(canvas, MARGIN, MARGIN);

    const link = document.createElement("a");
    link.download = "moenster.png";
    link.href = out.toDataURL("image/png");
    link.click();
}

function clearGrid() {
    if (!confirm("Ryd alt?")) return;
    grid = Array.from({length: ROWS}, () => Array(COLS).fill(null));
    draw();
}

draw();
updateTransform();
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

components.html(final_html, height=900, scrolling=False)
