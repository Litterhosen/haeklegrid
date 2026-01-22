import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Hækle Grid Pro", layout="wide")

# --- FUNKTIONER ---
def process_image(uploaded_file, target_rows, target_cols):
    """Omdanner uploadet billede til et grid af 0 og 1"""
    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert('L') # Til sort/hvid
        # Skalér billedet ned så 1 pixel = 1 maske
        img = img.resize((target_cols, target_rows), resample=Image.NEAREST)
        img_array = np.array(img)
        # Alt mørkere end grå (128) bliver sort (1)
        return (img_array < 128).astype(int)
    return np.zeros((target_rows, target_cols), dtype=int)

# --- SIDEBAR: INDSTILLINGER & IMPORT ---
st.sidebar.header("1. Opsætning")
cols = st.sidebar.number_input("Bredde (masker)", 5, 100, 20)
rows = st.sidebar.number_input("Højde (rækker)", 5, 100, 20)
cell_size = st.sidebar.slider("Zoom niveau", 15, 60, 25)

st.sidebar.header("2. Import (Kamera/Billede)")
st.sidebar.info("Upload et billede, eller tag et foto med mobilen for at omdanne det til et mønster.")
uploaded_file = st.sidebar.file_uploader("Vælg fil", type=['png', 'jpg', 'jpeg'])

# Knap til at indlæse
grid_data = np.zeros((rows, cols), dtype=int) # Standard: Tomt net

if uploaded_file:
    st.sidebar.write("Billede fundet! Tilpasser til nettet...")
    grid_data = process_image(uploaded_file, rows, cols)

# --- HOVEDSKÆRM ---
st.title("🧶 Hækle-Grid Pro")
st.write("Klik på felterne for at rette til. Brug knapperne under nettet til at gemme.")

# --- GENERER HTML/JS ---
# Vi bygger gridet baseret på 'grid_data' fra Python
grid_html_content = ""
for r in range(rows):
    for c in range(cols):
        # Hvis data siger 1, tilføj klassen 'active' (sort)
        is_active = "active" if grid_data[r, c] == 1 else ""
        grid_html_content += f'<div class="cell {is_active}" onclick="toggle(this)"></div>'

# HTML/CSS/JS Koden
full_html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
<style>
  body {{ font-family: sans-serif; margin: 0; padding: 10px; }}
  
  /* Selve nettet */
  .grid-container {{
    display: grid;
    grid-template-columns: repeat({cols}, {cell_size}px);
    gap: 1px;
    background-color: #ccc;
    border: 1px solid #999;
    width: fit-content;
    margin-bottom: 20px;
  }}

  .cell {{
    width: {cell_size}px;
    height: {cell_size}px;
    background-color: white;
    cursor: pointer;
  }}

  .cell.active {{
    background-color: black;
  }}

  /* Knapper */
  .btn-group {{ margin-top: 10px; display: flex; gap: 10px; }}
  button {{
    padding: 10px 20px;
    font-size: 16px;
    background-color: #ff4b4b;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }}
  button:hover {{ background-color: #d43f3f; }}
  .btn-blue {{ background-color: #0083B8; }}
  .btn-blue:hover {{ background-color: #006892; }}

</style>
</head>
<body>

<div id="capture-area" style="padding: 5px; display: inline-block; background: white;">
    <div class="grid-container" id="grid">
      {grid_html_content}
    </div>
</div>

<div class="btn-group">
  <button onclick="downloadImage()" class="btn-blue">📸 Gem som Billede</button>
  <button onclick="window.print()">🖨️ Print / PDF</button>
  <button onclick="clearGrid()">🗑️ Ryd alt</button>
</div>

<script>
  // Skift farve
  function toggle(el) {{
    el.classList.toggle("active");
  }}

  // Ryd nettet
  function clearGrid() {{
    if(confirm("Er du sikker på du vil slette alt?")) {{
        var cells = document.getElementsByClassName("cell");
        for (var i = 0; i < cells.length; i++) {{
            cells[i].classList.remove("active");
        }}
    }}
  }}

  // Gem som billede (PNG)
  function downloadImage() {{
    html2canvas(document.querySelector("#capture-area")).then(canvas => {{
        var link = document.createElement('a');
        link.download = 'haekle_moenster.png';
        link.href = canvas.toDataURL();
        link.click();
    }});
  }}
</script>

</body>
</html>
"""

# Beregn højde så iframe passer
iframe_height = (rows * cell_size) + 150 
components.html(full_html, height=iframe_height, scrolling=True)
