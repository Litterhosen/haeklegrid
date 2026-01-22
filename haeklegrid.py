import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

# Sætter siden op til at bruge hele bredden og fjerne alt standard UI
st.set_page_config(page_title="Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Fjerner Streamlits topbar, menu og padding helt */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {display:none !important;}
    .main .block-container {padding: 0 !important; max-width: 100% !important;}
    iframe {display: block;}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 120)
    rows = st.number_input("Rækker", 5, 400, 120)
    cell_size = st.slider("Zoom / Feltstørrelse", 5, 60, 25)
    st.divider()
    uploaded = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])
    
    import_data = []
    if uploaded:
        img = Image.open(uploaded).convert("L").resize((cols, rows), Image.NEAREST)
        import_data = np.where(np.array(img).flatten() < 128)[0].tolist()

html_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; font-family: sans-serif; background: #222; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
    
    /* FASTLÅST MENU I TOPPEN */
    .header-menu { 
        background: #1a1a1a; color: white; padding: 12px; 
        display: flex; gap: 12px; justify-content: center; align-items: center;
        z-index: 10000; border-bottom: 2px solid #000; flex-wrap: wrap;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    .canvas-container { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 40px; -webkit-overflow-scrolling: touch; }
    
    canvas { background: #fff; cursor: crosshair; box-shadow: 0 0 25px rgba(0,0,0,0.5); display: block; }
    
    button, select { padding: 12px 16px; border-radius: 8px; border: 1px solid #444; font-weight: bold; cursor: pointer; font-size: 14px; }
    .btn-blue { background: #007aff; color: white; border: none; }
    .btn-green { background: #34c759; color: white; border: none; }
    .btn-pan.active { background: #ff9500 !important; color: white !important; }
    
    select { background: #fff; color: #000; }
</style>
</head>
<body>

<div class="header-menu">
    <select id="tool">
        <option value="fill">⚫ SORT FELT</option>
        <option value="X">❌ SYMBOL X</option>
        <option value="O">⭕ SYMBOL O</option>
        <option value="erase">⚪ RYDDER</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ PANORER</button>
    <button class="btn-blue" onclick="exportData('png')">📸 GEM BILLEDE</button>
    <button class="btn-green" onclick="exportData('pdf')">🖨️ PDF PRINT</button>
    <button style="background: #ff3b30; color: white; border:none;" onclick="resetGrid()">🗑️ RYD ALT</button>
</div>

<div class="canvas-container" id="container">
    <canvas id="gridCanvas"></canvas>
</div>

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT = __IMPORT__;
const MARGIN = 100;

const canvas = document.getElementById("gridCanvas");
const ctx = canvas.getContext("2d");
const container = document.getElementById("container");

let isPan = false;
let gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));

// Setup lærredets størrelse
canvas.width = COLS * SIZE;
canvas.height = ROWS * SIZE;

// Indlæs import
if (IMPORT.length > 0) {
    IMPORT.forEach(idx => {
        const r = Math.floor(idx / COLS);
        const c = idx % COLS;
        gridData[r][c] = 'fill';
    });
}

function drawGrid() {
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = "#ddd"; // Gitter-farve
    ctx.lineWidth = 1;

    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const x = c * SIZE;
            const y = r * SIZE;
            
            // Tegn gitter (grids)
            ctx.strokeRect(x, y, SIZE, SIZE);
            
            const cell = gridData[r][c];
            if (cell === 'fill') {
                ctx.fillStyle = "black";
                ctx.fillRect(x, y, SIZE, SIZE);
            } else if (cell === 'X' || cell === 'O') {
                ctx.fillStyle = "black";
                ctx.font = `bold ${SIZE * 0.7}px Arial`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(cell, x + SIZE/2, y + SIZE/2);
            }
        }
    }
}

// Tegne-funktion
canvas.addEventListener('mousedown', handleClick);
canvas.addEventListener('touchstart', (e) => {
    if(!isPan) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent("mousedown", {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvas.dispatchEvent(mouseEvent);
    }
}, {passive: false});

function handleClick(e) {
    if (isPan) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const c = Math.floor(x / SIZE);
    const r = Math.floor(y / SIZE);
    
    if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
        const tool = document.getElementById("tool").value;
        if (tool === "erase") gridData[r][c] = null;
        else if (tool === "fill") gridData[r][c] = gridData[r][c] === 'fill' ? null : 'fill';
        else gridData[r][c] = gridData[r][c] === tool ? null : tool;
        drawGrid();
    }
}

function togglePan() {
    isPan = !isPan;
    document.getElementById("panBtn").classList.toggle("active");
    container.style.touchAction = isPan ? "auto" : "none";
    canvas.style.cursor = isPan ? "grab" : "crosshair";
}

function resetGrid() {
    if(confirm("Vil du slette alt mønster?")) {
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        drawGrid();
    }
}

function exportData(type) {
    // Lav et high-res canvas til eksport med margen
    const expCanvas = document.createElement("canvas");
    const expCtx = expCanvas.getContext("2d");
    const scale = 2;
    const s = SIZE * scale;
    const m = MARGIN * scale;

    expCanvas.width = (COLS * s) + (m * 2);
    expCanvas.height = (ROWS * s) + (m * 2);
    
    expCtx.fillStyle = "white";
    expCtx.fillRect(0, 0, expCanvas.width, expCanvas.height);
    
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const x = c * s + m;
            const y = r * s + m;
            
            expCtx.strokeStyle = "#bbb";
            expCtx.lineWidth = 1;
            expCtx.strokeRect(x, y, s, s);
            
            const cell = gridData[r][c];
            if (cell === 'fill') {
                expCtx.fillStyle = "black";
                expCtx.fillRect(x, y, s, s);
            } else if (cell === 'X' || cell === 'O') {
                expCtx.fillStyle = "black";
                expCtx.font = `bold ${s * 0.7}px Arial`;
                expCtx.textAlign = "center";
                expCtx.textBaseline = "middle";
                expCtx.fillText(cell, x + s/2, y + s/2);
            }
        }
    }

    const dataUrl = expCanvas.toDataURL("image/png");
    if (type === 'png') {
        const a = document.createElement("a");
        a.download = "moenster.png";
        a.href = dataUrl;
        a.click();
    } else {
        const win = window.open('', '_blank');
        win.document.write(`<html><body style="margin:0; display:flex; justify-content:center; background:#fff;">
            <img src="${dataUrl}" style="max-width:100%; height:auto;" onload="window.print();window.close();">
            </body></html>`);
    }
}

drawGrid();
</script>
</body>
</html>
"""

final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT__", json.dumps(import_data))
)

components.html(final_html, height=1200, scrolling=False)
