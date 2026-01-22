import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from PIL import Image
import json

st.set_page_config(
    page_title="Grid Designer Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Skjul Streamlit UI elementer permanent med CSS (fjerner Fork, GitHub, Menu osv.)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}
    [data-testid="stToolbar"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Indstillinger")
    cols = st.number_input("Kolonner", 5, 400, 60)
    rows = st.number_input("Rækker", 5, 400, 60)
    cell_size = st.slider("Zoom", 5, 60, 20)

    st.divider()
    uploaded_file = st.file_uploader("Importér billede", type=["png", "jpg", "jpeg"])
    
    import_data = []
    if uploaded_file:
        img = Image.open(uploaded_file).convert("L").resize((cols, rows), Image.NEAREST)
        arr = np.array(img)
        import_data = np.where(arr.flatten() < 128)[0].tolist()

# ---------- HTML & JAVASCRIPT ----------
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

<style>
body {
    margin: 0; padding: 0;
    background: #f0f0f0;
    font-family: -apple-system, sans-serif;
    display: flex; flex-direction: column;
    height: 100vh; overflow: hidden;
}

.toolbar {
    background: white; padding: 15px;
    border-bottom: 1px solid #ccc;
    display: flex; flex-wrap: wrap; gap: 10px;
    z-index: 1001; justify-content: center;
}

.grid-wrap {
    flex: 1; overflow: auto;
    padding: 20px; display: flex;
    justify-content: center; align-items: flex-start;
    -webkit-overflow-scrolling: touch;
}

.grid {
    display: grid;
    gap: 1px; 
    background-color: #000 !important;
    border: 1px solid #000;
    width: fit-content;
    background-color: white;
}

.cell {
    background-color: white;
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; user-select: none;
    min-width: var(--sz); min-height: var(--sz);
}

.cell.active { background-color: black !important; }

button {
    padding: 12px 18px; border-radius: 10px;
    border: none; background: #eee;
    font-size: 14px; font-weight: 600; cursor: pointer;
}

.btn-blue { background: #007aff; color: white; }
.btn-green { background: #34c759; color: white; }

/* ULTRA-REN PRINT: Skjuler ALT undtagen mønstret */
@media print {
    @page { margin: 0; }
    body, html { background: white !important; }
    /* Skjul alt i parent containers (Streamlit) */
    header, footer, .toolbar, #loading { display: none !important; }
    
    /* Tving kun grid til at være synlig */
    .grid-wrap { padding: 0; margin: 0; overflow: visible !important; }
    .grid { 
        position: absolute; left: 0; top: 0;
        gap: 0 !important; border: 1px solid black !important; 
    }
    .cell { 
        border: 0.1pt solid black !important;
        -webkit-print-color-adjust: exact; 
        print-color-adjust: exact; 
    }
}

#loading {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: white; display: flex; justify-content: center; align-items: center; z-index: 2000;
}
</style>
</head>
<body>

<div id="loading">Opbygger gitter...</div>

<div class="toolbar">
    <select id="mode" style="padding:10px; border-radius:8px;">
        <option value="fill">⚫ Sort</option>
        <option value="X">❌ X</option>
        <option value="O">⭕ O</option>
        <option value="erase">⚪ Slet</option>
    </select>
    <button id="panBtn" onclick="togglePan()">✋ Panorer</button>
    <button class="btn-blue" onclick="saveToCamera()">📸 Gem i Fotos</button>
    <button class="btn-green" onclick="window.print()">🖨️ PDF / Print</button>
    <button onclick="clearGrid()">🗑️ Ryd</button>
</div>

<div class="grid-wrap" id="view">
    <div id="grid" class="grid"></div>
</div>

<script>
const COLS = __COLS__;
const ROWS = __ROWS__;
const SIZE = __SIZE__;
const IMPORT_DATA = __IMPORT_DATA__;

let isPanMode = false;
const grid = document.getElementById("grid");

grid.style.setProperty('--sz', SIZE + "px");
grid.style.gridTemplateColumns = `repeat(${COLS}, ${SIZE}px)`;

function generateGrid() {
    const fragment = document.createDocumentFragment();
    const importSet = new Set(IMPORT_DATA);

    for (let i = 0; i < ROWS * COLS; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.style.width = SIZE + "px";
        cell.style.height = SIZE + "px";
        cell.style.fontSize = (SIZE * 0.7) + "px";

        if (importSet.has(i)) cell.classList.add("active");

        cell.onclick = function () {
            if (isPanMode) return;
            const mode = document.getElementById("mode").value;
            if (mode === "fill") {
                cell.textContent = "";
                cell.classList.toggle("active");
            } else if (mode === "erase") {
                cell.textContent = "";
                cell.classList.remove("active");
            } else {
                cell.classList.remove("active");
                cell.textContent = cell.textContent === mode ? "" : mode;
            }
        };
        fragment.appendChild(cell);
    }
    grid.appendChild(fragment);
    document.getElementById("loading").style.display = "none";
}

setTimeout(generateGrid, 50);

function togglePan() {
    isPanMode = !isPanMode;
    document.getElementById("panBtn").style.background = isPanMode ? "#5856d6" : "#eee";
    document.getElementById("panBtn").style.color = isPanMode ? "white" : "black";
    document.getElementById("view").style.touchAction = isPanMode ? "auto" : "none";
}

function clearGrid() {
    if (confirm("Ryd alt?")) {
        document.querySelectorAll(".cell").forEach(c => {
            c.textContent = "";
            c.classList.remove("active");
        });
    }
}

// NY METODE TIL KAMERARULLE (Mobil optimeret)
function saveToCamera() {
    const btn = event.target;
    btn.textContent = "Genererer...";
    
    html2canvas(grid, { 
        backgroundColor: "#ffffff", 
        scale: 3, // Høj kvalitet
        useCORS: true
    }).then(canvas => {
        canvas.toBlob(function(blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "mit-haekle-moenster.png";
            
            // Simuler klik
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            btn.textContent = "📸 Gem i Fotos";
            
            // På iPhone vil dette nu oftere trigger "Gem billede" dialogen direkte
            // fremfor kun at sende til filer.
        }, 'image/png');
    });
}
</script>
</body>
</html>
"""

final_html = (html_template
    .replace("__COLS__", str(cols))
    .replace("__ROWS__", str(rows))
    .replace("__SIZE__", str(cell_size))
    .replace("__IMPORT_DATA__", json.dumps(import_data))
)

# Vi bruger en lidt større højde for at sikre plads til værktøjslinjen på mobil
components.html(final_html, height=1200, scrolling=False)
