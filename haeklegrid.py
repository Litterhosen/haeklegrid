import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro - Mobil & Safe-Resize", layout="wide", initial_sidebar_state="collapsed")

# Skjul Streamlit standard elementer for at maksimere pladsen på mobilen
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
<style>
    :root {
        --bg-dark: #2c3e50;
        --toolbar-bg: #ffffff;
        --accent: #3498db;
        --accent-green: #27ae60;
    }

    body { margin: 0; font-family: sans-serif; background: var(--bg-dark); height: 100vh; overflow: hidden; }

    /* FAST TOP-MENU (Mobil-optimeret) */
    .toolbar { 
        position: fixed; top: 0; left: 0; right: 0;
        background: var(--toolbar-bg); 
        padding: 8px; display: flex; flex-direction: column; gap: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4); z-index: 1000;
    }

    .row { display: flex; justify-content: center; align-items: center; gap: 6px; width: 100%; }
    .group { display: flex; align-items: center; gap: 4px; background: #f0f2f6; padding: 4px 8px; border-radius: 10px; border: 1px solid #ddd; }

    button, select, input { 
        height: 42px; border-radius: 8px; border: 1px solid #ccc;
        font-size: 13px; font-weight: bold; cursor: pointer;
        background: white;
    }

    .btn-main { background: var(--accent); color: white; border: none; padding: 0 12px; }
    .btn-icon { width: 42px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .btn-red { background: #e74c3c; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; border-color: #f39c12 !important; }

    /* VIEWPORT TIL GRID */
    .viewport { 
        width: 100vw; height: 100vh; overflow: auto; 
        padding-top: 115px; /* Plads til den dobbelte toolbar */
        background: #34495e; -webkit-overflow-scrolling: touch;
    }
    
    canvas { 
        background: white; transform-origin: 0 0; 
        display: block; box-shadow: 0 0 30px rgba(0,0,0,0.5);
        image-rendering: pixelated;
    }

    .size-input { width: 45px; text-align: center; font-size: 16px; } /* Større font til mobil-input */
    #imgInput { display: none; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="row">
        <div class="group">
            <input type="number" id="rows" value="114" class="size-input"> x 
            <input type="number" id="cols" value="23" class="size-input">
            <button class="btn-main" onclick="resizeGrid()">JUSTÉR MÅL</button>
        </div>
        <button class="btn-icon" onclick="undo()" title="Undo">↩️</button>
        <button class="btn-icon" onclick="redo()" title="Redo">↪️</button>
    </div>

    <div class="row">
        <select id="mode" style="flex-grow: 1; max-width: 130px;">
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
        <button class="btn-icon" onclick="document.getElementById('imgInput').click()">🖼️</button>
        <input type="file" id="imgInput" accept="image/*">
        <button class="btn-icon btn-main" onclick="exportSmart('png')">📸</button>
        <button class="btn-icon btn-red" onclick="resetCanvas()">🗑️</button>
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

    function init() {
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        updateCanvas();
    }

    // SIKKER JUSTERING: Bevarer designet når rækker/kolonner ændres
    function resizeGrid() {
        const newRows = parseInt(document.getElementById('rows').value);
        const newCols = parseInt(document.getElementById('cols').value);
        
        saveHistory(); // Gem nuværende tilstand så man kan fortryde justeringen
        
        let oldData = JSON.parse(JSON.stringify(gridData));
        gridData = Array(newRows).fill().map(() => Array(newCols).fill(null));
        
        // Kopier gammelt indhold til det nye grid
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

    function drawOnContext(tCtx, s, off, isExport = false) {
        const margin = isExport ? 50 : 0;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
        
        // 1. Gitterlinjer (Optimerede stregtykkelser)
        for (let i = 0; i <= COLS; i++) {
            const x = i * s + off + margin;
            tCtx.beginPath();
            tCtx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
            tCtx.lineWidth = (i % 5 === 0) ? 1.5 : 0.5;
            tCtx.moveTo(x, off + margin); tCtx.lineTo(x, (ROWS * s) + off + margin);
            tCtx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {
                tCtx.font = (i+1)%10===0 ? "bold 12px Arial" : "11px Arial";
                tCtx.fillStyle = "#444"; tCtx.textAlign = "center";
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
                tCtx.font = (j+1)%10===0 ? "bold 12px Arial" : "11px Arial";
                tCtx.fillStyle = "#444"; tCtx.textAlign = "right";
                tCtx.fillText(j+1, off + margin - 8, y + s/1.5);
            }
        }

        // 2. Indhold (Sort, X, O)
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
        if (history.length > 40) history.shift();
        redoStack = [];
    }

    // Touch & Pointer Logic
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
        }
    });

    let isDown = false;
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
    });
    window.addEventListener('pointerup', () => isDown = false);

    // FUNKTIONER
    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function zoomGrid(v) { scale = Math.max(0.2, scale + v); canvas.style.transform = `scale(${scale})`; }
    function undo() { if(history.length) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); } }
    function redo() { if(redoStack.length) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); } }
    
    function exportSmart(type) {
        const dpr = 2;
        const s = SIZE * dpr, off = OFFSET * dpr, margin = 50 * dpr;
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (margin * 2);
        out.height = (ROWS * s) + off + (margin * 2);
        drawOnContext(out.getContext('2d'), s, off, true);
        const url = out.toDataURL("image/png");
        const a = document.createElement('a'); a.download = "haekle-design.png"; a.href = url; a.click();
    }

    // Billed import (Foto)
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
                    gridData[Math.floor((i/4)/COLS)][(i/4)%COLS] = avg < 128 ? 'fill' : null;
                }
                draw();
            }
            img.src = event.target.result;
        }
        reader.readAsDataURL(e.target.files[0]);
    };

    function resetCanvas() { if(confirm("Ryd alt?")) init(); }
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
