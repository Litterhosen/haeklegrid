import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np

st.set_page_config(page_title="Hækle Design", layout="wide")

st.title("🧶 Hækle-Grid (Stitch Fiddle Style)")

# --- SIDEBAR INDSTILLINGER ---
st.sidebar.header("Indstillinger")
grid_size = st.sidebar.slider("Maskestørrelse (zoom)", 10, 50, 25)
rows = st.sidebar.number_input("Rækker", 5, 100, 20)
cols = st.sidebar.number_input("Kolonner", 5, 100, 20)

bg_color = "#ffffff"
drawing_mode = st.sidebar.selectbox("Værktøj", ("Fyld maske", "Viskelæder"))
stroke_width = st.sidebar.slider("Pensel størrelse", 1, 10, 3)

# --- CANVAS OPSÆTNING ---
# Her beregner vi størrelsen i pixels
width = cols * grid_size
height = rows * grid_size

st.write(f"Brug din finger eller mus til at tegne direkte på nettet ({cols}x{rows} masker):")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 1)",  # Farve på masken
    stroke_width=stroke_width,
    stroke_color="#000000" if drawing_mode == "Fyld maske" else "#ffffff",
    background_color=bg_color,
    height=height,
    width=width,
    drawing_mode="freedraw",
    key="canvas",
    display_toolbar=True,
)

# --- INSTRUKTIONER ---
st.info("💡 Tryk på 'Download' ikonet under nettet for at gemme dit billede.")

st.markdown("""
<style>
    /* Gør det nemt at tegne på mobil uden at siden ruller */
    canvas {
        border: 1px solid #ccc;
        touch-action: none;
    }
</style>
""", unsafe_allow_html=True)
