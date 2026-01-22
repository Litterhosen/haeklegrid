import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hækle Grid Pro - Mobil", layout="wide", initial_sidebar_state="collapsed")

# Rydder Streamlit standard layout for at give plads
st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    body { background: #1a252f; }
    </style>
    """, unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {
        --bg: #2c3e50;
        --toolbar-bg: #ffffff;
        --accent: #3498db;
    }

    body { margin: 0; font-family: sans-serif; background: var(--bg); height: 100vh; overflow: hidden; }

    /* TOP TOOLBAR - Optimeret så den ikke bliver væk */
    .toolbar { 
        position: fixed; top: 0; left: 0; right: 0;
        background: var(--toolbar-bg); 
        padding: 8px; display: flex; flex-direction: column; gap: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 1000;
    }

    .row { display: flex; justify-content: center; gap: 5px; width: 100%; }
    
    .group { display: flex; align-items: center; gap: 4px; background: #f1f1f1; padding: 4px 8px; border-radius: 8px; }

    button, select, input { 
        height: 40px; border-radius: 6px; border: 1px solid #ccc;
        font-size: 13px; font-weight: bold; cursor: pointer;
    }

    .btn-main { background: var(--accent); color: white; border: none; padding: 0 10px; }
    .btn-icon { width: 40px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .active-tool { background: #f1c40f !important; color: black !important; }

    /* VIEWPORT */
    .viewport { 
        width: 100vw; height: 100vh; overflow: auto; 
        padding-top: 110px; /* Plads til den dobbelte toolbar */
        background: #34495e; -webkit-overflow-scrolling: touch;
    }
    
    canvas { 
        background: white; transform-origin: 0 0; 
        display: block; box-shadow: 0 0 20px rgba(0,0,0,0.5);
        image-rendering: pixelated;
    }

    .size-input { width: 40px; text-align: center; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="row">
        <div class="group">
            <input type="number" id="rows" value="114" class="size-input"> x 
            <input type="number" id="cols" value="23" class="size-input">
            <button class="btn-main" onclick="resizeGrid()">OK / JUSTÉR</button>
        </div>
        <button class="btn-icon" onclick="undo()" title="Undo">↩️</button>
        <button class="btn-icon btn-main" onclick="exportSmart()" title="Gem">📸</button>
    </div>

    <div class="row">
        <select id="mode" style="flex-grow: 1; max-width: 150px;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" class="btn-icon" onclick="togglePan()">✋</button>
        <div class="group">
            <button class="btn-icon" onclick="zoomGrid(0.2)">➕</button>
            <button class="btn-icon" onclick="zoomGrid(-0.2)">➖</button>
        </div>
        <button class="btn-icon" style="background:#e74c3c; color:white; border:none;" onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 40;
    let gridData = [], history = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    function init() {
        // Lav start grid
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        updateCanvas();
    }

    // SIKKER JUSTERING: Ændrer størrelse uden at slette tegning
    function resizeGrid() {
        const newRows = parseInt(document.getElementById('rows').value);
        const newCols = parseInt(document.getElementById('cols').value);
        
        // Gem gammel data
        let oldData = JSON.parse(JSON.stringify(gridData));
        
        // Lav nyt grid med nye mål
        gridData = Array(newRows).fill().map(() => Array(newCols).fill(null));
        
        // Flyt gammel tegning over i det nye grid
        for (let r = 0; r < Math.min(ROWS, newRows); r++) {
            for (let c = 0; c < Math.min(COLS, newCols); c++) {
                gridData[r][c] = oldData[r][c];
            }
        }
        
        ROWS = newRows;
        COLS = newCols;
        updateCanvas();
    }

    function updateCanvas() {
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        draw();
    }

    function draw() {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Gitterlinjer
        for (let i = 0; i <= COLS; i++) {
            const x = i * SIZE + OFFSET;
            ctx.beginPath();
            ctx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
            ctx.lineWidth = (i % 5 === 0) ? 1.5 : 0.5;
            ctx.moveTo(x, OFFSET); ctx.lineTo(x, ROWS * SIZE + OFFSET);
            ctx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {
                ctx.font = "10px Arial"; ctx.fillStyle = "#666";
                ctx.fillText(i+1, x + 5, OFFSET - 10);
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
                ctx.fillText(j+1, 5, y + 18);
            }
        }

        // Tegn indhold (Sort, X, O)
        ctx.textAlign = "center";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (!gridData[r][c]) continue;
                const x = c * SIZE + OFFSET, y = r * SIZE + OFFSET;
                if (gridData[r][c] === 'fill') {
                    ctx.fillStyle = "black"; ctx.fillRect(x+1, y+1, SIZE-2, SIZE-2);
                } else {
                    ctx.fillStyle = "black"; ctx.font = "bold 15px Arial";
                    ctx.fillText(gridData[r][c], x + SIZE/2, y + SIZE/1.4);
                }
            }
        }
    }

    // Mobil-venlig input
    canvas.addEventListener('pointerdown', e => {
        if (isPan) { isDown = true; return; }
        const rect = canvas.getBoundingClientRect();
        const c = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const r = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            history.push(JSON.stringify(gridData));
            if (history.length > 20) history.shift();
            const m = document.getElementById('mode').value;
            gridData[r][c] = (gridData[r][c] === m ? null : (m === 'erase' ? null : m));
            draw();
        }
    });

    let isDown = false;
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
    });
    window.addEventListener('pointerup', () => isDown = false);

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function zoomGrid(v) { scale = Math.max(0.2, scale + v); canvas.style.transform = `scale(${scale})`; }
    function undo() { if(history.length) { gridData = JSON.parse(history.pop()); draw(); } }
    function exportSmart() { const url = canvas.toDataURL(); const a = document.createElement('a'); a.download="design.png"; a.href=url; a.click(); }
    function resetCanvas() { if(confirm("Ryd alt?")) init(); }

    init();
</script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=False)
