import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hækle Grid Mobile", layout="wide", initial_sidebar_state="collapsed")

# Skjul Streamlit UI helt for at give plads til mobilen
st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    body { background: #1a1a1a; }
    </style>
    """, unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {
        --accent: #3498db;
        --bg: #2c3e50;
        --text: #ecf0f1;
        --toolbar: #f8f9fa;
    }

    body { 
        margin: 0; font-family: -apple-system, sans-serif; 
        background: var(--bg); color: var(--text);
        height: 100vh; overflow: hidden;
    }

    /* MOBIL-OPTIMERET MENU (Bund-menu) */
    .mobile-toolbar {
        position: fixed; bottom: 0; left: 0; right: 0;
        background: var(--toolbar);
        display: flex; flex-direction: column;
        padding: 10px; border-top: 2px solid #bdc3c7;
        z-index: 1000; box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
    }

    .toolbar-row { display: flex; justify-content: space-around; gap: 8px; margin-bottom: 8px; }
    
    .group { display: flex; align-items: center; gap: 4px; background: #eee; padding: 4px 8px; border-radius: 10px; }

    button, select, input { 
        height: 44px; /* Apple/Google standard for fingre */
        border-radius: 8px; border: 1px solid #ccc;
        font-size: 14px; font-weight: bold; cursor: pointer;
    }

    .btn-main { background: var(--accent); color: white; border: none; padding: 0 15px; }
    .btn-icon { width: 44px; padding: 0; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .active-tool { background: #f1c40f !important; border-color: #f39c12 !important; }

    /* VIEWPORT OG CANVAS */
    .viewport { 
        width: 100vw; height: calc(100vh - 120px); 
        overflow: auto; padding-top: 10px;
        -webkit-overflow-scrolling: touch;
    }
    
    canvas { 
        background: white; transform-origin: 0 0; 
        display: block; box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }

    .size-input { width: 45px; text-align: center; background: white; border: 1px solid #bbb; }
</style>
</head>
<body>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<div class="mobile-toolbar">
    <div class="toolbar-row">
        <div class="group">
            <input type="number" id="rows" value="114" class="size-input"> x 
            <input type="number" id="cols" value="23" class="size-input">
            <button class="btn-main" onclick="resizeGrid()">Opdatér mål</button>
        </div>
        <button class="btn-icon" onclick="undo()">↩️</button>
        <button class="btn-icon btn-main" onclick="exportSmart()">📸</button>
    </div>

    <div class="toolbar-row">
        <select id="mode" style="flex-grow: 1;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X-MASKER</option>
            <option value="O">⭕ O-MASKER</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" class="btn-icon" onclick="togglePan()">✋</button>
        <button class="btn-icon" onclick="zoomGrid(0.2)">➕</button>
        <button class="btn-icon" onclick="zoomGrid(-0.2)">➖</button>
    </div>
</div>

<script>
    let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 35;
    let gridData = [], history = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    // INITIALISERING
    function init() {
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        updateCanvasSize();
    }

    // DEN VIGTIGE FUNKTION: Ændr størrelse uden at slette design
    function resizeGrid() {
        const newRows = parseInt(document.getElementById('rows').value);
        const newCols = parseInt(document.getElementById('cols').value);
        
        // Gem nuværende data i en kopi
        let oldData = JSON.parse(JSON.stringify(gridData));
        
        // Lav nyt tomt grid
        gridData = Array(newRows).fill().map(() => Array(newCols).fill(null));
        
        // Kopier gammelt indhold over i det nye (så vidt der er plads)
        for (let r = 0; r < Math.min(ROWS, newRows); r++) {
            for (let c = 0; c < Math.min(COLS, newCols); c++) {
                gridData[r][c] = oldData[r][c];
            }
        }
        
        ROWS = newRows;
        COLS = newCols;
        updateCanvasSize();
    }

    function updateCanvasSize() {
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        draw();
    }

    function draw() {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Tegn linjer (Hver 5. og 10. er tydelig)
        for (let i = 0; i <= COLS; i++) {
            const x = i * SIZE + OFFSET;
            ctx.beginPath();
            ctx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
            ctx.lineWidth = (i % 5 === 0) ? 1.5 : 0.5;
            ctx.moveTo(x, OFFSET); ctx.lineTo(x, ROWS * SIZE + OFFSET);
            ctx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {
                ctx.font = "10px Arial"; ctx.fillStyle = "#666";
                ctx.fillText(i+1, x + 5, OFFSET - 5);
            }
        }
        for (let j = 0; j <= ROWS; j++) {
            const y = j * SIZE + OFFSET;
            ctx.beginPath();
            ctx.strokeStyle = (j % 10 === 0) ? "#000" : (j % 5 === 0 ? "#888" : "#ddd");
            ctx.lineWidth = (j % 5 === 0) ? 1.5 : 0.5;
            ctx.moveTo(OFFSET, y); ctx.lineTo(COLS * SIZE + OFFSET, y);
            ctx.stroke();
            if (j < ROWS && (j+1 === 1 || (j+1) % 5 === 0)) {
                ctx.font = "10px Arial"; ctx.fillStyle = "#666";
                ctx.fillText(j+1, 5, y + 15);
            }
        }

        // Tegn indhold
        ctx.textAlign = "center";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (!gridData[r][c]) continue;
                const x = c * SIZE + OFFSET, y = r * SIZE + OFFSET;
                if (gridData[r][c] === 'fill') {
                    ctx.fillStyle = "black"; ctx.fillRect(x+1, y+1, SIZE-2, SIZE-2);
                } else {
                    ctx.fillStyle = "black"; ctx.font = "bold 14px Arial";
                    ctx.fillText(gridData[r][c], x + SIZE/2, y + SIZE/1.4);
                }
            }
        }
    }

    // TOUCH HÅNDTERING
    canvas.addEventListener('pointerdown', e => {
        if (isPan) { isDown = true; return; }
        const rect = canvas.getBoundingClientRect();
        const c = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const r = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            history.push(JSON.stringify(gridData));
            const mode = document.getElementById('mode').value;
            gridData[r][c] = (gridData[r][c] === mode) ? null : (mode === 'erase' ? null : mode);
            draw();
        }
    });

    let isDown = false;
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
    });
    window.addEventListener('pointerup', () => isDown = false);

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function zoomGrid(val) { scale += val; canvas.style.transform = `scale(${scale})`; }
    function undo() { if(history.length) { gridData = JSON.parse(history.pop()); draw(); } }
    function exportSmart() { const url = canvas.toDataURL(); const a = document.createElement('a'); a.download="haekle_design.png"; a.href=url; a.click(); }

    init();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)
