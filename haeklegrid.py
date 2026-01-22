import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    body { overflow: hidden; background: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; font-family: sans-serif; background: #2c3e50; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    .toolbar { 
        background: #ecf0f1; padding: 5px; display: flex; flex-wrap: wrap; gap: 5px; 
        justify-content: center; align-items: center; border-bottom: 2px solid #bdc3c7; z-index: 100;
    }
    .group { display: flex; gap: 4px; align-items: center; border: 1px solid #ddd; padding: 4px; border-radius: 6px; background: #fff; }
    button, select, input { padding: 8px; border-radius: 4px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; font-size: 11px; height: 36px; }
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }
    .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; background: #34495e; touch-action: none; }
    canvas { background: white; box-shadow: 0 0 30px rgba(0,0,0,0.5); transform-origin: 0 0; image-rendering: -moz-crisp-edges; image-rendering: pixelated; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="group">
        <input type="number" id="rows" value="60" style="width:40px">x<input type="number" id="cols" value="60" style="width:40px">
        <button onclick="initGrid()">OK</button>
    </div>
    <div class="group">
        <button onclick="undo()">↩️</button>
        <button onclick="redo()">↪️</button>
    </div>
    <div class="group">
        <select id="mode">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ PAN</button>
    </div>
    <div class="group">
        <input type="file" id="imgInput" accept="image/*" style="width:90px; font-size:9px;">
        <button class="btn-blue" onclick="exportSmart('png')">📸 PNG</button>
        <button class="btn-green" onclick="exportSmart('pdf')">🖨️ PDF</button>
        <button onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS, ROWS, SIZE = 25, OFFSET = 35;
    let gridData = [], history = [], redoStack = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    function saveHistory() {
        history.push(JSON.stringify(gridData));
        if (history.length > 30) history.shift();
        redoStack = [];
    }
    function undo() { if (history.length > 0) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); } }
    function redo() { if (redoStack.length > 0) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); } }

    function initGrid() {
        COLS = parseInt(document.getElementById('cols').value);
        ROWS = parseInt(document.getElementById('rows').value);
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }

    function drawOnContext(targetCtx, s, off, isExport = false) {
        const w = (COLS * s) + off;
        const h = (ROWS * s) + off;
        
        targetCtx.fillStyle = "white";
        targetCtx.fillRect(0, 0, w, h);
        
        targetCtx.font = `${off * 0.4}px Arial`;
        targetCtx.fillStyle = "#888";
        targetCtx.textAlign = "center";
        targetCtx.textBaseline = "middle";

        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * s + off;
                const y = r * s + off;
                
                // Tal (1,1 i øverste venstre hjørne)
                if (r === 0 && (c + 1) % 5 === 0) targetCtx.fillText(c + 1, x + s/2, off/2);
                if (c === 0 && (r + 1) % 5 === 0) targetCtx.fillText(r + 1, off/2, y + s/2);
                
                targetCtx.beginPath();
                targetCtx.strokeStyle = ((r+1)%5===0 || (c+1)%5===0) ? "#999" : "#ddd";
                targetCtx.lineWidth = isExport ? 1.5 : 1;
                targetCtx.strokeRect(x, y, s, s);
                
                const val = gridData[r][c];
                if (val === 'fill') {
                    targetCtx.fillStyle = "black";
                    targetCtx.fillRect(x, y, s, s);
                } else if (val) {
                    targetCtx.fillStyle = "black";
                    targetCtx.font = `bold ${s * 0.6}px Arial`;
                    targetCtx.fillText(val, x + s/2, y + s/2);
                    targetCtx.font = `${off * 0.4}px Arial`;
                }
            }
        }
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    // Eksport funktion med høj opløsning og korrekte proportioner
    function exportSmart(type) {
        const exportScale = 2; // Gør billedet dobbelt så skarpt
        const s = SIZE * exportScale;
        const off = OFFSET * exportScale;
        
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (20 * exportScale); // ekstra margen
        out.height = (ROWS * s) + off + (20 * exportScale);
        const oCtx = out.getContext('2d');
        
        drawOnContext(oCtx, s, off, true);
        
        const url = out.toDataURL("image/png", 1.0);
        
        if(type === 'png') {
            const a = document.createElement('a');
            a.download = "grid-design-sharp.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            // PDF fix: ingen stræk, centreret billede
            w.document.write(`
                <html>
                <body style="margin:0; padding:40px; background:#fff; display:flex; justify-content:center;">
                    <img src="${url}" style="max-width:100%; height:auto; object-fit:contain; box-shadow: 0 0 10px #ccc;">
                    <script>setTimeout(() => { window.print(); }, 500);<\\/script>
                </body>
                </html>
            `);
        }
    }

    // Touch/Pointer logik
    let isDown = false, evCache = [], prevDiff = -1;
    canvas.addEventListener('pointerdown', e => {
        if (isPan) { isDown = true; return; }
        if (e.pointerType === 'touch') evCache.push(e);
        handleAction(e);
    });
    window.addEventListener('pointerup', e => {
        isDown = false;
        evCache = evCache.filter(ev => ev.pointerId !== e.pointerId);
        if (evCache.length < 2) prevDiff = -1;
    });
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) {
            vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; return;
        }
        if (e.pointerType === 'touch' && evCache.length === 2) {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            if (index > -1) evCache[index] = e;
            const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
            if (prevDiff > 0) {
                scale = Math.min(Math.max(0.2, scale * (curDiff / prevDiff)), 5);
                canvas.style.transform = `scale(${scale})`;
            }
            prevDiff = curDiff;
        }
    });

    function handleAction(e) {
        if (evCache.length >= 2) return;
        const rect = canvas.getBoundingClientRect();
        const gridC = Math.floor(( (e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const gridR = Math.floor(( (e.clientY - rect.top) / scale - OFFSET) / SIZE);

        if (gridR >= 0 && gridR < ROWS && gridC >= 0 && gridC < COLS) {
            saveHistory();
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[gridR][gridC] = null;
            else if (mode === 'fill') gridData[gridR][gridC] = (gridData[gridR][gridC] === 'fill' ? null : 'fill');
            else gridData[gridR][gridC] = (gridData[gridR][gridC] === mode ? null : mode);
            draw();
        }
    }

    function togglePan() {
        isPan = !isPan;
        document.getElementById('panBtn').classList.toggle('active-tool');
    }

    document.getElementById('imgInput').onchange = function(e) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                saveHistory();
                const tCanvas = document.createElement('canvas');
                tCanvas.width = COLS; tCanvas.height = ROWS;
                const tCtx = tCanvas.getContext('2d');
                tCtx.drawImage(img, 0, 0, COLS, ROWS);
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

    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }
    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
