import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Ultimate Grid Designer", layout="wide", initial_sidebar_state="collapsed")

# Fjern alt Streamlit UI for at give plads til appen
st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    body { overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# HTML koden indeholder nu både indstillinger og tegnebræt
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; font-family: -apple-system, sans-serif; background: #2c3e50; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    
    /* TOP MENU */
    .toolbar { 
        background: #ecf0f1; padding: 10px; display: flex; flex-wrap: wrap; gap: 10px; 
        justify-content: center; align-items: center; border-bottom: 3px solid #bdc3c7; z-index: 100;
    }
    
    .group { display: flex; gap: 5px; align-items: center; border-right: 2px solid #bdc3c7; padding-right: 10px; }
    .group:last-child { border: none; }

    button, select, input { padding: 8px 12px; border-radius: 6px; border: 1px solid #bdc3c7; font-weight: bold; cursor: pointer; }
    label { font-size: 12px; color: #34495e; font-weight: bold; }
    
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .btn-red { background: #e74c3c; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }

    /* CANVAS AREA */
    .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 40px; -webkit-overflow-scrolling: touch; }
    canvas { background: white; box-shadow: 0 0 30px rgba(0,0,0,0.5); cursor: crosshair; image-rendering: pixelated; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="group">
        <label>Rækker:</label><input type="number" id="rows" value="120" style="width:50px">
        <label>Cols:</label><input type="number" id="cols" value="120" style="width:50px">
        <button onclick="initGrid()">Opdater Grid</button>
    </div>

    <div class="group">
        <select id="mode">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ PANORER</button>
    </div>

    <div class="group">
        <label>Billede:</label><input type="file" id="imgInput" accept="image/*" style="width:120px">
        <button class="btn-blue" onclick="exportData('png')">📸 PNG</button>
        <button class="btn-green" onclick="exportData('pdf')">🖨️ PDF</button>
        <button class="btn-red" onclick="resetCanvas()">🗑️ RYD</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS, ROWS, SIZE = 25;
    let gridData = [];
    let isPan = false;
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const vp = document.getElementById('vp');

    function initGrid() {
        COLS = parseInt(document.getElementById('cols').value);
        ROWS = parseInt(document.getElementById('rows').value);
        canvas.width = COLS * SIZE;
        canvas.height = ROWS * SIZE;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }

    function draw() {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * SIZE;
                const y = r * SIZE;
                
                // MEGET TYDELIGE GRIDS
                ctx.strokeStyle = "#e0e0e0";
                ctx.lineWidth = 1;
                ctx.strokeRect(x, y, SIZE, SIZE);
                
                const val = gridData[r][c];
                if (val === 'fill') {
                    ctx.fillStyle = "black";
                    ctx.fillRect(x, y, SIZE, SIZE);
                } else if (val === 'X' || val === 'O') {
                    ctx.fillStyle = "black";
                    ctx.font = `bold ${SIZE * 0.7}px Arial`;
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(val, x + SIZE/2, y + SIZE/2);
                }
            }
        }
    }

    canvas.addEventListener('mousedown', (e) => {
        if (isPan) return;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const c = Math.floor(x / SIZE);
        const r = Math.floor(y / SIZE);
        
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[r][c] = null;
            else if (mode === 'fill') gridData[r][c] = (gridData[r][c] === 'fill' ? null : 'fill');
            else gridData[r][c] = (gridData[r][c] === mode ? null : mode);
            draw();
        }
    });

    function togglePan() {
        isPan = !isPan;
        document.getElementById('panBtn').classList.toggle('active-tool');
        vp.style.touchAction = isPan ? "auto" : "none";
        canvas.style.cursor = isPan ? "grab" : "crosshair";
    }

    // BILLEDE IMPORT LOGIK
    document.getElementById('imgInput').onchange = function(e) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = COLS;
                tempCanvas.height = ROWS;
                const tCtx = tempCanvas.getContext('2d');
                tCtx.drawImage(img, 0, 0, COLS, ROWS);
                const pix = tCtx.getImageData(0, 0, COLS, ROWS).data;
                
                for(let i=0; i<pix.length; i+=4) {
                    const avg = (pix[i]+pix[i+1]+pix[i+2])/3;
                    const r = Math.floor((i/4)/COLS);
                    const c = (i/4)%COLS;
                    gridData[r][c] = avg < 128 ? 'fill' : null;
                }
                draw();
            }
            img.src = event.target.result;
        }
        reader.readAsDataURL(e.target.files[0]);
    };

    function exportData(type) {
        const MARGIN = 100;
        const out = document.createElement('canvas');
        out.width = canvas.width + MARGIN*2;
        out.height = canvas.height + MARGIN*2;
        const oCtx = out.getContext('2d');
        oCtx.fillStyle = "white";
        oCtx.fillRect(0,0,out.width,out.height);
        oCtx.drawImage(canvas, MARGIN, MARGIN);
        
        const url = out.toDataURL("image/png");
        if(type === 'png') {
            const a = document.createElement('a');
            a.download = "moenster.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<img src="${url}" style="width:100%" onload="window.print();window.close();">`);
        }
    }

    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }

    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=2000, scrolling=False)
