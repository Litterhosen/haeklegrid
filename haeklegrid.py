import streamlit as st
import streamlit.components.v1 as components

# --- OPSÆTNING ---
st.set_page_config(page_title="Hækle Grid Pro v3", layout="wide", initial_sidebar_state="expanded")

st.sidebar.header("1. Dimensioner")
rows = st.sidebar.number_input("Højde (Rækker)", 1, 200, 114)
cols = st.sidebar.number_input("Bredde (Masker)", 1, 100, 23)

st.sidebar.header("2. Zoom & Visning")
cell_size = st.sidebar.slider("Felt størrelse", 10, 80, 25)

st.sidebar.header("3. Værktøj")
mode = st.sidebar.selectbox("Klik-funktion", ["⚫ SORT", "❌ X", "⭕ O", "⚪ SLET"])

# Konverter mode til en værdi JS kan forstå
mode_map = {"⚫ SORT": "fill", "❌ X": "X", "⭕ O": "O", "⚪ SLET": "erase"}
js_mode = mode_map[mode]

# --- GRID GENERERING (Python -> HTML) ---
grid_html = ""
for r in range(1, rows + 1):
    for c in range(1, cols + 1):
        # Find klasser for tykke streger (hver 5. og 10.)
        classes = ["cell"]
        if c % 10 == 0: classes.append("v-10")
        elif c % 5 == 0: classes.append("v-5")
        
        if r % 10 == 0: classes.append("h-10")
        elif r % 5 == 0: classes.append("h-5")
        
        # Tilføj labels på hver 5. række/kolonne
        label = ""
        if (r == 1 or r % 5 == 0) and c == 1:
            label = f'<span class="label-r">{r}</span>'
        if r == 1 and (c == 1 or c % 5 == 0):
            label += f'<span class="label-c">{c}</span>'
            
        class_str = " ".join(classes)
        grid_html += f'<div class="{class_str}" onclick="applyMode(this)">{label}</div>'

# --- HTML / CSS / JS ---
full_code = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
    body {{ font-family: sans-serif; background: #2c3e50; margin: 0; padding: 20px; color: white; }}
    
    /* Grid Container */
    .grid-wrapper {{
        display: inline-block;
        background: white;
        padding: 40px; /* Plads til tal-labels */
        border: 2px solid #000;
        position: relative;
    }}
    
    .grid-container {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        background-color: #ddd; /* Gitterlinje farve */
        gap: 1px;
    }}

    /* Felter */
    .cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        background-color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: {cell_size * 0.6}px;
        color: black;
        position: relative;
        user-select: none;
    }}

    /* Streg-logik (Hver 5. og 10.) */
    .v-5 {{ border-right: 2px solid #888 !important; }}
    .v-10 {{ border-right: 3px solid #000 !important; }}
    .h-5 {{ border-bottom: 2px solid #888 !important; }}
    .h-10 {{ border-bottom: 3px solid #000 !important; }}

    /* Aktive tilstande */
    .cell.active-fill {{ background-color: black !important; }}
    
    /* Tal labels */
    .label-r {{ position: absolute; left: -25px; font-size: 10px; color: #666; width: 20px; text-align: right; }}
    .label-c {{ position: absolute; top: -25px; font-size: 10px; color: #666; width: 100%; text-align: center; }}

    /* Knapper */
    .toolbar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 1000; }}
    button {{ padding: 10px 20px; border-radius: 20px; border: none; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    .btn-save {{ background: #27ae60; color: white; }}
    .btn-clear {{ background: #e74c3c; color: white; }}
</style>
</head>
<body>

<div class="grid-wrapper" id="capture">
    <div class="grid-container">
        {grid_html}
    </div>
</div>

<div class="toolbar">
    <button class="btn-save" onclick="download()">📸 Gem Billede</button>
    <button class="btn-clear" onclick="resetGrid()">🗑️ Ryd alt</button>
</div>

<script>
    let currentMode = "{js_mode}";

    function applyMode(el) {{
        if (currentMode === "fill") {{
            el.classList.toggle("active-fill");
            el.innerText = ""; // Fjern X eller O hvis man maler sort
        }} 
        else if (currentMode === "X") {{
            el.classList.remove("active-fill");
            el.innerText = (el.innerText === "X") ? "" : "X";
        }}
        else if (currentMode === "O") {{
            el.classList.remove("active-fill");
            el.innerText = (el.innerText === "O") ? "" : "O";
        }}
        else if (currentMode === "erase") {{
            el.classList.remove("active-fill");
            el.innerText = "";
        }}
    }}

    function resetGrid() {{
        if(confirm("Vil du slette alt?")) {{
            document.querySelectorAll('.cell').forEach(c => {{
                c.classList.remove('active-fill');
                c.innerText = "";
            }});
        }}
    }}

    function download() {{
        html2canvas(document.querySelector("#capture")).then(canvas => {{
            let link = document.createElement('a');
            link.download = 'haekle-moenster.png';
            link.href = canvas.toDataURL();
            link.click();
        }});
    }}
</script>
</body>
</html>
"""

# Vis komponenten
# Vi beregner højden dynamisk så den ruller pænt
calc_height = (rows * (cell_size + 1)) + 200
components.html(full_code, height=calc_height, scrolling=True)

st.info("💡 Tip: Brug slideren i venstre side til at zoome ind og ud. Brug rullebjælkerne til at navigere i det lange mønster.")
