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
        canvas { background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.2); cursor: crosshair; touch-action: none; }
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
        <button class="btn-blue" onclick="exportWithMargin('png')">📸 Gem Billede</button>
        <button class="btn-blue" style="background:#34c759" onclick="exportWithMargin('pdf')">🖨️ Gem som PDF</button>
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
    const MARGIN = 60; // Margen i pixels for at undgå telefon-overlap

    const canvas = document.getElementById('gridCanvas');
    const ctx = canvas.getContext('2d');
    
    let gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));

    canvas.width = COLS * SIZE;
    canvas.height = ROWS * SIZE;

    if (IMPORT_DATA.length > 0) {
        IMPORT_DATA.forEach(idx => {
            const r = Math.floor(idx / COLS);
            const c = idx % COLS;
            gridData[r][c] = 'fill';
        });
    }

    function draw(targetCtx, scale = 1, withMargin = false) {
        const sSize = SIZE * scale;
        const offset = withMargin ? MARGIN : 0;
        
        // Hvid baggrund
        targetCtx.fillStyle = "#ffffff";
        targetCtx.fillRect(0, 0, targetCtx.canvas.width, targetCtx.canvas.height);
        
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * sSize + offset;
                const y = r * sSize + offset;
                
                if (gridData[r][c] === 'fill') {
                    targetCtx.fillStyle = '#000';
                    targetCtx.fillRect(x, y, sSize, sSize);
                } else {
                    targetCtx.strokeStyle = '#ccc';
                    targetCtx.lineWidth = 1 * scale;
                    targetCtx.strokeRect(x, y, sSize, sSize);
                    
                    if (gridData[r][c] === 'X' || gridData[r][c] === 'O') {
                        targetCtx.fillStyle = '#000';
                        targetCtx.font = `bold ${sSize * 0.7}px Arial`;
                        targetCtx.textAlign = "center";
                        targetCtx.textBaseline = "middle";
                        targetCtx.fillText(gridData[r][c], x + sSize/2, y + sSize/2);
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
        
        draw(ctx);
    });

    function exportWithMargin(type) {
        // Skab et usynligt canvas i høj opløsning (High DPI)
        const exportCanvas = document.createElement('canvas');
        const exportCtx = exportCanvas.getContext('2d');
        const scale = 4; // 4x opløsning for super skarpe pixels
        
        exportCanvas.width = (COLS * SIZE * scale) + (MARGIN * 2);
        exportCanvas.height = (ROWS * SIZE * scale) + (MARGIN * 2);
        
        draw(exportCtx, scale, true);
        
        const dataUrl = exportCanvas.toDataURL("image/png");

        if (type === 'png') {
            const link = document.createElement('a');
            link.download = 'skarp-moenster.png';
            link.href = dataUrl;
            link.click();
        } else {
            const win = window.open('', '_blank');
            win.document.write('<html><body style="margin:0; background:#fff; display:flex; justify-content:center;">');
            win.document.write('<img src="' + dataUrl + '" style="width:100%; height:auto;" onload="window.print();window.close();">');
            win.document.write('</body></html>');
            win.document.close();
        }
    }

    function clearCanvas() {
        if(confirm("Ryd alt?")) {
            gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
            draw(ctx);
        }
    }

    draw(ctx);
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
