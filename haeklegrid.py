import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image

st.set_page_config(page_title="Design Grid Pro", layout="wide")

# --- CSS FOR MODERNE UI ---
st.markdown("""
<style>
    /* Skjul sidebar automatisk på små skærme (standard Streamlit opførsel) */
    .stApp { background-color: #f8f9fa; }
    
    /* Top Menu Styling */
    .top-menu {
        display: flex;
        gap: 10px;
        padding: 10px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Indstillinger) ---
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Bredde (felter)", 5, 500, 30)
    rows = st.number_input("Højde (felter)", 5, 500, 30)
    cell_size = st.slider("Zoom / Feltstørrelse", 10, 60, 25)
    
    st.divider()
    st.header("📥 Import")
    uploaded_file = st.file_uploader("Konverter billede", type=['png', 'jpg', 'jpeg'])

# --- LOGIK TIL BILLEDE-IMPORT ---
grid_data = np.zeros((rows, cols), dtype=int)
if uploaded_file:
    img = Image.open(uploaded_file).convert('L').resize((cols, rows), Image.NEAREST)
    grid_data = (np.array(img) < 128).astype(int)

# --- HOVEDSKÆRM ---
st.title("🎨 Multi-Grid Designer")

# Top eksport knapper (vi bruger JS til at aktivere dem i HTML-komponenten)
st.info("💡 Tip: Vælg symbol nederst og klik på felterne. På mobil kan du 'zoome' ind med fingrene.")

# --- HTML / JS GRID COMPONENT ---
grid_html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
    body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }}
    
    .toolbar {{
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        background: #eee;
        padding: 15px;
        border-radius: 8px;
        position: sticky;
        top: 0;
        z-index: 100;
    }}

    /* Tvinger farver frem ved print (vigtigt for mobil PDF) */
    @media print {{
        .toolbar {{ display: none !important; }} /* Skjul knapper på print */
        body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        .grid-container {{ border: 1px solid #000 !important; }}
    }}

    .grid-container {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        gap: 1px;
        background-color: #bbb;
        border: 2px solid #333;
        width: fit-content;
        -webkit-print-color-adjust: exact; /* Sikrer farver i browser-visning */
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
        font-size: {int(cell_size*0.7)}px;
        cursor: pointer;
        user-select: none;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}

    .cell.active {{ 
        background-color: black !important; /* !important er nødvendigt for print */
        color: white !important; 
    }}
    
    button {{
        padding: 8px 15px;
        border: none;
        border-radius: 5px;
        background: #007bff;
        color: white;
        cursor: pointer;
    }}
    
    select {{ padding: 8px; border-radius: 5px; }}
</style>
</head>
<body>

<div class="toolbar">
    <select id="mode">
        <option value="fill">Udfyld (Sort)</option>
        <option value="X">Tegn X</option>
        <option value="O">Tegn O</option>
        <option value="erase">Viskelæder</option>
    </select>
    <button onclick="download()">💾 Gem til Kamerarulle</button>
    <button onclick="window.print()" style="background:#6c757d">🖨️ PDF / Print</button>
</div>

<div id="capture">
    <div class="grid-container">
        {''.join([f'<div class="cell {"active" if grid_data.flatten()[i]==1 else ""}" onclick="mark(this)"></div>' for i in range(rows*cols)])}
    </div>
</div>

<script>
    function mark(el) {{
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
        // Vi bruger en højere scale for at få et skarpt billede til fotos
        html2canvas(document.querySelector("#capture"), {{ scale: 2 }}).then(canvas => {{
            const link = document.createElement('a');
            link.download = 'mit-design.png';
            link.href = canvas.toDataURL("image/png");
            link.click();
        }});
    }}
</script>
</body>
</html>
"""

<div class="toolbar">
    <select id="mode">
        <option value="fill">Udfyld (Sort)</option>
        <option value="X">Tegn X</option>
        <option value="O">Tegn O</option>
        <option value="erase">Viskelæder</option>
    </select>
    <button onclick="download()">💾 Gem til Kamerarulle</button>
    <button onclick="window.print()" style="background:#6c757d">🖨️ PDF</button>
</div>

<div id="capture">
    <div class="grid-container">
        {''.join([f'<div class="cell {"active" if grid_data.flatten()[i]==1 else ""}" onclick="mark(this)"></div>' for i in range(rows*cols)])}
    </div>
</div>

<script>
    function mark(el) {{
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
        html2canvas(document.querySelector("#capture")).then(canvas => {{
            const link = document.createElement('a');
            link.download = 'mit-design.png';
            link.href = canvas.toDataURL("image/png");
            link.click();
        }});
    }}
</script>
</body>
</html>
"""

components.html(grid_html, height=2000, scrolling=True)

