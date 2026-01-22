import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(page_title="Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

# Skjul alt Streamlit UI
st.markdown("<style>header, footer, .stDeployButton {display:none !important;} [data-testid='stHeader'] {display:none !important;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 60)
    rows = st.number_input("Rækker", 5, 400, 60)
    cell_size = st.slider("Felt størrelse", 5, 50, 20)
    st.divider()
    uploaded_file = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])
    
    import_data = []
    if uploaded_file:
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        body { margin: 0; font-family: sans-serif; background: #ddd; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .toolbar { background: #fff; padding: 10px; display: flex; gap: 8px; justify-content: center; border-bottom: 2px solid #bbb; z-index: 10; }
        .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 20px; -webkit-overflow-scrolling: touch; }
        .grid { display: grid; gap: 1px; background: #888; border: 1px solid #000; width: fit-content; background-color: white; }
        .cell { background: #fff; width: var(--sz); height: var(--sz); display: flex; align-items: center; justify-content: center; user-select: none; }
        .cell.active { background: #000 !important; }
        button { padding: 10px 15px; border-radius: 8px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; }
        .btn-blue { background: #007aff; color: white; border: none; }
    </style>
</head>
<body>
    <div class="toolbar">
        <select id="mode" style="padding:10px;">
            <option value="fill">⚫ Sort</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ Ryd</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
        <button class="btn-blue" onclick="exportFinal('png')">📸 Gem Billede</button>
        <button class="btn-blue" style="background:#34c759" onclick="exportFinal('pdf')">🖨️ Gem som PDF</button>
    </div>

    <div class="viewport" id="vp">
        <div id="grid" class="grid"></div>
    </div>

    <script>
    const COLS = __COLS__; const ROWS = __ROWS__; const SIZE = __SIZE__; const IMPORT_DATA = __IMPORT_DATA__;
    let isPan = false;
    const grid = document.getElementById("grid");
    grid.style.setProperty('--sz', SIZE + "px");
    grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

    const importSet = new Set(IMPORT_DATA);
    for (let i = 0; i < ROWS * COLS; i++) {
        const c = document.createElement("div");
        c.className = "cell";
        if (importSet.has(i)) c.classList.add("active");
        c.onclick = function() {
            if (isPan) return;
            const m = document.getElementById("mode").value;
            if (m === "fill") { c.textContent = ""; c.classList.toggle("active"); }
            else if (m === "erase") { c.textContent = ""; c.classList.remove("active"); }
            else { c.classList.remove("active"); c.textContent = c.textContent === m ? "" : m; }
        };
        grid.appendChild(c);
    }

    function togglePan() {
        isPan = !isPan;
        document.getElementById("panBtn").style.background = isPan ? "#5856d6" : "#eee";
        document.getElementById("panBtn").style.color = isPan ? "white" : "black";
        document.getElementById("vp").style.touchAction = isPan ? "auto" : "none";
    }

    function exportFinal(type) {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = "Arbejder...";

        html2canvas(grid, { backgroundColor: "#ffffff", scale: 2 }).then(canvas => {
            const imgData = canvas.toDataURL("image/png");
            
            if (type === 'png') {
                const link = document.createElement("a");
                link.download = "moenster.png";
                link.href = imgData;
                link.click();
            } else {
                // PDF-udgave: Vi åbner billedet i et nyt vindue dedikeret til print
                const win = window.open('', '_blank');
                win.document.write('<html><body style="margin:0; display:flex; justify-content:center;">');
                win.document.write('<img src="' + imgData + '" style="width:100%; max-width:100%; height:auto;" onload="window.print();window.close();">');
                win.document.write('</body></html>');
                win.document.close();
            }
            btn.textContent = originalText;
        });
    }
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

components.html(final_html, height=850, scrolling=False)
