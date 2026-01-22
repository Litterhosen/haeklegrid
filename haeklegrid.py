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

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Indstillinger")
    cols = st.number_input("Kolonner", min_value=120, max_value=400, value=120)
    rows = st.number_input("Rækker", min_value=120, max_value=400, value=120)
    cell_size = st.slider("Zoom (px per felt)", 5, 60, 20)

    st.divider()
    uploaded = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])

    import_data = []
    if uploaded:
        img = Image.open(uploaded).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.argwhere(arr < 128).flatten().tolist()

    st.write("Klik udenfor panelet for at lukke.")

# ---------- HTML ----------
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
body {{ margin:0; background:#f2f2f2; font-family:-apple-system, Arial, sans-serif; display:flex; flex-direction:column; height:100vh; }}
.toolbar {{ position:sticky; top:0; background:white; padding:10px; border-bottom:1px solid #ddd; display:flex; flex-wrap:wrap; gap:8px; z-index:1000; justify-content:center; }}
button, select {{ padding:10px 14px; border-radius:8px; border:1px solid #ccc; background:white; cursor:pointer; font-weight:600; }}
button.primary {{ background:#007aff; color:white; border:none; }}
button.active-tool {{ background:#5856d6; color:white; }}
.grid-wrap {{ flex:1; overflow:auto; -webkit-overflow-scrolling: touch; padding:20px; background:#e5e5e5; touch-action: none; }}
.grid {{ display:grid; gap:1px; width:fit-content; margin:0 auto; background:white; box-shadow:0 0 10px rgba(0,0,0,0.1); }}
.cell {{ background:white; display:flex; align-items:center; justify-content:center; font-weight:bold; user-select:none; }}
.cell.active {{ background:black; color:white; }}
.pan-mode .cell {{ pointer-events:none; cursor:grab; }}
.grid-wrap.pan-active {{ cursor:grab; }}
@media print {{ .toolbar{{display:none !important;}} .grid-wrap{{overflow:visible; padding:0; background:white;}} body{{background:white;}} .cell{{border:0.1pt solid #eee;}} }}
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
    <button class="primary" onclick="exportPNG()">💾 Gem PNG</button>
    <button onclick="exportPDF()">🖨️ PDF</button>
    <button onclick="clearGrid()">🗑️ Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS={cols};
const ROWS={rows};
const SIZE={cell_size};
const IMPORT={json.dumps(import_data)};

let isPan=false;
const grid=document.getElementById("grid");
const view=document.getElementById("view");

// Sæt grid kolonner korrekt
grid.style.gridTemplateColumns = "repeat(" + COLS + ", " + SIZE + "px)";

// Generer celler
for(let i=0;i<ROWS*COLS;i++){{
    const cell=document.createElement("div");
    cell.className="cell";
    cell.style.width=SIZE+"px";
    cell.style.height=SIZE+"px";
    cell.style.fontSize=(SIZE*0.6)+"px";
    cell.onclick=function(){{
        if(isPan) return;
        const mode=document.getElementById("mode").value;
        if(mode==="fill"){{ cell.textContent=""; cell.classList.toggle("active"); }}
        else if(mode==="erase"){{ cell.textContent=""; cell.classList.remove("active"); }}
        else{{ cell.classList.remove("active"); cell.textContent=cell.textContent===mode?"":mode; }}
    }};
    grid.appendChild(cell);
}}

// Import billede
IMPORT.forEach(idx=>{{
    const r=Math.floor(idx/COLS);
    const c=idx%COLS;
    const cell=grid.children[r*COLS+c];
    if(cell) cell.classList.add("active");
}});

function togglePan(){{
    isPan=!isPan;
    document.getElementById("panBtn").classList.toggle("active-tool");
    grid.classList.toggle("pan-mode");
    view.classList.toggle("pan-active");
    view.style.touchAction=isPan?"auto":"none";
}}

function clearGrid(){{
    if(!confirm("Vil du slette alt?")) return;
    document.querySelectorAll(".cell").forEach(c=>{{ c.textContent=""; c.classList.remove("active"); }});
}}

// Pixel-perfekt PNG med margin
function exportPNG(){{
    const MARGIN=80;
    const SCALE=3;
    html2canvas(grid,{{backgroundColor:"#ffffff", scale:SCALE}}).then(c=>{{
        const out=document.createElement("canvas");
        out.width=c.width+MARGIN*2*SCALE;
        out.height=c.height+MARGIN*2*SCALE;
        const ctx=out.getContext("2d");
        ctx.imageSmoothingEnabled=false;
        ctx.fillStyle="#ffffff";
        ctx.fillRect(0,0,out.width,out.height);
        ctx.drawImage(c,MARGIN*SCALE,MARGIN*SCALE);
        const link=document.createElement("a");
        link.download="design-grid.png";
        link.href=out.toDataURL("image/png");
        link.click();
    }});
}}

// PDF / print med margin
function exportPDF(){{
    html2canvas(grid,{{backgroundColor:"#ffffff", scale:2}}).then(c=>{{
        const win=window.open("");
        const img=c.toDataURL("image/png");
        win.document.write('<html><body style="margin:0; display:flex; justify-content:center;">');
        win.document.write('<img src="'+img+'" style="width:100%; height:auto; margin:40px 0;">');
        win.document.write('</body></html>');
        win.document.close();
        win.focus();
        win.print();
    }});
}}
</script>
</body>
</html>
"""

components.html(html, height=1000, scrolling=False)
st.caption("Ultimate Grid Designer – pan, pinch-zoom, import og pixel-perfekt eksport")
