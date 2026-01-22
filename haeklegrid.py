import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Ultimate Grid Designer Pro", layout="wide", initial_sidebar_state="collapsed")

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
    body { margin: 0; font-family: -apple-system, sans-serif; background: #2c3e50; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    .toolbar { 
        background: #ecf0f1; padding: 10px; display: flex; flex-wrap: wrap; gap: 10px; 
        justify-content: center; align-items: center; border-bottom: 3px solid #bdc3c7; z-index: 100;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .group { display: flex; gap: 8px; align-items: center; border-right: 2px solid #bdc3c7; padding: 0 10px; }
    .group:last-child { border: none; }
    button, select, input { padding: 8px 12px; border-radius: 6px; border: 1px solid #bdc3c7; font-weight: bold; cursor: pointer; font-size: 13px; }
    label { font-size: 11px; color: #34495e; font-weight: bold; text-transform: uppercase; }
    .btn-blue { background: #3498db; color: white; border: none; }
    .btn-green { background: #27ae60; color: white; border: none; }
    .btn-red { background: #e74c3c; color: white; border: none; }
    .active-tool { background: #f1c40f !important; color: black !important; }
    .viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 20px; background: #34495e; }
    canvas { background: white; box-shadow: 0 0 50px rgba(0,0,0,0.5); cursor: crosshair; }
</style>
</head>
<body>

<div class="toolbar">
    <div class="group">
        <label>Rækker:</label><input type="number" id="rows" value="60" style="width:60px">
        <label>Cols:</label><input type="number" id="cols" value="60" style="width:60px">
        <button onclick="initGrid()">Opdater</button>
    </div>
    <div class="group">
        <select id="mode">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ RYDDER</option>
        </select>
        <button id="panBtn" onclick="togglePan()">✋ PANORER</button>
    </div>
    <div class="group">
        <label>Import:</label><input type="file" id="imgInput" accept="image/*" style="width:140px">
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
    const OFFSET = 40; // Plads til tal
    let gridData = [];
    let isPan = false;
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const vp = document.getElementById('vp');

    function initGrid() {
        COLS = parseInt(document.getElementById('cols').value);
        ROWS = parseInt(document.getElementById('rows').value);
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }

    function draw() {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.font = "10px Arial";
        ctx.fillStyle = "#7f8c8d";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                const x = c * SIZE + OFFSET;
                const y = r * SIZE + OFFSET;
                
                // Tegn tal på rækker og kolonner for hver 5.
                if (r === 0 && (c + 1) % 5 === 0) ctx.fillText(c + 1, x + SIZE/2, OFFSET/2);
                if (c === 0 && (r + 1) % 5 === 0) ctx.fillText(r + 1, OFFSET/2, y + SIZE/2);

                // Gitterlinjer
                ctx.beginPath();
                ctx.strokeStyle = ((r+1)%5===0 || (c+1)%5===0) ? "#bdc3c7" : "#ecf0f1";
                ctx.lineWidth = ((r+1)%5===0 || (c+1)%5===0) ? 1.5 : 1;
                ctx.strokeRect(x, y, SIZE, SIZE);
                
                const val = gridData[r][c];
                if (val === 'fill') {
                    ctx.fillStyle = "black";
                    ctx.fillRect(x + 1, y + 1, SIZE - 2, SIZE - 2);
                } else if (val === 'X' || val === 'O') {
                    ctx.fillStyle = "black";
                    ctx.font = `bold ${SIZE * 0.6}px Arial`;
                    ctx.fillText(val, x + SIZE/2, y + SIZE/2);
                    ctx.font = "10px Arial"; // Reset font til tal
                }
                ctx.fillStyle = "#7f8c8d"; // Reset farve til tal
            }
        }
    }

    function getCoords(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {
            c: Math.floor((clientX - rect.left - OFFSET) / SIZE),
            r: Math.floor((clientY - rect.top - OFFSET) / SIZE)
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        if (isPan) return;
        const {r, c} = getCoords(e);
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

    document.getElementById('imgInput').onchange = function(e) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = COLS; tempCanvas.height = ROWS;
                const tCtx = tempCanvas.getContext('2d');
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

    function exportData(type) {
        const url = canvas.toDataURL("image/png");
        if(type === 'png') {
            const a = document.createElement('a');
            a.download = "moenster.png"; a.href = url; a.click();
        } else {
            const w = window.open();
            w.document.write(`<html><body style="margin:0; display:flex; justify-content:center;"><img src="${url}" style="max-width:95%; height:auto;" onload="window.print();"></body></html>`);
        }
    }

    function resetCanvas() { if(confirm("Ryd alt?")) initGrid(); }
    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
