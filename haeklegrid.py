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
        transition: transform 0.3s ease;
    }
    .toolbar.minimized { transform: translateY(-85%); }
    
    .toggle-ui {
        position: absolute; bottom: -20px; right: 10px;
        background: #bdc3c7; border: none; border-radius: 0 0 5px 5px;
        padding: 2px 10px; cursor: pointer; font-size: 12px;
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
        <input type="number" id="rows" value="60" style="width:35px">x<input type="number" id="cols" value="60" style="width:35px">
        <button onclick="initGrid()">OK</button>
    </div>
    <div class="group">
        <button onclick="undo()">↩️</button>
        <button onclick="redo()">↪️</button>
    </div>
    <div class="group">
        <select id="mode" style="width: 75px;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋</button>
    </div>
    <div class="group">
        <input type="file" id="imgInput" accept="image/*" style="width:70px; font-size:8px;">
        <button class="btn-blue" onclick="exportSmart('png')">📸</button>
        <button class="btn-green" onclick="exportSmart('pdf')">🖨️</button>
        <button onclick="resetCanvas()">🗑️</button>
    </div>
    <button class="toggle-ui" onclick="document.getElementById('toolbar').classList.toggle('minimized')">🔼/🔽</button>
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

    function initGrid() {
        COLS = parseInt(document.getElementById('cols').value);
        ROWS = parseInt(document.getElementById('rows').value);
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        ctx.imageSmoothingEnabled = false;
        draw();
    }

    function drawOnContext(tCtx, s, off, isExport = false) {
        const margin = isExport ? 50 : 0;
        const totalW = (COLS * s) + off;
        const totalH = (ROWS * s) + off;

        tCtx.imageSmoothingEnabled = false;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);

        // 1. Tegn fyldte felter (Sort, X, O)
        tCtx.textAlign = "center";
        tCtx.textBaseline = "middle";
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const val = gridData[r][c];
                if (!val) continue;
                const x = c * s + off + margin;
                const y = r * s + off + margin;
                if (val === 'fill') {
                    tCtx.fillStyle = "black";
                    tCtx.fillRect(x, y, s, s);
                } else {
                    tCtx.fillStyle = "black";
                    tCtx.font = `bold ${s * 0.6}px Arial`;
                    tCtx.fillText(val, x + s/2, y + s/2);
                }
            }
        }

        // 2. Tegn Gitterlinjer (Lodrette og Vandrette)
        for (let i = 0; i <= COLS; i++) {
            const x = i * s + off + margin;
            tCtx.beginPath();
            tCtx.moveTo(x, off + margin);
            tCtx.lineTo(x, totalH + margin);
            styleLine(tCtx, i, isExport);
            tCtx.stroke();
            
            // Tal for kolonner
            if (i < COLS) {
                const num = i + 1;
                if (num === 1 || num % 5 === 0) {
                    drawLabel(tCtx, num, x + s/2, (off/2) + margin, off, num % 10 === 0);
                }
            }
        }

        for (let j = 0; j <= ROWS; j++) {
            const y = j * s + off + margin;
            tCtx.beginPath();
            tCtx.moveTo(off + margin, y);
            tCtx.lineTo(totalW + margin, y);
            styleLine(tCtx, j, isExport);
            tCtx.stroke();

            // Tal for rækker
            if (j < ROWS) {
                const num = j + 1;
                if (num === 1 || num % 5 === 0) {
                    drawLabel(tCtx, num, (off/2) + margin, y + s/2, off, num % 10 === 0);
                }
            }
        }
    }

    function styleLine(tCtx, index, isExport) {
        if (index % 10 === 0) {
            tCtx.strokeStyle = "#000"; tCtx.lineWidth = isExport ? 2 : 1.5;
        } else if (index % 5 === 0) {
            tCtx.strokeStyle = "#666"; tCtx.lineWidth = isExport ? 1.5 : 1.0;
        } else {
            tCtx.strokeStyle = "#ccc"; tCtx.lineWidth = 0.5;
        }
    }

    function drawLabel(tCtx, text, x, y, off, isMajor) {
        tCtx.font = isMajor ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
        tCtx.fillStyle = isMajor ? "#000" : "#777";
        tCtx.fillText(text, x, y);
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, false); }

    function exportSmart(type) {
        const dpr = 2;
        const s = SIZE * dpr, off = OFFSET * dpr, margin = 50 * dpr;
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (margin * 2);
        out.height = (ROWS * s) + off + (margin * 2);
        drawOnContext(out.getContext('2d'), s, off, true);
        const url = out.toDataURL("image/png", 1.0);
        if(type === 'png') {
            const a = document.createElement('a'); a.download = "pixel-perfect-grid.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<html><body style="margin:0;padding:20px;display:flex;justify-content:center;background:#fff;"><img src="${url}" style="max-width:98%;height:auto;"><script>setTimeout(()=>window.print(),600);<\\/script></body></html>`);
        }
    }

    // Touch & Input Logic (Uændret men stabil)
    let isDown = false, evCache = [], prevDiff = -1;
    canvas.addEventListener('pointerdown', e => { if (isPan) { isDown = true; return; } if (e.pointerType === 'touch') evCache.push(e); handleAction(e); });
    window.addEventListener('pointerup', e => { isDown = false; evCache = evCache.filter(ev => ev.pointerId !== e.pointerId); if (evCache.length < 2) prevDiff = -1; });
    canvas.addEventListener('pointermove', e => {
        if (isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; return; }
        if (e.pointerType === 'touch' && evCache.length === 2) {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            if (index > -1) evCache[index] = e;
            const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
            if (prevDiff > 0) {
                scale = Math.min(Math.max(0.1, scale * (curDiff / prevDiff)), 8);
                canvas.style.transform = `scale(${scale})`;
            }
            prevDiff = curDiff;
        }
    });

    function handleAction(e) {
        if (evCache.length >= 2) return;
        const rect = canvas.getBoundingClientRect();
        const gridC = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const gridR = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (gridR >= 0 && gridR < ROWS && gridC >= 0 && gridC < COLS) {
            saveHistory();
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[gridR][gridC] = null;
            else if (mode === 'fill') gridData[gridR][gridC] = (gridData[gridR][gridC] === 'fill' ? null : 'fill');
            else gridData[gridR][gridC] = (gridData[gridR][gridC] === mode ? null : mode);
            draw();
        }
    }

    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
    function undo() { if (history.length > 0) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); } }
    function redo() { if (redoStack.length > 0) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); } }
    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }
    
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

    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
