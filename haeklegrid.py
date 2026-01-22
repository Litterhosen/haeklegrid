import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SIDEBAR (KONFIGURATION) ---
st.set_page_config(page_title="Grid Designer Pro v4", layout="wide", initial_sidebar_state="expanded")

# Skjul Streamlit standard elementer
st.markdown("""
    <style>
    header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
    .main .block-container {padding: 0px !important;}
    section[data-testid="stSidebar"] { background-color: #1a252f; color: white; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🧶 Indstillinger")
    st.subheader("1. Dimensioner")
    rows = st.number_input("Højde (Rækker)", 1, 300, 114)
    cols = st.number_input("Bredde (Masker)", 1, 100, 23)
    
    st.divider()
    
    st.subheader("2. Visning")
    zoom = st.slider("Zoom niveau", 10, 60, 25)
    
    st.info("Brug knapperne i toppen til at tegne og eksportere dit mønster.")

# --- HTML / JS KOMPONENT ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root {{
        --bg-dark: #2c3e50;
        --toolbar-bg: rgba(255, 255, 255, 0.95);
        --accent-blue: #3498db;
        --accent-green: #27ae60;
        --accent-red: #e74c3c;
        --border-color: #bdc3c7;
    }}

    body {{ 
        margin: 0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background: var(--bg-dark); 
        height: 100vh; 
        overflow: hidden; 
    }}
    
    /* MODERNE TOOLBAR */
    .toolbar {{ 
        position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
        background: var(--toolbar-bg); 
        padding: 8px 15px; 
        display: flex; gap: 12px; 
        justify-content: center; align-items: center; 
        border-radius: 50px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 1000;
        border: 1px solid var(--border-color);
    }}

    .group {{ display: flex; gap: 6px; align-items: center; }}
    .divider {{ width: 1px; height: 24px; background: #ddd; margin: 0 5px; }}

    button, select {{ 
        padding: 6px 12px; 
        border-radius: 20px; 
        border: 1px solid #ccc; 
        font-weight: 600; 
        cursor: pointer; 
        font-size: 13px; 
        height: 36px;
        transition: all 0.2s ease;
        background: white;
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    button:hover {{ background: #f8f9fa; border-color: var(--accent-blue); transform: translateY(-1px); }}
    button:active {{ transform: translateY(0); }}

    .btn-icon {{ width: 36px; justify-content: center; padding: 0; }}
    .btn-blue {{ background: var(--accent-blue); color: white; border: none; }}
    .btn-green {{ background: var(--accent-green); color: white; border: none; }}
    .btn-red {{ background: var(--accent-red); color: white; border: none; }}
    .active-tool {{ background: #f1c40f !important; color: black !important; border-color: #f39c12 !important; }}

    /* VIEWPORT */
    .viewport {{ 
        width: 100vw; 
        height: 100vh; 
        overflow: auto; 
        background: #34495e; 
        touch-action: none; 
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding-top: 80px;
    }}
    
    canvas {{ 
        background: white; 
        box-shadow: 0 0 50px rgba(0,0,0,0.5);
        image-rendering: pixelated;
    }}

    #imgInput {{ display: none; }}
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
    <div class="group">
        <button class="btn-icon" onclick="undo()" title="Fortryd">↩️</button>
        <button class="btn-icon" onclick="redo()" title="Genskab">↪️</button>
    </div>
    
    <div class="divider"></div>

    <div class="group">
        <select id="mode" style="width: 100px;">
            <option value="fill">⚫ SORT</option>
            <option value="X">❌ X</option>
            <option value="O">⭕ O</option>
            <option value="erase">⚪ SLET</option>
        </select>
        <button id="panBtn" class="btn-icon" onclick="togglePan()" title="Flyt (Pan)">✋</button>
    </div>

    <div class="divider"></div>

    <div class="group">
        <button onclick="document.getElementById('imgInput').click()">🖼️ Foto</button>
        <input type="file" id="imgInput" accept="image/*">
        
        <button class="btn-blue" onclick="exportSmart('png')">📸 PNG</button>
        <button class="btn-green" onclick="exportSmart('pdf')">🖨️ PDF</button>
        <button class="btn-red btn-icon" onclick="resetCanvas()" title="Ryd alt">🗑️</button>
    </div>
</div>

<div class="viewport" id="vp">
    <canvas id="c"></canvas>
</div>

<script>
    let COLS = {cols}, ROWS = {rows}, SIZE = {zoom}, OFFSET = 40;
    let gridData = [], history = [], redoStack = [];
    let isPan = false, scale = 1.0;
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d'), vp = document.getElementById('vp');

    function saveHistory() {{
        history.push(JSON.stringify(gridData));
        if (history.length > 30) history.shift();
        redoStack = [];
    }}

    function initGrid() {{
        canvas.width = (COLS * SIZE) + OFFSET;
        canvas.height = (ROWS * SIZE) + OFFSET;
        gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
        draw();
    }}

    function drawOnContext(tCtx, s, off, isExport = false) {{
        const margin = isExport ? 50 : 0;
        tCtx.fillStyle = "white";
        tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);

        // 1. Tegn Indhold
        tCtx.textAlign = "center";
        tCtx.textBaseline = "middle";
        for (let r = 0; r < ROWS; r++) {{
            for (let c = 0; c < COLS; c++) {{
                const val = gridData[r][c];
                if (!val) continue;
                const x = c * s + off + margin;
                const y = r * s + off + margin;
                if (val === 'fill') {{
                    tCtx.fillStyle = "black";
                    tCtx.fillRect(x, y, s, s);
                }} else {{
                    tCtx.fillStyle = "black";
                    tCtx.font = `bold ${{s * 0.6}}px Arial`;
                    tCtx.fillText(val, x + s/2, y + s/2);
                }}
            }}
        }}

        // 2. Tegn Gitterlinjer
        for (let i = 0; i <= COLS; i++) {{
            const x = i * s + off + margin;
            tCtx.beginPath();
            if (i % 10 === 0) {{ tCtx.strokeStyle = "#000"; tCtx.lineWidth = 1.5; }}
            else if (i % 5 === 0) {{ tCtx.strokeStyle = "#666"; tCtx.lineWidth = 1.0; }}
            else {{ tCtx.strokeStyle = "#ddd"; tCtx.lineWidth = 0.5; }}
            tCtx.moveTo(x, off + margin);
            tCtx.lineTo(x, (ROWS * s) + off + margin);
            tCtx.stroke();
            
            if (i < COLS && (i+1 === 1 || (i+1) % 5 === 0)) {{
                tCtx.font = (i+1) % 10 === 0 ? "bold 11px Arial" : "10px Arial";
                tCtx.fillStyle = "#555";
                tCtx.fillText(i+1, x + s/2, (off/2) + margin);
            }}
        }}

        for (let j = 0; j <= ROWS; j++) {{
            const y = j * s + off + margin;
            tCtx.beginPath();
            if (j % 10 === 0) {{ tCtx.strokeStyle = "#000"; tCtx.lineWidth = 1.5; }}
            else if (j % 5 === 0) {{ tCtx.strokeStyle = "#666"; tCtx.lineWidth = 1.0; }}
            else {{ tCtx.strokeStyle = "#ddd"; tCtx.lineWidth = 0.5; }}
            tCtx.moveTo(off + margin, y);
            tCtx.lineTo((COLS * s) + off + margin, y);
            tCtx.stroke();

            if (j < ROWS && (j+1 === 1 || (j+1) % 5 === 0)) {{
                tCtx.font = (j+1) % 10 === 0 ? "bold 11px Arial" : "10px Arial";
                tCtx.fillStyle = "#555";
                tCtx.fillText(j+1, (off/2) + margin, y + s/2);
            }}
        }}
    }}

    function draw() {{ drawOnContext(ctx, SIZE, OFFSET, false); }}

    function handleAction(e) {{
        if (isPan) return;
        const rect = canvas.getBoundingClientRect();
        const gridC = Math.floor(((e.clientX - rect.left) / scale - OFFSET) / SIZE);
        const gridR = Math.floor(((e.clientY - rect.top) / scale - OFFSET) / SIZE);
        if (gridR >= 0 && gridR < ROWS && gridC >= 0 && gridC < COLS) {{
            saveHistory();
            const mode = document.getElementById('mode').value;
            if (mode === 'erase') gridData[gridR][gridC] = null;
            else if (mode === 'fill') gridData[gridR][gridC] = (gridData[gridR][gridC] === 'fill' ? null : 'fill');
            else gridData[gridR][gridC] = (gridData[gridR][gridC] === mode ? null : mode);
            draw();
        }}
    }}

    // Event Listeners
    canvas.addEventListener('pointerdown', e => {{ if (isPan) isDown = true; else handleAction(e); }});
    window.addEventListener('pointerup', () => isDown = false);
    canvas.addEventListener('pointermove', e => {{ if (isPan && isDown) {{ vp.scrollLeft -= e.movementX; vp.scrollTop -= e.movementY; }} }});
    let isDown = false;

    function togglePan() {{ isPan = !isPan; document.getElementById('panBtn').classList.toggle('active-tool'); }}
    function undo() {{ if (history.length > 0) {{ redoStack.push(JSON.stringify(gridData)); gridData = JSON.parse(history.pop()); draw(); }} }}
    function redo() {{ if (redoStack.length > 0) {{ history.push(JSON.stringify(gridData)); gridData = JSON.parse(redoStack.pop()); draw(); }} }}
    function resetCanvas() {{ if(confirm("Ryd alt?")) initGrid(); }}

    document.getElementById('imgInput').onchange = function(e) {{
        const reader = new FileReader();
        reader.onload = function(event) {{
            const img = new Image();
            img.onload = function() {{
                saveHistory();
                const tCanvas = document.createElement('canvas'); tCanvas.width = COLS; tCanvas.height = ROWS;
                const tCtx = tCanvas.getContext('2d'); tCtx.drawImage(img, 0, 0, COLS, ROWS);
                const pix = tCtx.getImageData(0, 0, COLS, ROWS).data;
                for(let i=0; i<pix.length; i+=4) {{
                    const avg = (pix[i]+pix[i+1]+pix[i+2])/3;
                    gridData[Math.floor((i/4)/COLS)][(i/4)%COLS] = avg < 128 ? 'fill' : null;
                }}
                draw();
            }}
            img.src = event.target.result;
        }}
        reader.readAsDataURL(e.target.files[0]);
    }};

    function exportSmart(type) {{
        const dpr = 2;
        const s = SIZE * dpr, off = OFFSET * dpr, margin = 50 * dpr;
        const out = document.createElement('canvas');
        out.width = (COLS * s) + off + (margin * 2);
        out.height = (ROWS * s) + off + (margin * 2);
        drawOnContext(out.getContext('2d'), s, off, true);
        const url = out.toDataURL("image/png");
        if(type === 'png') {{
            const a = document.createElement('a'); a.download = "design.png"; a.href = url; a.click();
        }} else {{
            const w = window.open();
            w.document.write(`<html><body style="margin:0;display:flex;justify-content:center;"><img src="${{url}}" style="max-width:100%;"><script>setTimeout(()=>window.print(),500);<\\/script></body></html>`);
        }}
    }}

    initGrid();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
