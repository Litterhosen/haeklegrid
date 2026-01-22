import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json
import base64

st.set_page_config(page_title="Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

# Skjul Streamlit UI
st.markdown("<style>header, footer, .stDeployButton {display:none;} [data-testid='stHeader'] {display:none;}</style>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 60)
    rows = st.number_input("Rækker", 5, 400, 60)
    cell_size = st.slider("Zoom", 5, 60, 20)
    st.divider()
    uploaded_file = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])
    
    import_data = []
    if uploaded_file:
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

# ---------- HTML & JS KODE ----------
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
    body { margin: 0; font-family: sans-serif; background: #f0f0f0; display: flex; flex-direction: column; height: 100vh; }
    .toolbar { background: white; padding: 10px; border-bottom: 1px solid #ccc; display: flex; gap: 10px; justify-content: center; position: sticky; top:0; z-index:100; }
    .grid-wrap { flex: 1; overflow: auto; padding: 20px; display: flex; justify-content: center; -webkit-overflow-scrolling: touch; }
    .grid { display: grid; gap: 1px; background-color: #000; border: 1px solid #000; width: fit-content; background-color: white; }
    .cell { background-color: white; width: var(--sz); height: var(--sz); display: flex; align-items: center; justify-content: center; font-weight: bold; user-select: none; }
    .cell.active { background-color: black !important; }
    button { padding: 10px 15px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; }
    .btn-main { background: #007aff; color: white; }
    .btn-alt { background: #34c759; color: white; }
    
    @media print {
        .toolbar { display: none !important; }
        .grid-wrap { padding: 0; overflow: visible; }
        .grid { gap: 0; border: 1px solid black; }
        .cell { border: 0.1pt solid black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
</style>
</head>
<body>
    <div class="toolbar" id="tb">
        <select id="mode" style="padding:8px; border-radius:5px;">
            <option value="fill">⚫ Sort</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ Slet</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
        <button class="btn-main" onclick="openInNewTab()">🚀 ÅBN I NY FANE (Til Print/Gem)</button>
        <button class="btn-alt" onclick="window.print()">🖨️ PDF / Print</button>
    </div>
    <div class="grid-wrap" id="view">
        <div id="grid" class="grid"></div>
    </div>

    <script>
    const COLS = __COLS__; const ROWS = __ROWS__; const SIZE = __SIZE__; const IMPORT_DATA = __IMPORT_DATA__;
    let isPanMode = false;
    const grid = document.getElementById("grid");
    grid.style.setProperty('--sz', SIZE + "px");
    grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

    function generateGrid(target) {
        const importSet = new Set(IMPORT_DATA);
        for (let i = 0; i < ROWS * COLS; i++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            if (importSet.has(i)) cell.classList.add("active");
            cell.onclick = function() {
                if (isPanMode) return;
                const m = document.getElementById("mode").value;
                if (m === "fill") { cell.textContent = ""; cell.classList.toggle("active"); }
                else if (m === "erase") { cell.textContent = ""; cell.classList.remove("active"); }
                else { cell.classList.remove("active"); cell.textContent = cell.textContent === m ? "" : m; }
            };
            target.appendChild(cell);
        }
    }

    function togglePan() {
        isPanMode = !isPanMode;
        document.getElementById("panBtn").style.background = isPanMode ? "#5856d6" : "#eee";
        document.getElementById("view").style.touchAction = isPanMode ? "auto" : "none";
    }

    function openInNewTab() {
        // Vi tager det nuværende grid-indhold og bygger en ny HTML-side
        const gridClone = document.getElementById("grid").cloneNode(true);
        const style = document.querySelector("style").innerHTML;
        const newWin = window.open('', '_blank');
        newWin.document.write('<html><head><title>Mit Mønster</title><style>' + style + '</style></head><body>');
        newWin.document.write('<div class="toolbar"><button onclick="window.print()">PRØV PRINT HERFRA</button><p>Hold fingeren på mønsteret for at gemme som billede</p></div>');
        newWin.document.write('<div class="grid-wrap">' + gridClone.outerHTML + '</div>');
        newWin.document.write('</body></html>');
        newWin.document.close();
    }

    generateGrid(grid);
    </script>
</body>
</html>
"""

final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT_DATA__", json.dumps(import_data))
)

components.html(final_html, height=1000, scrolling=False)
