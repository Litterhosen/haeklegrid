import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image

st.set_page_config(page_title="Design Grid Pro", layout="wide", initial_sidebar_state="collapsed")

# --- CSS FOR BEDRE NAVIGERING ---
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Gør iframe beholderen mere mobilvenlig */
    iframe {
        border-radius: 8px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Opsætning")
    cols = st.number_input("Bredde (felter)", 5, 500, 30)
    rows = st.number_input("Højde (felter)", 5, 500, 30)
    cell_size = st.slider("Feltstørrelse (Zoom)", 10, 80, 25)
    
    st.divider()
    uploaded_file = st.file_uploader("Importér billede", type=['png', 'jpg', 'jpeg'])

# --- BILLEDE LOGIK ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    img = Image.open(uploaded_file).convert('L').resize((cols, rows), Image.NEAREST)
    grid_data = (np.array(img) < 128).astype(int)

# --- HTML / JS KOMPONENT ---
grid_html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
    body {{ 
        font-family: sans-serif; 
        margin: 0; 
        display: flex; 
        flex-direction: column; 
        height: 100vh;
        background: #f0f2f6;
    }}
    
    /* Sticky toolbar der ikke forsvinder ved scroll */
    .toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 10px;
        background: white;
        border-bottom: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 1000;
        justify-content: center;
    }}

    /* Container til grid med scrolling */
    .scroll-container {{
        flex: 1;
        overflow: auto; /* Tillader både horisontal og vertikal scroll */
        padding: 20px;
        display: block;
        -webkit-overflow-scrolling: touch;
    }}

    .grid-container {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        gap: 1px;
        background-color: #ccc;
        border: 2px solid #333;
        width: fit-content;
        margin: 0 auto; /* Centrerer gridet i scroll-området */
    }}

    .cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: {int(cell_size*0.6)}px;
        user-select: none;
        touch-action: none; /* Forhindrer browser-scroll når vi tegner */
    }}

    /* Pan-mode: Tillader scroll på cellerne */
    .pan-mode .cell {{
        touch-action: auto !important;
        cursor: grab;
    }}

    .cell.active {{ background-color: black !important; color: white !important; }}
    
    @media print {{
        .toolbar {{ display: none !important; }}
        body, .scroll-container {{ overflow: visible; display: block; }}
        .grid-container {{ border: 1px solid #000; -webkit-print-color-adjust: exact; }}
    }}

    button, select {{
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #ccc;
        background: white;
        font-size: 14px;
    }}
    
    .active-tool {{ background: #007aff; color: white; border-color: #0056b3; }}
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
    <select id="mode" onchange="updateTool()">
        <option value="fill">⚫ Sort</option>
        <option value="X">❌ X</option>
        <option value="O">⭕ O</option>
        <option value="erase">⚪ Visk</option>
    </select>
    
    <button id="pan-btn" onclick="togglePan()">✋ Panorer</button>
    <button onclick="download()">💾 Gem</button>
    <button onclick="window.print()">🖨️ PDF</button>
</div>

<div class="scroll-container" id="scroll-area">
    <div id="capture">
        <div class="grid-container" id="grid">
            {''.join([f'<div class="cell {"active" if grid_data.flatten()[i]==1 else ""}" onclick="handleClick(this)"></div>' for i in range(rows*cols)])}
        </div>
    </div>
</div>

<script>
    let isPanMode = false;

    function updateTool() {{
        if(isPanMode) togglePan(); // Deaktiver pan hvis man skifter værktøj
    }}

    function togglePan() {{
        isPanMode = !isPanMode;
        const btn = document.getElementById('pan-btn');
        const grid = document.getElementById('grid');
        
        if(isPanMode) {{
            btn.classList.add('active-tool');
            grid.classList.add('pan-mode');
        }} else {{
            btn.classList.remove('active-tool');
            grid.classList.remove('pan-mode');
        }}
    }}

    function handleClick(el) {{
        if (isPanMode) return; // Gør intet hvis vi panorerer
        
        const mode = document.getElementById('mode').value;
        if (mode === "fill") {{
            el.innerHTML = "";
            el.classList.toggle("active");
        }} else if (mode === "erase") {{
            el.innerHTML = "";
            el.classList.remove("active");
        }} else {{
            el.classList.remove("active");
            el.innerHTML = el.innerHTML === mode ? "" : mode;
        }}
    }}

    function download() {{
        const captureArea = document.querySelector("#capture");
        html2canvas(captureArea, {{ scale: 2 }}).then(canvas => {{
            const link = document.createElement('a');
            link.download = 'design.png';
            link.href = canvas.toDataURL();
            link.click();
        }});
    }}
</script>
</body>
</html>
"""

components.html(grid_html, height=800, scrolling=False)
