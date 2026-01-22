import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="Hækle Design App", layout="wide")

st.title("🧶 Hækle-Grid Designer Pro")

# --- SIDEBAR: INDSTILLINGER ---
st.sidebar.header("1. Opsætning")
rows = st.sidebar.number_input("Rækker (Højde)", 5, 100, 30)
cols = st.sidebar.number_input("Kolonner (Bredde)", 5, 100, 30)

# --- BILLEDUPLOAD FUNKTION ---
st.sidebar.header("2. Digitaliser tegning")
uploaded_file = st.sidebar.file_uploader("Upload billede af din skitse", type=['png', 'jpg', 'jpeg'])

# Initialiser grid i session state
if 'grid' not in st.session_state or st.session_state.grid.shape != (rows, cols):
    st.session_state.grid = np.zeros((rows, cols), dtype=int)

if uploaded_file is not None:
    if st.sidebar.button("Konverter billede til grid"):
        img = Image.open(uploaded_file).convert('L') # Gør gråtonet
        img = img.resize((cols, rows), resample=Image.NEAREST)
        img_array = np.array(img)
        # Tærskel: alt mørkere end 128 bliver en maske (1)
        st.session_state.grid = (img_array < 128).astype(int)

# --- INTERAKTIVT GRID ---
st.write("Tryk på felterne for at finpudse mønsteret:")

# CSS til mobilvenlige knapper
st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0px !important;
        border-radius: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

for r in range(rows):
    columns = st.columns(cols)
    for c in range(cols):
        is_active = st.session_state.grid[r, c]
        if columns[c].button("", key=f"{r}-{c}", 
                             type="primary" if is_active else "secondary"):
            st.session_state.grid[r, c] = 0 if is_active else 1
            st.rerun()

# --- EKSPORT ---
st.sidebar.header("3. Gem")
if st.sidebar.button("Ryd alt"):
    st.session_state.grid = np.zeros((rows, cols), dtype=int)
    st.rerun()