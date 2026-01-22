import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v5", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    body { background: #1a252f; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
    :root {
        --bg-dark: #2c3e50;
        --toolbar-bg: #ffffff;
        --btn-blue: #3498db;
        --btn-green: #27ae60;
        --btn-red: #e74c3c;
    }

    body { margin: 0; font-family: -apple-system, sans-serif; background: var(--bg-dark); height: 100vh; overflow: hidden; }

    /* MENU-STRUKTUR (Top-fixeret) */
    .toolbar { 
        position: fixed; top: 0; left: 0; right: 0;
        background: var(--toolbar-bg); 
        padding: 6px; display: flex; flex-direction: column; gap: 6px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4); z-index: 1000;
    }

    .row { display: flex; justify-content: space-between; align-items: center; gap: 4px; }
    .group { display: flex; align-items: center; gap: 3px; background: #f0f2f6; padding: 3px 6px; border-radius: 8px; }

    button, select, input { 
        height: 38px; border-radius: 6px; border: 1px solid #ccc;
        font-size: 12px; font-weight: bold; cursor: pointer; background: white;
    }

    .btn-action { background: #eee; color: #333; flex: 1; }
    .btn-save-png { background: var(--btn-blue); color: white; border: none; }
    .btn-save-pdf { background: var(--btn-green); color: white; border: none; }
    .btn-icon { width: 38px; font-size: 16px; }
    .active-tool { background: #f1c40f !important; border-color: #f39c12 !important; }

    /* VIEWPORT */
    .viewport { 
        width: 100vw; height: 100vh; overflow: auto; 
        padding-top: 135px; /* Plads til 3 rækker menu */
        background: #34495e; -webkit-overflow-scrolling: touch;
    }
    
    canvas { background: white; transform-origin: 0 0; display: block; image-rendering: pixelated; }

    .size-input { width: 35px; text-align: center; }
    #imgInput { display: none; }
    .label-small { font-size: 10px; color: #666; margin-bottom: 2px; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="row">
        <div class="group" style="flex-grow: 1;">
            <span style="font-size: 11px;">Mål:</span>
            <input type="number" id="rows" value="114" class="size-input"> x 
            <input type="number" id="cols" value="23" class="size-input">
            <button class="btn-action" onclick="resizeGrid()" style="background:#ddd;">OK</button>
        </div>
        <div class="group">
            <button class="btn-icon" onclick="undo()">↩️</button>
            <button class="btn-icon" onclick="redo()">↪️</button>
        </div>
    </div>

    <div class="row">
        <select id="mode" style="flex: 2;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X-MASKE</option>
            <option value="O">⭕ O-MASKE</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" class="btn-icon" onclick="togglePan()">✋</button>
        <div class="group">
            <button class="btn-icon" onclick="zoomGrid(0.2)">➕</button>
            <button class="btn-icon" onclick="zoomGrid(-0.2)">➖</button>
        </div>
    </div>

    <div class="row">
        <button class="btn-action" onclick="document.getElementById('imgInput').click()">📥 HENT FOTO</button>
        <input type="file" id="imgInput" accept="image/*">
        
        <button class="btn-save-png" onclick="exportPNG()" style="flex:1;">🖼️ PNG</button>
        <button class="btn-save-pdf" onclick="exportPDF()" style="flex:1;">📄 PDF</button>
        
        <button class="btn-icon" style="background:var(--btn-red); color:white;" onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 40;
    let gridData = [], history = [], redoStack = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    // INITIALISERING & AUTO-GEM
    function init() {
        const saved = localStorage.getItem('haekleGridData');
        const savedRows = localStorage.getItem('haekleGridRows');
        const savedCols = localStorage.getItem('haekleGridCols');

        if (saved && savedRows && savedCols) {
            gridData = JSON.parse(saved);
            ROWS = parseInt(savedRows);
            COLS = parseInt(savedCols);
            document.getElementById('rows').value = ROWS;
            document.getElementById('cols').value = COLS;
        } else {
            gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        }
        updateCanvas();
    }

    function autoSave() {
        localStorage.setItem('haekleGridData', JSON.stringify(gridData));
        localStorage.setItem('haekleGridRows', ROWS);
        localStorage.setItem('haekleGridCols', COLS);
    }

    function resizeGrid() {
        const newRows = parseInt(document.getElementById('rows').value);
        const newCols = parseInt(document.getElementById('cols').value);
        saveHistory();
        let oldData = JSON.parse(JSON.stringify(gridData));
        gridData = Array(newRows).fill().map(() => Array(newCols).fill(null));
        for (let r = 0; r < Math.min(ROWS, newRows); r++) {
            for (let c = 0; c < Math.min(COLS, newCols); c++) {
                gridData[r][c] = oldData[r][c];
            }
        }
        ROWS = newRows; COLS = newCols;
        updateCanvas();
        autoSave();
    }

    function updateCanvas() {
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        draw();
    }

    function drawOnContext(tCtx, s, off, isExport = false) {
        const margin = isExport ? 50 : 0;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
        
        // Linjer
        for (let i = 0; i <= COLS; i++) {
            const x = i * s + off + margin;
            tCtx.beginPath();
            tCtx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
            tCtx.lineWidth = (i % 5 === 0) ? 1.5 : 0.5;
            tCtx.moveTo(x, off + margin); tCtx.lineTo(x, (ROWS * s) + off + margin);
            tCtx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {
                tCtx.font = "bold 11px Arial"; tCtx.fillStyle = "#444"; tCtx.textAlign = "center";
                tCtx.fillText(i+1, x + s/2, off + margin - 10);
            }
        }
        for (let j = 0; j <= ROWS; j++) {
            const y = j * s + off + margin;
            tCtx.beginPath();
            tCtx.strokeStyle = (j % 10 === 0) ? "#000" : (j % 5 === 0 ? "#888" : "#ddd");
            tCtx.lineWidth = (j % 5 === 0) ? 1.5 : 0.5;
            tCtx.moveTo(off + margin, y); tCtx.lineTo((COLS * s) + off + margin, y);
            tCtx.stroke();
            if (j < ROWS && (j+1 === 1 || (j+1) % 5 === 0)) {
                tCtx.font = "bold 11px Arial"; tCtx.fillStyle = "#444"; tCtx.textAlign = "right";
                tCtx.fillText(j+1, off + margin - 8, y + s/1.5);
            }
        }

        // Felter
        tCtx.textAlign = "center";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (!gridData[r][c]) continue;
                const x = c * s + off + margin, y = r * s + off + margin;
                if (gridData[r][c] === 'fill') {
                    tCtx.fillStyle = "black"; tCtx.fillRect(x+1, y+1, s-1, s-1);
                } else {
                    tCtx.fillStyle = "black"; tCtx.font = `bold ${s * 0.6}px Arial`;
                    tCtx.fillText(gridData[r][c], x + s/2, y + s/1.3);
                }
            }
        }
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    function saveHistory() {
        history.push(JSON.stringify(gridData));
        if (history.length > 30) history.shift();
        redoStack = [];
    }

    // Touch Logik
    canvas.addEventListener('pointerdown', e => {
        if (isPan) { isDown = true; return; }
        const rect = canvas.getBoundingClientRect();
        const c = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const r = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            saveHistory();
            const m = document.getElementById('mode').value;
            gridData[r][c] = (gridData[r][c] === m ? null : (m === 'erase' ? null : m));
            draw();
            autoSave();
        }
    });

    let isDown = false;
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
    });
    window.addEventListener('pointerup', () => isDown = false);

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function zoomGrid(v) { scale = Math.max(0.2, scale + v); canvas.style.transform = `scale(${scale})`; }
    function undo() { if(history.length) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); autoSave(); } }
    function redo() { if(redoStack.length) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); autoSave(); } }

    // EKSPORT FUNKTIONER
    function exportPNG() {
        const url = canvas.toDataURL("image/png");
        const a = document.createElement('a'); a.download = "haekle-moenster.png"; a.href = url; a.click();
    }

    async function exportPDF() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgData = canvas.toDataURL("image/png");
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save("haekle-moenster.pdf");
    }

    // IMPORT FOTO
    document.getElementById('imgInput').onchange = function(e) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                saveHistory();
                const tCanvas = document.createElement('canvas'); tCanvas.width = COLS; tCanvas.height = ROWS;
                const tCtx = tCanvas.getContext('2d'); tCtx.drawImage(img, 0, 0, COLS, ROWS);
                const pix = tCtx.getImageData(0, 0, COLS, ROWS).data;
                for(let i=0; i<pix.length; i+=4) {
                    const avg = (pix[i]+pix[i+1]+pix[i+2])/3;
                    gridData[Math.floor((i/4)/COLS)][(i/4)%COLS] = avg < 120 ? 'fill' : null;
                }
                draw(); autoSave();
            }
            img.src = event.target.result;
        }
        reader.readAsDataURL(e.target.files[0]);
    };

    function resetCanvas() { if(confirm("Vil du slette ALT?")) { localStorage.clear(); location.reload(); } }
    
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
