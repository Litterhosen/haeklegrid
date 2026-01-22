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
    body { margin: 0; font-family: sans-serif; background: #2c3e50; height: 100vh; overflow: hidden; }
    .toolbar { 
        position: fixed; top: 0; left: 0; right: 0;
        background: rgba(236, 240, 241, 0.95); 
        padding: 5px; display: flex; flex-wrap: wrap; gap: 4px; 
        justify-content: center; align-items: center; 
        border-bottom: 2px solid #bdc3c7; z-index: 1000;
    }
    .group { display: flex; gap: 3px; align-items: center; border: 1px solid #ddd; padding: 3px; border-radius: 6px; background: #fff; }
    button, select, input { padding: 6px; border-radius: 4px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; font-size: 10px; height: 32px; }
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }
    .viewport { width: 100vw; height: 100vh; overflow: auto; background: #34495e; touch-action: none; padding-top: 50px; }
    canvas { 
        background: white; transform-origin: 0 0; display: block; 
        image-rendering: pixelated; image-rendering: crisp-edges;
    }
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
    <div class="group">
        <button onclick="undo()">↩️</button>
        <button onclick="redo()">↪️</button>
    </div>
    <div class="group">
        <select id="mode" style="width: 75px;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ PAN</button>
    </div>
    <div class="group">
        <button class="btn-blue" onclick="exportSmart('png')">📸 PNG</button>
        <button onclick="resetCanvas()">🗑️ RYD</button>
    </div>
    <div style="font-size: 10px; font-weight: bold; margin-left: 10px;">Format: 114 x 23</div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 35;
    let gridData = [], history = [], redoStack = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    function initGrid() {
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        
        // GENSKABELSE AF START-MØNSTER (Eksempel baseret på din 23-bredde struktur)
        // Vi placerer prikker i midten for at starte mønsteret
        const mid = Math.floor(COLS / 2);
        for(let r = 0; r < 10; r++) {
            gridData[r][mid] = 'fill';
            if (r % 3 === 0) {
                gridData[r][mid-1] = 'fill';
                gridData[r][mid+1] = 'fill';
            }
        }
        
        draw();
    }

    function drawOnContext(tCtx, s, off, isExport = false) {
        const margin = isExport ? 50 : 0;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
        
        // Gitterlinjer
        for (let i = 0; i <= COLS; i++) {
            const x = i * s + off + margin;
            tCtx.beginPath();
            tCtx.moveTo(x, off + margin);
            tCtx.lineTo(x, (ROWS * s) + off + margin);
            styleLine(tCtx, i, isExport);
            tCtx.stroke();
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) drawLabel(tCtx, i+1, x + s/2, (off/2) + margin, off, (i+1)%10===0);
        }
        for (let j = 0; j <= ROWS; j++) {
            const y = j * s + off + margin;
            tCtx.beginPath();
            tCtx.moveTo(off + margin, y);
            tCtx.lineTo((COLS * s) + off + margin, y);
            styleLine(tCtx, j, isExport);
            tCtx.stroke();
            if (j < ROWS && (j+1 === 1 || (j+1) % 5 === 0)) drawLabel(tCtx, j+1, (off/2) + margin, y + s/2, off, (j+1)%10===0);
        }

        // Felter
        tCtx.textAlign = "center"; tCtx.textBaseline = "middle";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (!gridData[r][c]) continue;
                const x = c * s + off + margin, y = r * s + off + margin;
                if (gridData[r][c] === 'fill') {
                    tCtx.fillStyle = "black"; tCtx.fillRect(x+1, y+1, s-1, s-1);
                } else {
                    tCtx.fillStyle = "black"; tCtx.font = `bold ${s * 0.6}px Arial`;
                    tCtx.fillText(gridData[r][c], x + s/2, y + s/2);
                }
            }
        }
    }

    function styleLine(tCtx, idx, isExp) {
        if (idx % 10 === 0) { tCtx.strokeStyle = "#000"; tCtx.lineWidth = isExp ? 2 : 1.5; }
        else if (idx % 5 === 0) { tCtx.strokeStyle = "#666"; tCtx.lineWidth = isExp ? 1.5 : 1; }
        else { tCtx.strokeStyle = "#ccc"; tCtx.lineWidth = 0.5; }
    }

    function drawLabel(tCtx, txt, x, y, off, bold) {
        tCtx.font = bold ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
        tCtx.fillStyle = bold ? "#000" : "#777";
        tCtx.fillText(txt, x, y);
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    function exportSmart(type) {
        const dpr = 2, s = SIZE * dpr, off = OFFSET * dpr, margin = 50 * dpr;
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (margin * 2);
        out.height = (ROWS * s) + off + (margin * 2);
        drawOnContext(out.getContext('2d'), s, off, true);
        const url = out.toDataURL("image/png");
        const a = document.createElement('a'); a.download = "moenster_114x23.png"; a.href = url; a.click();
    }

    let isDown = false, evCache = [], prevDiff = -1;
    canvas.addEventListener('pointerdown', e => { if (isPan) isDown = true; else handleAction(e); if (e.pointerType === 'touch') evCache.push(e); });
    window.addEventListener('pointerup', e => { isDown = false; evCache = evCache.filter(ev => ev.pointerId !== e.pointerId); if (evCache.length < 2) prevDiff = -1; });
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }
        if (e.pointerType === 'touch' && evCache.length === 2) {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            if (index > -1) evCache[index] = e;
            const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
            if (prevDiff > 0) { scale = Math.min(Math.max(0.1, scale * (curDiff / prevDiff)), 8); canvas.style.transform = `scale(${scale})`; }
            prevDiff = curDiff;
        }
    });

    function handleAction(e) {
        if (evCache.length >= 2) return;
        const rect = canvas.getBoundingClientRect();
        const c = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const r = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            history.push(JSON.stringify(gridData));
            const mode = document.getElementById('mode').value;
            gridData[r][c] = (gridData[r][c] === mode) ? null : (mode === 'erase' ? null : mode);
            draw();
        }
    }

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function undo() { if (history.length) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); } }
    function redo() { if (redoStack.length) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); } }
    function resetCanvas() { if(confirm("Vil du rydde alt?")) initGrid(); }
    
    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
