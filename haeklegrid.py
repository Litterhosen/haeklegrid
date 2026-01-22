import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hækle Grid", layout="wide")

st.sidebar.header("Indstillinger")
rows = st.sidebar.number_input("Rækker", 5, 50, 15)
cols = st.sidebar.number_input("Kolonner", 5, 30, 15)
cell_size = st.sidebar.slider("Zoom (Pixel størrelse)", 15, 50, 30)

st.title("🧶 Hækle-Grid (Stitch Fiddle Style)")
st.write("Klik på felterne for at tænde/slukke dem.")

# Vi bygger selve gridet i ren HTML/CSS for at tvinge layoutet på plads
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  /* Dette sikrer at gridet ALDRIG stabler sig, selv på mobil */
  .grid-container {{
    display: grid;
    grid-template-columns: repeat({cols}, {cell_size}px); /* Tvinger X antal kolonner */
    gap: 1px;
    background-color: #ddd; /* Farven på stregerne imellem */
    width: fit-content;
    padding: 10px;
  }}

  .cell {{
    width: {cell_size}px;
    height: {cell_size}px;
    background-color: white;
    cursor: pointer;
  }}

  /* Når klassen 'active' er på, bliver den sort */
  .cell.active {{
    background-color: black;
  }}
</style>
</head>
<body>

<div class="grid-container" id="grid">
  {''.join([f'<div class="cell" onclick="toggle(this)" id="c-{i}"></div>' for i in range(rows * cols)])}
</div>

<script>
  // Simpel javascript der skifter farve med det samme (uden ventetid)
  function toggle(el) {{
    el.classList.toggle("active");
  }}
</script>

</body>
</html>
"""

# Indsæt HTML'en i appen
# height beregnes så scrollbaren passer nogenlunde
components.html(html_code, height=(rows * cell_size) + 50, scrolling=True)

st.sidebar.info("Bemærk: Da dette kører som ren grafik, nulstilles mønsteret hvis du ændrer antal rækker/kolonner.")
