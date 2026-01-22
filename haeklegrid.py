import streamlit as st
import streamlit.components.v1 as components

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
    .viewport { flex: 1; overflow: auto; background: #34495e; display: block; touch-action: none; }
    canvas { background: white; transform-origin: 0 0; display: block; }
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
        
        targetCtx.textAlign = "center";
        targetCtx.textBaseline = "middle";

        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * s + off;
                const y = r * s + off;
                
                // Tal i margenen - nu præcis justeret
                if (r === 0) {
                    const colNum = c + 1;
                    if (colNum === 1 || colNum % 5 === 0) {
                        targetCtx.font = (colNum % 10 === 0) ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
                        targetCtx.fillStyle = (colNum % 10 === 0) ? "#000" : "#777";
                        targetCtx.fillText(colNum, x + s/2, off/2);
                    }
                }
                if (c === 0) {
                    const rowNum = r + 1;
                    if (rowNum === 1 || rowNum % 5 === 0) {
                        targetCtx.font = (rowNum % 10 === 0) ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
                        targetCtx.fillStyle = (rowNum % 10 === 0) ? "#000" : "#777";
                        targetCtx.fillText(rowNum, off/2, y + s/2);
                    }
                }

                // Gitterlinjer
                targetCtx.beginPath();
                if ((r + 1) % 10 === 0 || (c + 1) % 10 === 0) {
                    targetCtx.strokeStyle = "#444"; // Hver 10. (Meget tydelig)
                    targetCtx.lineWidth = isExport ? 2 : 1.5;
                } else if ((r + 1) % 5 === 0 || (c + 1) % 5 === 0) {
                    targetCtx.strokeStyle = "#888"; // Hver 5.
                    targetCtx.lineWidth = 1;
                } else {
                    targetCtx.strokeStyle = "#ddd"; // Standard
                    targetCtx.lineWidth = 0.5;
                }
                targetCtx.strokeRect(x, y, s, s);
                
                const val = gridData[r][c];
                if (val === 'fill') {
                    targetCtx.fillStyle = "black";
                    targetCtx.fillRect(x, y, s, s);
                } else if (val) {
                    targetCtx.fillStyle = "black";
                    targetCtx.font = `bold ${s * 0.6}px Arial`;
                    targetCtx.fillText(val, x + s/2, y + s/2);
                }
            }
        }
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    function handleAction(e) {
        if (evCache.length >= 2) return;
        const rect = canvas.getBoundingClientRect();
        // Korrekt beregning af koordinater relativt til zoom og offset
        const x = (e.clientX - rect.left) / scale;
        const y = (e.clientY - rect.top) / scale;
        
        const gridC = Math.floor((x - OFFSET) / SIZE);
        const gridR = Math.floor((y - OFFSET) / SIZE);

        if (gridR >= 0 && gridR < ROWS && gridC >= 0 && gridC < COLS) {
            saveHistory();
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[gridR][gridC] = null;
            else if (mode === 'fill') gridData[gridR][gridC] = (gridData[gridR][gridC] === 'fill' ? null : 'fill');
            else gridData[gridR][gridC] = (gridData[gridR][gridC] === mode ? null : mode);
            draw();
        }
    }

    // Export og Zoom logik herunder (uændret men stabil)
    function exportSmart(type) {
        const exportScale = 2;
        const s = SIZE * exportScale;
        const off = OFFSET * exportScale;
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off;
        out.height = (ROWS * s) + off;
        drawOnContext(out.getContext('2d'), s, off, true);
        const url = out.toDataURL("image/png", 1.0);
        if(type === 'png') {
            const a = document.createElement('a'); a.download = "mønster.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<html><body style="margin:0;padding:20px;display:flex;justify-content:center;background:#fff;"><img src="${url}" style="max-width:100%;height:auto;object-fit:contain;"><script>setTimeout(()=>window.print(),500);<\\/script></body></html>`);
        }
    }

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
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; return; }
        if (e.pointerType === 'touch' && evCache.length === 2) {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            if (index > -1) evCache[index] = e;
            const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
            if (prevDiff > 0) {
                scale = Math.min(Math.max(0.1, scale * (curDiff / prevDiff)), 5);
                canvas.style.transform = `scale(${scale})`;
            }
            prevDiff = curDiff;
        }
    });

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }

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

    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }
    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
