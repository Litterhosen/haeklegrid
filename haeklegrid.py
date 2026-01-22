import streamlit as st
import numpy as np
from PIL import Image

# Tving siden til at være bred og hav en titel
st.set_page_config(page_title="Hækle App", layout="wide")

# --- CSS FOR MOBIL-OPTIMERING ---
# Dette er "magien", der forhindrer kolonner i at stable på mobilen
st.markdown("""
    <style>
    /* Fjern standard Streamlit padding for at få plads */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* TVING kolonner til at blive ved siden af hinanden (ingen stacking) */
    [data-testid="column"] {
        flex-basis: 0% !important;
        flex-grow: 1 !important;
        min-width: 0px !important;
    }

    /* Gør knapperne kvadratiske og touch-venlige */
    .stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0px !important;
        margin: 0px !important;
        min-width: 0px !important;
        border-radius: 2px !important;
        line-height: 0 !important;
    }
    
    /* Skjul tekst i knapperne for at holde dem rene */
    .stButton p {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧶 Mobil Hækle-Grid")

# Sidebar til indstillinger (skjult som standard på mobil)
with st.sidebar:
    st.header("Indstillinger")
    rows = st.number_input("Rækker", 5, 50, 20)
    cols = st.number_input("Kolonner", 5, 30, 20) # Hold kolonner lave på mobil (max 20-30)
    
    uploaded_file = st.file_uploader("Upload skitse", type=['png', 'jpg', 'jpeg'])
    if st.button("Ryd net"):
        st.session_state.grid = np.zeros((rows, cols), dtype=int)
        st.rerun()

# Initialiser grid
if 'grid' not in st.session_state or st.session_state.grid.shape != (rows, cols):
    st.session_state.grid = np.zeros((rows, cols), dtype=int)

# Billed-logik
if uploaded_file:
    if st.sidebar.button("Konverter nu"):
        img = Image.open(uploaded_file).convert('L').resize((cols, rows), Image.NEAREST)
        st.session_state.grid = (np.array(img) < 128).astype(int)

# --- TEGN GRIDET ---
# Vi bruger en container til at holde det samlet
with st.container():
    for r in range(rows):
        columns = st.columns(cols)
        for c in range(cols):
            active = st.session_state.grid[r, c]
            # Brug "primary" for sort og "secondary" for hvid
            if columns[c].button("", key=f"{r}-{c}", type="primary" if active else "secondary"):
                st.session_state.grid[r, c] = 0 if active else 1
                st.rerun()
