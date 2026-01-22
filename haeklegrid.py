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
    button, select, input { padding: 8px; border-radius: 4px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; font-size: 12px; height: 36px; }
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .btn-red { background: #e74c3c; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }
    .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; background: #34495e; touch-action: none; }
    canvas { background: white; box-shadow: 0 0 30px rgba(0,0,0,0.5); transform-origin: 0 0; image-rendering: pixelated; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="group">
        <input type="number" id="rows" value="60" style="width:45px"> x <input type="number" id="cols" value="60" style="width:45px">
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
        <button class="btn-blue" onclick="exportData('png')">📸</button>
        <button class="btn-green" onclick="exportData('pdf')">🖨️</button>
        <button onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS, ROWS, SIZE = 25, OFFSET = 40;
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

    function draw() {
        ctx.setTransform(1,0,0,1,0,0);
        ctx.fillStyle = "white";
        ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.font = "10px Arial"; ctx.fillStyle = "#7f8c8d"; ctx.textAlign = "center"; ctx.textBaseline = "middle";

        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * SIZE + OFFSET, y = r * SIZE + OFFSET;
                if (r === 0 && (c + 1) % 5 === 0) ctx.fillText(c + 1, x + SIZE/2, OFFSET/2);
                if (c === 0 && (r + 1) % 5 === 0) ctx.fillText(r + 1, OFFSET/2, y + SIZE/2);
                ctx.strokeStyle = ((r+1)%5===0 || (c+1)%5===0) ? "#bdc3c7" : "#ecf0f1";
                ctx.lineWidth = ((r+1)%5===0 || (c+1)%5===0) ? 1.5 : 1;
                ctx.strokeRect(x, y, SIZE, SIZE);
                const val = gridData[r][c];
                if (val === 'fill') { ctx.fillStyle = "black"; ctx.fillRect(x+1, y+1, SIZE-2, SIZE-2); }
                else if (val) { ctx.fillStyle = "black"; ctx.font = `bold ${SIZE*0.6}px Arial`; ctx.fillText(val, x+SIZE/2, y+SIZE/2); ctx.font = "10px Arial"; }
            }
        }
    }

    // --- NY FORBEDRET TOUCH/MUS LOGIK ---
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
            vp.scrollLeft -= e.movementX;
            vp.scrollTop -= e.movementY;
            return;
        }
        
        // Pinch Zoom håndtering
        if (e.pointerType === 'touch') {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            evCache[index] = e;
            if (evCache.length === 2) {
                const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
                if (prevDiff > 0) {
                    let zoom = curDiff / prevDiff;
                    scale = Math.min(Math.max(0.3, scale * zoom), 4);
                    canvas.style.transform = `scale(${scale})`;
                }
                prevDiff = curDiff;
            }
        }
    });

    function handleAction(e) {
        if (evCache.length >= 2) return; // Ingen tegning ved zoom
        const rect = canvas.getBoundingClientRect();
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

    function togglePan() {
        isPan = !isPan;
        document.getElementById('panBtn').classList.toggle('active-tool');
    }

    function exportData(type) {
        const url = canvas.toDataURL("image/png");
        if(type === 'png') {
            const a = document.createElement('a');
            a.download = "design.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<html><body style="margin:0;display:flex;justify-content:center;"><img src="${url}" style="max-width:95%;height:auto;" onload="window.print();"></body></html>`);
        }
    }

    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }
    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
