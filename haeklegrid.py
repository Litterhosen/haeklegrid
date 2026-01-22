import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(
    page_title="Ultimate Grid Designer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Skjul Streamlit standard elementer helt
st.markdown("""
    <style>
    header, footer, .stDeployButton {display:none !important;}
    [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    </style>
    """, unsafe_allow_html=True)

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
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
body {{
    margin: 0;
    background: #222;
    font-family: sans-serif;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}}

.toolbar {{
    position: sticky;
    top: 0;
    background: #fff;
    padding: 10px;
    border-bottom: 2px solid #000;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    z-index: 1000;
    justify-content: center;
}}

button, select {{
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #ccc;
    background: white;
    cursor: pointer;
    font-weight: 600;
}}
button.primary {{
    background: #007aff;
    color: white;
    border: none;
}}
button.active-tool {{
    background: #ff9500 !important;
    color: white !important;
}}

.grid-wrap {{
    flex: 1;
    overflow: auto;
    padding: 40px;
    background: #444;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    -webkit-overflow-scrolling: touch;
}}

canvas {{
    background: white;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    display: block;
    cursor: crosshair;
}}

.pan-active canvas {{
    cursor: grab;
}}
</style>
</head>
<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">⚫ Sort Felt</option>
        <option value="X">❌ Symbol X</option>
        <option value="O">⭕ Symbol O</option>
        <option value="erase">⚪ Ryd felt</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="primary" onclick="exportSmart('png')">📸 Gem PNG</button>
    <button class="primary" style="background:#34c759" onclick="exportSmart('pdf')">🖨️ PDF</button>
    <button onclick="clearGrid()">🗑️ Ryd alt</button>
</div>

<div class="grid-wrap" id="view">
    <canvas id="gridCanvas"></canvas>
</div>

<script>
const COLS = {cols};
const ROWS = {rows};
const SIZE = {cell_size};
const IMPORT = {json.dumps(import_data)};
const MARGIN = 100; // Margen til eksport

const canvas = document.getElementById("gridCanvas");
const ctx = canvas.getContext("2d");
const view = document.getElementById("view");

let isPan = false;
let gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));

// Initialiser størrelse
canvas.width = COLS * SIZE;
canvas.height = ROWS * SIZE;

// Indlæs import data
IMPORT.forEach(idx => {{
    const r = Math.floor(idx / COLS);
    const c = idx % COLS;
    gridData[r][c] = 'fill';
}});

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Tegn baggrund
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Tegn Grid linjer
    ctx.strokeStyle = "#ddd";
    ctx.lineWidth = 1;
    
    // Lodrette linjer
    for (let c = 0; c <= COLS; c++) {{
        ctx.beginPath();
        ctx.moveTo(c * SIZE, 0);
        ctx.lineTo(c * SIZE, canvas.height);
        ctx.stroke();
    }}
    
    // Vandre linjer
    for (let r = 0; r <= ROWS; r++) {{
        ctx.beginPath();
        ctx.moveTo(0, r * SIZE);
        ctx.lineTo(canvas.width, r * SIZE);
        ctx.stroke();
    }}
    
    // Tegn celler
    for (let r = 0; r < ROWS; r++) {{
        for (let c = 0; c < COLS; c++) {{
            const x = c * SIZE;
            const y = r * SIZE;
            
            const cell = gridData[r][c];
            if (cell === 'fill') {{
                ctx.fillStyle = "black";
                ctx.fillRect(x, y, SIZE, SIZE);
            }} else if (cell === 'X' || cell === 'O') {{
                ctx.fillStyle = "black";
                ctx.font = `bold ${{SIZE * 0.7}}px Arial`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(cell, x + SIZE/2, y + SIZE/2);
            }}
        }}
    }}
}}

// Håndter klik/tegn
canvas.addEventListener('mousedown', (e) => {{
    if (isPan) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const c = Math.floor(x / SIZE);
    const r = Math.floor(y / SIZE);
    
    if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {{
        const mode = document.getElementById("mode").value;
        if (mode === "erase") gridData[r][c] = null;
        else if (mode === "fill") gridData[r][c] = gridData[r][c] === 'fill' ? null : 'fill';
        else gridData[r][c] = gridData[r][c] === mode ? null : mode;
        draw();
    }}
}});

function togglePan() {{
    isPan = !isPan;
    document.getElementById("panBtn").classList.toggle("active-tool");
    view.classList.toggle("pan-active");
    view.style.touchAction = isPan ? "auto" : "none";
}}

function clearGrid() {{
    if(confirm("Vil du rydde hele mønsteret?")) {{
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }}
}}

// Eksport funktion der virker hver gang
function exportSmart(type) {{
    const scale = 2; // Højere opløsning til eksport
    const s = SIZE * scale;
    const m = MARGIN * scale;
    
    const out = document.createElement("canvas");
    out.width = (COLS * s) + (m * 2);
    out.height = (ROWS * s) + (m * 2);
    const octx = out.getContext("2d");
    
    // Hvid baggrund (Margen)
    octx.fillStyle = "white";
    octx.fillRect(0, 0, out.width, out.height);
    
    // Tegn grid linjer på eksport
    octx.strokeStyle = "#ccc";
    octx.lineWidth = 1;
    
    // Lodrette linjer
    for (let c = 0; c <= COLS; c++) {{
        octx.beginPath();
        octx.moveTo(c * s + m, 0);
        octx.lineTo(c * s + m, out.height);
        octx.stroke();
    }}
    
    // Vandre linjer
    for (let r = 0; r <= ROWS; r++) {{
        octx.beginPath();
        octx.moveTo(0, r * s + m);
        octx.lineTo(out.width, r * s + m);
        octx.stroke();
    }}
    
    // Tegn celler
    for (let r = 0; r < ROWS; r++) {{
        for (let c = 0; c < COLS; c++) {{
            const x = c * s + m;
            const y = r * s + m;
            
            const cell = gridData[r][c];
            if (cell === 'fill') {{
                octx.fillStyle = "black";
                octx.fillRect(x, y, s, s);
            }} else if (cell === 'X' || cell === 'O') {{
                octx.fillStyle = "black";
                octx.font = `bold ${{s * 0.7}}px Arial`;
                octx.textAlign = "center";
                octx.textBaseline = "middle";
                octx.fillText(cell, x + s/2, y + s/2);
            }}
        }}
    }}
    
    const dataUrl = out.toDataURL("image/png");
    if (type === 'png') {{
        const a = document.createElement("a");
        a.download = "design.png";
        a.href = dataUrl;
        a.click();
    }} else {{
        const win = window.open('', '_blank');
        win.document.write('<html><body style="margin:0;display:flex;justify-content:center;background:#fff;">');
        win.document.write('<img src="' + dataUrl + '" style="max-width:100%; height:auto;" onload="window.print();window.close();">');
        win.document.write('</body></html>');
    }}
}}

draw();
</script>
</body>
</html>
"""

components.html(html_code, height=1100, scrolling=False)
st.caption("Grid Designer Pro – Panorer, tegn og eksportér med sikkerhedsmargin.")
