import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(page_title="Grid Designer", layout="wide", initial_sidebar_state="collapsed")

# Tvinger Streamlit UI til at forsvinde HELT
st.markdown("""
    <style>
    header, footer, .stDeployButton {display:none !important;}
    [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 120)
    rows = st.number_input("Rækker", 5, 400, 120)
    cell_size = st.slider("Zoom", 5, 60, 20)
    st.divider()
    uploaded = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])
    import_data = []
    if uploaded:
        img = Image.open(uploaded).convert("L").resize((cols, rows), Image.NEAREST)
        import_data = np.where(np.array(img).flatten() < 128)[0].tolist()

# Navngivet 'html_template' for at undgå fejl
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; font-family: sans-serif; background: #ccc; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
    
    .menu-bar { 
        background: #333; color: white; padding: 10px; 
        display: flex; gap: 10px; justify-content: center; align-items: center;
        z-index: 9999; border-bottom: 2px solid #000; flex-wrap: wrap;
    }
    
    .view-area { flex: 1; overflow: auto; padding: 40px; display: flex; justify-content: center; -webkit-overflow-scrolling: touch; }
    
    .grid { display: grid; gap: 1px; background: #999; border: 2px solid #000; width: fit-content; background-color: white; }
    .cell { background: white; width: var(--sz); height: var(--sz); display: flex; align-items: center; justify-content: center; font-weight: bold; font-family: Arial; user-select: none; }
    .cell.active { background: black !important; }
    
    button, select { padding: 12px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; }
    .btn-green { background: #28a745; color: white; }
    .btn-blue { background: #007aff; color: white; }
    .btn-pan.active { background: #ff9500 !important; color: white !important; }
</style>
</head>
<body>

<div class="menu-bar">
    <select id="tool">
        <option value="fill">SORT</option>
        <option value="X">Symbol X</option>
        <option value="O">Symbol O</option>
        <option value="erase">SLET</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="btn-blue" onclick="doExport('png')">📸 GEM BILLEDE</button>
    <button class="btn-green" onclick="doExport('pdf')">🖨️ PDF</button>
    <button onclick="location.reload()">🗑️ RYD ALT</button>
</div>

<div class="view-area" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = __COLS__, ROWS = __ROWS__, SIZE = __SIZE__, IMPORT = __IMPORT__;
let isPan = false;
const grid = document.getElementById("grid");
const view = document.getElementById("view");

grid.style.setProperty('--sz', SIZE + "px");
grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

// Generer celler
for (let i = 0; i < ROWS * COLS; i++) {
    const c = document.createElement("div");
    c.className = "cell";
    c.style.fontSize = (SIZE * 0.7) + "px";
    if (IMPORT.includes(i)) c.classList.add("active");
    
    c.onclick = function() {
        if (isPan) return;
        const tool = document.getElementById("tool").value;
        if (tool === "fill") { c.textContent = ""; c.classList.toggle("active"); }
        else if (tool === "erase") { c.textContent = ""; c.classList.remove("active"); }
        else { c.classList.remove("active"); c.textContent = c.textContent === tool ? "" : tool; }
    };
    grid.appendChild(c);
}

function togglePan() {
    isPan = !isPan;
    document.getElementById("panBtn").classList.toggle("active");
    view.style.touchAction = isPan ? "auto" : "none";
}

function doExport(type) {
    const scale = 2; // Høj opløsning
    const margin = 120; // Din ønskede margen
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const s = SIZE * scale;

    canvas.width = (COLS * s) + (margin * 2);
    canvas.height = (ROWS * s) + (margin * 2);
    
    // Hvid baggrund (margen)
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const cells = grid.children;
    for(let i=0; i<cells.length; i++) {
        const r = Math.floor(i/COLS), col = i%COLS;
        const x = margin + (col * s), y = margin + (r * s);
        
        if(cells[i].classList.contains("active")) {
            ctx.fillStyle = "black";
            ctx.fillRect(x, y, s, s);
        } else {
            ctx.strokeStyle = "#ccc";
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, s, s);
            if(cells[i].textContent) {
                ctx.fillStyle = "black";
                ctx.font = `bold ${s*0.7}px Arial`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(cells[i].textContent, x+s/2, y+s/2);
            }
        }
    }

    const data = canvas.toDataURL("image/png");
    if(type === 'png') {
        const a = document.createElement("a");
        a.download = "moenster.png"; a.href = data; a.click();
    } else {
        const w = window.open();
        w.document.write(`<html><body style="margin:0; display:flex; justify-content:center;">
            <img src="${data}" style="max-width:100%; height:auto;" onload="window.print();window.close();">
            </body></html>`);
    }
}
</script>
</body>
</html>
"""

# Her blev 'html' rettet til 'html_template'
final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT__", json.dumps(import_data))
)

components.html(final_html, height=1200, scrolling=False)
