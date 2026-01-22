import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v6", layout="wide", initial_sidebar_state="collapsed")

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

    /* MENU (Fastgjort i toppen) */
    .toolbar { 
        position: fixed; top: 0; left: 0; right: 0;
        background: var(--toolbar-bg); 
        padding: 8px; display: flex; flex-direction: column; gap: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4); z-index: 1000;
    }

    .row { display: flex; justify-content: space-between; align-items: center; gap: 6px; }
    .group { display: flex; align-items: center; gap: 5px; background: #f1f3f5; padding: 4px 10px; border-radius: 10px; border: 1px solid #dee2e6; }

    button, select, input { 
        height: 42px; border-radius: 8px; border: 1px solid #ccc;
        font-size: 13px; font-weight: bold; cursor: pointer; background: white;
    }

    .btn-icon { width: 44px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .btn-text { flex: 1; padding: 0 10px; }
    .btn-blue { background: var(--btn-blue); color: white; border: none; }
    .btn-green { background: var(--btn-green); color: white; border: none; }
    .btn-red { background: var(--btn-red); color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }

    /* GRID OMRÅDE */
    .viewport { 
        width: 100vw; height: 100vh; overflow: auto; 
        padding-top: 140px; /* Plads til menu */
        background: #34495e; -webkit-overflow-scrolling: touch;
    }
    
    canvas { background: white; transform-origin: 0 0; display: block; box-shadow: 0 0 30px rgba(0,0,0,0.6); }

    .size-input { width: 45px; text-align: center; font-size: 16px; }
    #imgInput { display: none; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="row">
        <div class="group">
            <input type="number" id="rows" value="114" class="size-input"> rk x 
            <input type="number" id="cols" value="23" class="size-input"> mk
            <button class="btn-text" onclick="resizeGrid()" style="background:#ccc;">OK</button>
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
        <button id="panBtn" class="btn-icon" onclick="togglePan()" title="Flyt side">✋</button>
        <div class="group">
            <button class="btn-icon" onclick="zoomGrid(0.2)">➕</button>
            <button class="btn-icon" onclick="zoomGrid(-0.2)">➖</button>
        </div>
    </div>

    <div class="row">
        <button class="btn-text btn-blue" onclick="document.getElementById('imgInput').click()">📥 HENT FOTO</button>
        <input type="file" id="imgInput" accept="image/*">
        
        <button class="btn-text btn-green" onclick="exportPDF()">📄 GEM PDF</button>
        <button class="btn-text" onclick="exportPNG()">🖼️ PNG</button>
        
        <button class="btn-icon btn-red" onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 45;
    let gridData = [], history = [], redoStack = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    // 1. AUTO-SAVE & INDLÆSNING
    function init() {
        const saved = localStorage.getItem('haekleGridData');
        const sRows = localStorage.getItem('haekleGridRows');
        const sCols = localStorage.getItem('haekleGridCols');

        if (saved && sRows && sCols) {
            gridData = JSON.parse(saved);
            ROWS = parseInt(sRows);
            COLS = parseInt(sCols);
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

    // 2. SIKKER JUSTERING AF MÅL
    function resizeGrid() {
        const nR = parseInt(document.getElementById('rows').value);
        const nC = parseInt(document.getElementById('cols').value);
        saveHistory();
        let old = JSON.parse(JSON.stringify(gridData));
        gridData = Array(nR).fill().map(() => Array(nC).fill(null));
        for (let r = 0; r < Math.min(ROWS, nR); r++) {
            for (let c = 0; c < Math.min(COLS, nC); c++) {
                gridData[r][c] = old[r][c];
            }
        }
        ROWS = nR; COLS = nC;
        updateCanvas();
        autoSave();
    }

    function updateCanvas() {
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        draw();
    }

    function drawOnContext(tCtx, s, off, isExport = false) {
        const margin = isExport ? 40 : 0;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
        
        // Gitterlinjer
        for (let i = 0; i <= COLS; i++) {
            const x = i * s + off + margin;
            tCtx.beginPath();
            tCtx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
            tCtx.lineWidth = (i % 5 === 0) ? 1.5 : 0.8;
            tCtx.moveTo(x, off + margin); tCtx.lineTo(x, (ROWS * s) + off + margin);
            tCtx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {
                tCtx.font = "bold 12px Arial"; tCtx.fillStyle = "#000"; tCtx.textAlign = "center";
                tCtx.fillText(i+1, x + s/2, off + margin - 12);
            }
        }
        for (let j = 0; j <= ROWS; j++) {
            const y = j * s + off + margin;
            tCtx.beginPath();
            tCtx.strokeStyle = (j % 10 === 0) ? "#000" : (j % 5 === 0 ? "#888" : "#ddd");
            tCtx.lineWidth = (j % 5 === 0) ? 1.5 : 0.8;
            tCtx.moveTo(off + margin, y); tCtx.lineTo((COLS * s) + off + margin, y);
            tCtx.stroke();
            if (j < ROWS && (j+1 === 1 || (j+1) % 5 === 0)) {
                tCtx.font = "bold 12px Arial"; tCtx.fillStyle = "#000"; tCtx.textAlign = "right";
                tCtx.fillText(j+1, off + margin - 10, y + s/1.5);
            }
        }

        // Tegn indhold
        tCtx.textAlign = "center";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (!gridData[r][c]) continue;
                const x = c * s + off + margin, y = r * s + off + margin;
                if (gridData[r][c] === 'fill') {
                    tCtx.fillStyle = "black"; tCtx.fillRect(x+1, y+1, s-1, s-1);
                } else {
                    tCtx.fillStyle = "black"; tCtx.font = `bold ${s * 0.7}px Arial`;
                    tCtx.fillText(gridData[r][c], x + s/2, y + s/1.3);
                }
            }
        }
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    function saveHistory() {
        history.push(JSON.stringify(gridData));
        if (history.length > 50) history.shift();
        redoStack = [];
    }

    // 3. MOBIL TOUCH LOGIK
    canvas.addEventListener('pointerdown', e => {
        if (isPan) { isDown = true; return; }
        const rect = canvas.getBoundingClientRect();
        const c = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const r = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            saveHistory();
            const m = document.getElementById('mode').value;
            gridData[r][c] = (gridData[r][c] === m ? null : (m === 'erase' ? null : m));
            draw(); autoSave();
        }
    });

    let isDown = false;
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
    });
    window.addEventListener('pointerup', () => isDown = false);

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function zoomGrid(v) { scale = Math.max(0.1, scale + v); canvas.style.transform = `scale(${scale})`; }
    function undo() { if(history.length) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); autoSave(); } }
    function redo() { if(redoStack.length) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); autoSave(); } }

    // 4. EKSPORT (PDF RETTET)
    function exportPNG() {
        const url = canvas.toDataURL("image/png");
        const a = document.createElement('a'); a.download = "haekle-design.png"; a.href = url; a.click();
    }

    async function exportPDF() {
        const { jsPDF } = window.jspdf;
        
        // Lav en midlertidig canvas i høj opløsning til PDF
        const tempCanvas = document.createElement('canvas');
        const exportScale = 2; // Højere kvalitet
        tempCanvas.width = ((COLS * SIZE) + OFFSET + 80) * exportScale;
        tempCanvas.height = ((ROWS * SIZE) + OFFSET + 80) * exportScale;
        
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.scale(exportScale, exportScale);
        drawOnContext(tempCtx, SIZE, OFFSET, true);

        const imgData = tempCanvas.toDataURL("image/png");
        
        // Beregn PDF dimensioner (A4 er 210x297mm)
        // Hvis mønsteret er meget langt, laver vi en lang PDF-side i stedet for at klippe det over
        const pdfW = 210;
        const pdfH = (tempCanvas.height * pdfW) / tempCanvas.width;
        
        const pdf = new jsPDF('p', 'mm', [pdfW, pdfH]);
        pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH);
        pdf.save("haekle-moenster.pdf");
    }

    // 5. IMPORT FOTO
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
                    gridData[Math.floor((i/4)/COLS)][(i/4)%COLS] = avg < 125 ? 'fill' : null;
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
