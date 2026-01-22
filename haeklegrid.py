import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import io

# Konfiguration af siden
st.set_page_config(page_title="Design Grid Pro", layout="wide", initial_sidebar_state="collapsed")

# --- CSS TIL STYLING AF STREAMLIT ELEMENTER ---
st.markdown("""
<style>
    /* Gør hovedområdet bredere og pænere */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    /* Skjul Streamlit menuen for et rent app-look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: INDSTILLINGER & IMPORT ---
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Bredde (felter)", 5, 500, 30)
    rows = st.number_input("Højde (felter)", 5, 500, 30)
    cell_size = st.slider("Feltstørrelse (Zoom)", 10, 80, 25)
    
    st.divider()
    st.header("📥 Import")
    st.write("Tag et billede af din skitse eller upload en fil:")
    uploaded_file = st.file_uploader("Vælg billede", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    st.info("Tryk uden for denne menu for at lukke den på mobil.")

# --- LOGIK TIL BILLEDE-IMPORT ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    # Konverter billede til sort/hvid grid
    img = Image.open(uploaded_file).convert('L').resize((cols, rows), Image.NEAREST)
    # Tærskelværdi: alt under 128 (mørkt) bliver 'aktivt'
    grid_data = (np.array(img) < 128).astype(int)

# --- HOVEDSKÆRM ---
st.title("🎨 Multi-Grid Designer")

# Konstruktion af HTML/JS Grid
# Vi bruger 'print-color-adjust' for at sikre at PDF ikke bliver blank
grid_html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
    body {{ 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        margin: 0;
        padding: 10px;
        background-color: #f8f9fa;
    }}
    
    /* Værktøjslinje i toppen */
    .toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        position: sticky;
        top: 0;
        z-index: 1000;
        width: 100%;
        max-width: 800px;
        justify-content: center;
    }}

    /* CSS til Print - sikrer at farver kommer med på PDF */
    @media print {{
        .toolbar {{ display: none !important; }}
        body {{ 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
            background: white !important;
        }}
        .grid-container {{ border: 1px solid #000 !important; }}
        .cell.active {{ background-color: black !important; }}
    }}

    .grid-container {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        gap: 1px;
        background-color: #ccc;
        border: 2px solid #444;
        width: fit-content;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}

    .cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: {int(cell_size*0.65)}px;
        cursor: pointer;
        user-select: none;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}

    .cell.active {{ 
        background-color: black !important; 
        color: white !important; 
    }}
    
    /* Knapper og inputs */
    button, select {{
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        cursor: pointer;
        transition: transform 0.1s;
    }}
    
    button:active {{ transform: scale(0.95); }}
    
    .btn-save {{ background-color: #007aff; color: white; font-weight: 600; }}
    .btn-print {{ background-color: #5856d6; color: white; }}
    .btn-clear {{ background-color: #ff3b30; color: white; }}
    
    select {{
        background-color: #e9e9eb;
        color: black;
        font-weight: 500;
    }}

    #capture-area {{
        padding: 10px;
        background: white;
        border-radius: 4px;
    }}
</style>
</head>
<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">⚫ Fyld felt</option>
        <option value="X">❌ Tegn X</option>
        <option value="O">⭕ Tegn O</option>
        <option value="erase">⚪ Viskelæder</option>
    </select>
    <button class="btn-save" onclick="download()">💾 Gem til Fotos</button>
    <button class="btn-print" onclick="window.print()">🖨️ PDF / Print</button>
    <button class="btn-clear" onclick="clearAll()">🗑️ Ryd</button>
</div>

<div id="capture-area">
    <div class="grid-container" id="main-grid">
        {''.join([f'<div class="cell {"active" if grid_data.flatten()[i]==1 else ""}" onclick="mark(this)"></div>' for i in range(rows*cols)])}
    </div>
</div>

<script>
    // Funktion til at tegne/skifte
    function mark(el) {{
        const mode = document.getElementById('mode').value;
        
        if (mode === "fill") {{
            el.innerHTML = "";
            el.classList.toggle("active");
        }} else if (mode === "erase") {{
            el.innerHTML = "";
            el.classList.remove("active");
        }} else {{
            // Hvis man klikker med X eller O
            el.classList.remove("active");
            if (el.innerHTML === mode) {{
                el.innerHTML = "";
            }} else {{
                el.innerHTML = mode;
            }}
        }}
    }}

    // Nulstil alt
    function clearAll() {{
        if(confirm("Vil du slette hele dit mønster?")) {{
            const cells = document.querySelectorAll('.cell');
            cells.forEach(c => {{
                c.innerHTML = "";
                c.classList.remove("active");
            }});
        }}
    }}

    // Eksport til billede
    function download() {{
        const area = document.querySelector("#capture-area");
        html2canvas(area, {{ 
            scale: 2,
            backgroundColor: "#ffffff",
            logging: false
        }}).then(canvas => {{
            const link = document.createElement('a');
            link.download = 'mit-design-grid.png';
            link.href = canvas.toDataURL("image/png");
            link.click();
        }});
    }}
</script>

</body>
</html>
"""

# Indsæt komponenten med dynamisk højde
components.html(grid_html, height=(rows * cell_size) + 200, scrolling=True)

st.caption("Design Grid Pro v2.0 - Udviklet til hækling, strik og broderi.")
