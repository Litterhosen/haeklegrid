import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(page_title="Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

# Skjul Streamlit UI
st.markdown("<style>header, footer, .stDeployButton {display:none !important;} [data-testid='stHeader'] {display:none !important;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 120)
    rows = st.number_input("Rækker", 5, 400, 120)
    cell_size = st.slider("Zoom (Feltstørrelse)", 5, 50, 20)
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
    <style>
        body { margin: 0; font-family: sans-serif; background: #ddd; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .toolbar { background: #fff; padding: 10px; display: flex; gap: 8px; justify-content: center; border-bottom: 2px solid #bbb; z-index: 10; flex-wrap: wrap; }
        .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 20px; -webkit-overflow-scrolling: touch; }
        canvas { background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.2); cursor: crosshair; }
        button, select { padding: 10px 15px; border-radius: 8px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; }
        .btn-blue { background: #007aff; color: white; border: none; }
    </style>
</head>
<body>
    <div class="toolbar">
        <select id="mode">
            <option value="fill">⚫ Sort</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ Ryd</option>
        </select>
        <button class="btn-blue" onclick="downloadImage()">📸 Gem Billede</button>
        <button class="btn-blue" style="background:#34c759" onclick="printCanvas()">🖨️ Gem som PDF</button>
        <button onclick="clearCanvas()">🗑️ Ryd alt</button>
    </div>

    <div class="viewport">
        <canvas id="gridCanvas"></canvas>
    </div>

    <script>
    const COLS = __COLS__;
    const ROWS = __ROWS__;
    const SIZE = __SIZE__;
    const IMPORT_DATA = __IMPORT_DATA__;

    const canvas = document.getElementById('gridCanvas');
    const ctx = canvas.getContext('2d');
    
    // Data storage
    let gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));

    // Setup canvas size
    canvas.width = COLS * SIZE;
    canvas.height = ROWS * SIZE;

    // Load Import Data
    if (IMPORT_DATA.length > 0) {
        IMPORT_DATA.forEach(idx => {
            const r = Math.floor(idx / COLS);
            const c = idx % COLS;
            gridData[r][c] = 'fill';
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * SIZE;
                const y = r * SIZE;
                
                // Draw Cell Background
                if (gridData[r][c] === 'fill') {
                    ctx.fillStyle = '#000';
                    ctx.fillRect(x, y, SIZE, SIZE);
                } else {
                    ctx.strokeStyle = '#ccc';
                    ctx.strokeRect(x, y, SIZE, SIZE);
                    
                    if (gridData[r][c] === 'X' || gridData[r][c] === 'O') {
                        ctx.fillStyle = '#000';
                        ctx.font = `bold ${SIZE * 0.7}px Arial`;
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(gridData[r][c], x + SIZE/2, y + SIZE/2);
                    }
                }
            }
        }
    }

    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const c = Math.floor(x / SIZE);
        const r = Math.floor(y / SIZE);
        
        const mode = document.getElementById('mode').value;
        if (mode === 'erase') gridData[r][c] = null;
        else if (mode === 'fill') gridData[r][c] = (gridData[r][c] === 'fill') ? null : 'fill';
        else gridData[r][c] = (gridData[r][c] === mode) ? null : mode;
        
        draw();
    });

    function downloadImage() {
        const link = document.createElement('a');
        link.download = 'moenster.png';
        link.href = canvas.toDataURL();
        link.click();
    }

    function printCanvas() {
        const dataUrl = canvas.toDataURL();
        const win = window.open('', '_blank');
        win.document.write('<html><body style="margin:0; display:flex; justify-content:center;">');
        win.document.write('<img src="' + dataUrl + '" style="width:100%; height:auto;" onload="window.print();window.close();">');
        win.document.write('</body></html>');
        win.document.close();
    }

    function clearCanvas() {
        if(confirm("Ryd alt?")) {
            gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
            draw();
        }
    }

    draw();
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
