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
    .toolbar { background: #ecf0f1; padding: 5px; display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; border-bottom: 2px solid #bdc3c7; z-index: 100; }
    .group { display: flex; gap: 4px; align-items: center; border: 1px solid #ddd; padding: 4px; border-radius: 6px; background: #fff; }
    button, select, input { padding: 8px; border-radius: 4px; border: 1px solid #ccc; font-weight: bold; cursor: pointer; font-size: 11px; height: 36px; }
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .viewport { flex: 1; overflow: auto; background: #34495e; touch-action: none; position: relative; }
    canvas { 
        background: white; transform-origin: 0 0; 
        image-rendering: pixelated; 
        image-rendering: crisp-edges;
    }
</style>
</head>
<body>

<div class="toolbar">
    <div class="group">
        <input type="number" id="rows" value="60" style="width:40px">x<input type="number" id="cols" value="60" style="width:40px">
        <button onclick="initGrid()">OK</button>
    </div>
    <div class="group"><button onclick="undo()">↩️</button><button onclick="redo()">↪️</button></div>
    <div class="group">
        <select id="mode"><option value="fill">⚫ SORT</option><option value="X">❌ X</option><option value="O">⭕ O</option><option value="erase">⚪ SLET</option></select>
        <button id="panBtn" onclick="togglePan()">✋ PAN</button>
    </div>
    <div class="group">
        <input type="file" id="imgInput" accept="image/*" style="width:80px; font-size:8px;">
        <button class="btn-blue" onclick="exportFinal('png')">📸 PNG</button>
        <button class="btn-green" onclick="exportFinal('pdf')">🖨️ PDF</button>
        <button onclick="resetCanvas()">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp"><canvas id="c"></canvas></div>

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

    function initGrid() {
        COLS = parseInt(document.getElementById('cols').value);
        ROWS = parseInt(document.getElementById('rows').value);
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }

    function drawOnContext(tCtx, s, off, margin = 0) {
        // Tving pixel-skarphed
        tCtx.imageSmoothingEnabled = false;
        tCtx.webkitImageSmoothingEnabled = false;
        tCtx.mozImageSmoothingEnabled = false;

        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
        
        tCtx.textAlign = "center";
        tCtx.textBaseline = "middle";

        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * s + off + margin;
                const y = r * s + off + margin;

                // Tal-margen (1, 5, 10...)
                if (r === 0) {
                    const colNum = c + 1;
                    if (colNum === 1 || colNum % 5 === 0) {
                        tCtx.font = (colNum % 10 === 0) ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
                        tCtx.fillStyle = (colNum % 10 === 0) ? "#000" : "#888";
                        tCtx.fillText(colNum, x + s/2, (off/2) + margin);
                    }
                }
                if (c === 0) {
                    const rowNum = r + 1;
                    if (rowNum === 1 || rowNum % 5 === 0) {
                        tCtx.font = (rowNum % 10 === 0) ? `bold ${off*0.35}px Arial` : `${off*0.3}px Arial`;
                        tCtx.fillStyle = (rowNum % 10 === 0) ? "#000" : "#888";
                        tCtx.fillText(rowNum, (off/2) + margin, y + s/2);
                    }
                }

                // Gitter-linjer (Hierarki: 1, 5, 10)
                tCtx.beginPath();
                if ((r + 1) % 10 === 0 || (c + 1) % 10 === 0) {
                    tCtx.strokeStyle = "#444"; tCtx.lineWidth = 1.5;
                } else if ((r + 1) % 5 === 0 || (c + 1) % 5 === 0) {
                    tCtx.strokeStyle = "#999"; tCtx.lineWidth = 1;
                } else {
                    tCtx.strokeStyle = "#ddd"; tCtx.lineWidth = 0.5;
                }
                tCtx.strokeRect(x, y, s, s);
                
                const val = gridData[r][c];
                if (val === 'fill') {
                    tCtx.fillStyle = "black";
                    tCtx.fillRect(x, y, s, s);
                } else if (val) {
                    tCtx.fillStyle = "black";
                    tCtx.font = `bold ${s * 0.6}px Arial`;
                    tCtx.fillText(val, x + s/2, y + s/2);
                }
            }
        }
    }

    function draw() { drawOnContext(ctx, SIZE, OFFSET, 0); }

    function exportFinal(type) {
        const dpr = 2; // Høj opløsning
        const s = SIZE * dpr;
        const off = OFFSET * dpr;
        const margin = 60; // Stor sikkerhedsmargen så intet skæres af fotos

        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (margin * 2);
        out.height = (ROWS * s) + off + (margin * 2);
        const oCtx = out.getContext('2d');
        
        drawOnContext(oCtx, s, off, margin);
        
        const url = out.toDataURL("image/png", 1.0);
        if(type === 'png') {
            const a = document.createElement('a'); a.download = "design.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<html><body style="margin:0;padding:20px;display:flex;justify-content:center;background:#eee;">
                <img src="${url}" style="max-width:95%; height:auto; background:white; box-shadow:0 0 20px #999;">
                <script>setTimeout(()=>window.print(),800);<\\/script></body></html>`);
        }
    }

    // Touch & Zoom (Optimerede Pointer Events)
    let evCache = [], prevDiff = -1, isDown = false;
    canvas.addEventListener('pointerdown', e => { if(isPan) isDown=true; else handleAction(e); if(e.pointerType==='touch') evCache.push(e); });
    window.addEventListener('pointerup', e => { isDown=false; evCache = evCache.filter(ev => ev.pointerId !== e.pointerId); if(evCache.length < 2) prevDiff = -1; });
    
    canvas.addEventListener('pointermove', e => {
        if(isPan && isDown) { vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; return; }
        if (e.pointerType === 'touch' && evCache.length === 2) {
            const index = evCache.findIndex(ev => ev.pointerId === e.pointerId);
            if (index > -1) evCache[index] = e;
            const curDiff = Math.hypot(evCache[0].clientX - evCache[1].clientX, evCache[0].clientY - evCache[1].clientY);
            if (prevDiff > 0) {
                scale = Math.min(Math.max(0.1, scale * (curDiff / prevDiff)), 6);
                canvas.style.transform = `scale(${scale})`;
            }
            prevDiff = curDiff;
        }
    });

    function handleAction(e) {
        if(evCache.length >= 2) return;
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) / scale;
        const y = (e.clientY - rect.top) / scale;
        const c = Math.floor((x - OFFSET) / SIZE);
        const r = Math.floor((y - OFFSET) / SIZE);
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            saveHistory();
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[r][c] = null;
            else if (mode === 'fill') gridData[r][c] = (gridData[r][c] === 'fill' ? null : 'fill');
            else gridData[r][c] = (gridData[r][c] === mode ? null : mode);
            draw();
        }
    }

    function undo() { if (history.length > 0) { redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); } }
    function redo() { if (redoStack.length > 0) { history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); } }
    function togglePan() { isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }
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
