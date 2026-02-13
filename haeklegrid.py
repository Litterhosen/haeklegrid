import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT OPSÆTNING ---
st.set_page_config(
    page_title="Hækle Grid Pro",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
.main .block-container {padding: 0px !important;}
body { background: #1a252f; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

html_code = r"""
<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
  :root{
    --bg-dark:#2c3e50;
    --toolbar-bg:#ffffff;
    --btn-blue:#3498db;
    --btn-green:#27ae60;
    --btn-red:#e74c3c;
    --toolbar-h:64px;
  }

  *{box-sizing:border-box;}
  body{
    margin:0;
    font-family:-apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif;
    background:var(--bg-dark);
    height:100vh;
    overflow:hidden;
    touch-action:none;
  }

  /* === KOMPAKT TOPBAR === */
  .toolbar{
    position:fixed;top:0;left:0;right:0;
    background:var(--toolbar-bg);
    z-index:1000;
    box-shadow:0 6px 18px rgba(0,0,0,0.25);
  }
  .topbar{
    display:flex;align-items:center;gap:8px;padding:8px 10px;
  }
  .spacer{flex:1;}

  button,select,input{
    height:42px;border-radius:10px;border:1px solid #cfd4da;
    font-size:14px;font-weight:700;cursor:pointer;background:#fff;
    -webkit-tap-highlight-color:transparent;
  }
  button:active{transform:translateY(1px);}

  .btn-icon{
    width:44px;display:flex;align-items:center;justify-content:center;font-size:18px;
  }
  .btn-text{
    padding:0 12px;display:flex;align-items:center;gap:8px;white-space:nowrap;
  }
  .btn-blue{background:var(--btn-blue);color:#fff;border:none;}
  .btn-green{background:var(--btn-green);color:#fff;border:none;}
  .btn-red{background:var(--btn-red);color:#fff;border:none;}
  .active-tool{background:#f1c40f !important;color:#000 !important;}

  .mode{min-width:130px;max-width:220px;}

  /* Farvevælger-knap */
  .color-btn{
    width:44px;height:42px;border-radius:10px;border:2px solid #adb5bd;
    cursor:pointer;padding:0;position:relative;
  }
  .color-btn-inner{
    width:100%;height:100%;border-radius:8px;
  }
  #colorInput{
    position:absolute;opacity:0;width:100%;height:100%;top:0;left:0;cursor:pointer;
    border:none;padding:0;
  }

  /* === FOLD-UD MENU PANEL === */
  .panel-backdrop{
    position:fixed;inset:0;background:rgba(0,0,0,0.45);display:none;z-index:1500;
  }
  .panel{
    position:fixed;top:56px;left:10px;right:10px;
    background:#fff;border-radius:14px;
    box-shadow:0 18px 60px rgba(0,0,0,0.35);
    padding:12px;display:none;z-index:1600;
    max-height:calc(100vh - 70px);overflow-y:auto;
  }
  .panel h3{margin:0 0 10px;font-size:16px;}
  .panel-row{
    display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px;
  }
  .group{
    display:flex;gap:8px;align-items:center;flex-wrap:wrap;
    background:#f1f3f5;border:1px solid #dee2e6;padding:8px 10px;border-radius:12px;
  }
  .size-input{width:90px;text-align:center;font-size:16px;}
  #imgInput{display:none;}

  /* Farvepalet i menuen */
  .palette{display:flex;gap:6px;flex-wrap:wrap;}
  .swatch{
    width:32px;height:32px;border-radius:8px;border:2px solid #dee2e6;
    cursor:pointer;transition:transform 0.1s;
  }
  .swatch:hover{transform:scale(1.15);}
  .swatch.sel{border-color:#000;box-shadow:0 0 0 2px #f1c40f;}

  /* === VIEWPORT === */
  .viewport{
    width:100vw;height:100vh;overflow:auto;
    padding-top:calc(var(--toolbar-h) + 6px);
    background:#34495e;-webkit-overflow-scrolling:touch;
  }
  canvas{
    background:#fff;transform-origin:0 0;display:block;
    box-shadow:0 0 30px rgba(0,0,0,0.55);touch-action:none;
  }

  /* === HJÆLP MODAL === */
  .help-backdrop{
    position:fixed;inset:0;background:rgba(0,0,0,0.45);
    display:none;align-items:center;justify-content:center;z-index:2000;padding:16px;
  }
  .help{
    width:min(720px,96vw);max-height:min(80vh,720px);overflow:auto;
    background:#fff;border-radius:16px;
    box-shadow:0 18px 60px rgba(0,0,0,0.5);padding:14px 14px 10px;
  }
  .help h2{margin:0 0 6px;font-size:18px;}
  .help p,.help li{font-size:14px;line-height:1.35;}
  .pill{
    display:inline-block;padding:2px 8px;border-radius:999px;
    background:#f1f3f5;border:1px solid #dee2e6;font-weight:800;font-size:12px;
  }

  /* === MOBIL OPTIMERING === */
  @media(max-width:560px){
    :root{--toolbar-h:56px;}
    .topbar{padding:7px 8px;gap:6px;}
    button,select,input{height:40px;font-size:13px;}
    .mode{min-width:120px;max-width:160px;}
    .btn-text{padding:0 10px;}
    .panel{top:52px;}
    .swatch{width:28px;height:28px;}
  }
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
  <div class="topbar">
    <button class="btn-text" onclick="togglePanel()" title="Åbn/luk menu">☰ Menu</button>

    <select id="mode" class="mode" title="Vælg værktøj" onchange="onModeChange()">
      <option value="fill">⬛ Fyld</option>
      <option value="X">❌ X-maske</option>
      <option value="O">⭕ O-maske</option>
      <option value="symbol">✿ Symbol</option>
      <option value="line">╲ Streg</option>
      <option value="erase">🧽 Viskelæder</option>
    </select>

    <!-- Farvevælger i topbar -->
    <div class="color-btn" id="colorBtnWrap" title="Vælg farve">
      <div class="color-btn-inner" id="colorBtnInner" style="background:#000000;"></div>
      <input type="color" id="colorInput" value="#000000">
    </div>

    <button class="btn-icon" onclick="undo()" title="Fortryd (Ctrl/Cmd+Z)">↩️</button>
    <button class="btn-icon" onclick="redo()" title="Gendan (Ctrl/Cmd+Y)">↪️</button>

    <button id="panBtn" class="btn-icon" onclick="togglePan()" title="Pan-lås">✋</button>
    <button class="btn-icon" onclick="zoomAtCenter(1.15)" title="Zoom ind">➕</button>
    <button class="btn-icon" onclick="zoomAtCenter(1/1.15)" title="Zoom ud">➖</button>

    <div class="spacer"></div>

    <button class="btn-text btn-green" onclick="exportPDF()" title="Gem som PDF">📄 PDF</button>
    <button class="btn-icon" onclick="toggleHelp()" title="Brugsguide">❓</button>
  </div>
</div>

<!-- Fold-ud panel -->
<div class="panel-backdrop" id="panelBackdrop" onclick="closePanelFromBackdrop(event)"></div>
<div class="panel" id="panel">
  <div class="panel-row" style="justify-content:space-between;">
    <h3>Menu</h3>
    <button class="btn-icon" onclick="togglePanel()" title="Luk">✖️</button>
  </div>

  <!-- Størrelse -->
  <div class="panel-row">
    <div class="group" aria-label="Størrelse på grid">
      <label style="font-weight:900;">Størrelse:</label>
      <input type="number" id="rows" value="114" class="size-input" inputmode="numeric" title="Rækker"> Rk
      <span style="font-weight:900;">×</span>
      <input type="number" id="cols" value="23" class="size-input" inputmode="numeric" title="Kolonner"> Kol
      <button class="btn-text" onclick="resizeGrid()" style="background:#d9dde1;">Anvend</button>
    </div>
  </div>

  <!-- Specialsymbol -->
  <div class="panel-row">
    <div class="group" aria-label="Specialsymbol">
      <label style="font-weight:900;">Symbol:</label>
      <select id="symbolSelect" style="min-width:100px;" title="Vælg specialsymbol">
        <option value="▪">▪ Firkant</option>
        <option value="✿">✿ Blomst</option>
        <option value="↘">↘ Pil ned-højre</option>
        <option value="★">★ Stjerne</option>
        <option value="♥">♥ Hjerte</option>
        <option value="●">● Cirkel</option>
        <option value="▲">▲ Trekant</option>
        <option value="◆">◆ Diamant</option>
        <option value="↗">↗ Pil op-højre</option>
        <option value="∞">∞ Uendelig</option>
      </select>
    </div>
  </div>

  <!-- Farvepalet -->
  <div class="panel-row">
    <div class="group" aria-label="Farvepalet">
      <label style="font-weight:900;">Farve:</label>
      <div class="palette" id="palette"></div>
    </div>
  </div>

  <!-- PDF-kvalitet -->
  <div class="panel-row">
    <div class="group" aria-label="PDF-kvalitet">
      <label style="font-weight:900;">PDF-kvalitet:</label>
      <select id="pdfPreset" title="Kvalitet vs. filstørrelse">
        <option value="normal" selected>Normal (anbefalet)</option>
        <option value="print">Print (skarpere)</option>
        <option value="small">Lille fil</option>
      </select>
    </div>
  </div>

  <!-- Import / eksport -->
  <div class="panel-row">
    <div class="group" aria-label="Import og eksport">
      <button class="btn-text btn-blue" onclick="document.getElementById('imgInput').click()" title="Importér billede til grid">📥 Hent foto</button>
      <input type="file" id="imgInput" accept="image/*">
      <button class="btn-text" onclick="exportPNG()" title="Gem som PNG">🖼️ PNG</button>
      <button class="btn-text btn-red" onclick="resetCanvas()" title="Slet alt">🗑️ Slet alt</button>
    </div>
  </div>

  <!-- Tip -->
  <div class="panel-row">
    <div class="group" aria-label="Tips">
      <span class="pill">Tip</span>
      <span style="font-size:13px;font-weight:800;">
        Mobil: 1 finger tegner • 2 fingre flytter • knib for zoom
      </span>
    </div>
  </div>
</div>

<div class="viewport" id="vp">
  <canvas id="c"></canvas>
</div>

<!-- Hjælp-dialog -->
<div class="help-backdrop" id="helpBackdrop" onclick="closeHelpFromBackdrop(event)">
  <div class="help" role="dialog" aria-modal="true" aria-label="Brugsguide">
    <h2>Brugsguide</h2>
    <p>
      Brug griddet til <b>hækling</b>, <b>strik</b>, <b>korssting</b>, <b>broderi</b>, <b>perleplader</b> og andre mønstre.
    </p>
    <ul>
      <li><span class="pill">1</span> Vælg værktøj: <b>Fyld</b>, <b>X</b>, <b>O</b>, <b>Symbol</b>, <b>Streg</b> eller <b>Viskelæder</b>.</li>
      <li><span class="pill">2</span> Vælg <b>farve</b> med farveknappen i topbaren eller paletten i menuen.</li>
      <li><span class="pill">3</span> Tryk eller træk på griddet for at tegne.</li>
      <li><span class="pill">4</span> <b>Streg</b>: Klik startcelle, klik slutcelle → linje tegnes mellem dem.</li>
      <li><span class="pill">5</span> Flyt/zoom:
        <ul>
          <li><b>Mobil/Tablet:</b> 2 fingre = flyt, knib = zoom.</li>
          <li><b>Desktop:</b> Hold <b>Mellemrum</b> nede og træk for at flytte.</li>
        </ul>
      </li>
      <li><span class="pill">6</span> ↩️/↪️ fortryd/gendan (desktop: Ctrl/Cmd+Z / Ctrl/Cmd+Y).</li>
      <li><span class="pill">7</span> PDF: "Normal" er bedst til deling. "Print" er skarpere.</li>
    </ul>
    <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:10px;">
      <button onclick="toggleHelp()" class="btn-text" style="background:#d9dde1;">Luk</button>
    </div>
  </div>
</div>

<script>
  /* =====================================================
     Hækle Grid Pro – Komplet JavaScript
     ===================================================== */

  // --- GRID TILSTAND ---
  let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 45;

  /*
   * gridData[r][c] kan være:
   *   null                        – tom celle
   *   "X" / "O"                   – baglæns-kompatibilitet (sort)
   *   "fill"                      – baglæns-kompatibilitet (sort fyld)
   *   { type:"fill", color:"#…" } – farvet fyld
   *   { type:"X", color:"#…" }    – X med farve
   *   { type:"O", color:"#…" }    – O med farve
   *   { type:"symbol", symbol:"✿", color:"#…" } – specialsymbol
   */
  let gridData = [];

  // Linjer tegnet via stregværktøjet: [{r1,c1,r2,c2,color}]
  let lineData = [];

  let history = [], redoStack = [];

  let isPanLocked = false;
  let scale = 1.0;
  const minScale = 0.2, maxScale = 4.0;

  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const vp = document.getElementById('vp');

  // Aktiv farve
  let currentColor = '#000000';

  // Stregværktøj: startcelle
  let lineStart = null;

  // Pointer tracking
  const pointers = new Map();
  let drawing = false;
  let lastCell = { r: -1, c: -1 };

  // --- FARVEPALET ---
  const paletFarver = [
    '#000000','#ffffff','#e74c3c','#e67e22','#f1c40f','#2ecc71',
    '#1abc9c','#3498db','#9b59b6','#e91e63','#795548','#607d8b',
    '#c0392b','#d35400','#f39c12','#27ae60','#16a085','#2980b9',
    '#8e44ad','#fd79a8','#a1887f','#b0bec5',
  ];

  function byggPalet(){
    const pal = document.getElementById('palette');
    pal.innerHTML = '';
    paletFarver.forEach(f => {
      const el = document.createElement('div');
      el.className = 'swatch' + (f === currentColor ? ' sel' : '');
      el.style.background = f;
      if(f === '#ffffff') el.style.borderColor = '#adb5bd';
      el.onclick = () => vælgFarve(f);
      pal.appendChild(el);
    });
  }

  function vælgFarve(farve){
    currentColor = farve;
    document.getElementById('colorInput').value = farve;
    document.getElementById('colorBtnInner').style.background = farve;
    opdaterPaletMarkering();
  }

  function opdaterPaletMarkering(){
    document.querySelectorAll('.swatch').forEach(s => {
      const bg = rgbToHex(getComputedStyle(s).backgroundColor);
      s.classList.toggle('sel', bg === currentColor.toLowerCase());
    });
  }

  function rgbToHex(rgb){
    const m = rgb.match(/\d+/g);
    if(!m||m.length<3) return rgb;
    return '#' + m.slice(0,3).map(v => parseInt(v).toString(16).padStart(2,'0')).join('');
  }

  // Farve-input i topbar
  document.getElementById('colorInput').addEventListener('input', function(e){
    vælgFarve(e.target.value);
  });

  function onModeChange(){
    lineStart = null; // Nulstil stregværktøj ved skift
  }

  // --- PANEL / HJÆLP ---
  function togglePanel(){
    const panel = document.getElementById('panel');
    const bd = document.getElementById('panelBackdrop');
    const isOpen = panel.style.display === 'block';
    panel.style.display = isOpen ? 'none' : 'block';
    bd.style.display = isOpen ? 'none' : 'block';
    measureToolbarHeight();
  }
  function closePanelFromBackdrop(e){
    if(e.target && e.target.id === 'panelBackdrop') togglePanel();
  }

  function toggleHelp(){
    const bd = document.getElementById('helpBackdrop');
    const isOpen = bd.style.display === 'flex';
    bd.style.display = isOpen ? 'none' : 'flex';
  }
  function closeHelpFromBackdrop(e){
    if(e.target && e.target.id === 'helpBackdrop') toggleHelp();
  }

  function clamp(v,a,b){return Math.max(a,Math.min(b,v));}

  function setScale(newScale){
    scale = clamp(newScale, minScale, maxScale);
    canvas.style.transform = 'scale(' + scale + ')';
    localStorage.setItem('haekleGridScale', String(scale));
  }

  function measureToolbarHeight(){
    const tb = document.getElementById('toolbar');
    const h = tb.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--toolbar-h', Math.ceil(h) + 'px');
  }
  window.addEventListener('resize', measureToolbarHeight);

  // --- AUTO-SAVE & INIT ---
  function init(){
    const saved = localStorage.getItem('haekleGridData');
    const sRows = localStorage.getItem('haekleGridRows');
    const sCols = localStorage.getItem('haekleGridCols');
    const sScale = localStorage.getItem('haekleGridScale');
    const sLines = localStorage.getItem('haekleGridLines');

    if(saved && sRows && sCols){
      gridData = JSON.parse(saved);
      ROWS = parseInt(sRows, 10);
      COLS = parseInt(sCols, 10);
      document.getElementById('rows').value = ROWS;
      document.getElementById('cols').value = COLS;
    } else {
      gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
    }

    if(sLines){
      lineData = JSON.parse(sLines);
    }

    updateCanvas();
    setScale(sScale ? parseFloat(sScale) : 1.0);
    measureToolbarHeight();
    byggPalet();
  }

  function autoSave(){
    localStorage.setItem('haekleGridData', JSON.stringify(gridData));
    localStorage.setItem('haekleGridRows', ROWS);
    localStorage.setItem('haekleGridCols', COLS);
    localStorage.setItem('haekleGridLines', JSON.stringify(lineData));
  }

  // --- RESIZE ---
  function resizeGrid(){
    const nR = Math.max(1, parseInt(document.getElementById('rows').value || "1", 10));
    const nC = Math.max(1, parseInt(document.getElementById('cols').value || "1", 10));
    saveHistory();

    const old = JSON.parse(JSON.stringify(gridData));
    gridData = Array(nR).fill().map(() => Array(nC).fill(null));

    for(let r=0;r<Math.min(ROWS,nR);r++){
      for(let c=0;c<Math.min(COLS,nC);c++){
        gridData[r][c] = old[r][c];
      }
    }

    // Fjern linjer der er udenfor det nye grid
    lineData = lineData.filter(l =>
      l.r1 < nR && l.c1 < nC && l.r2 < nR && l.c2 < nC
    );

    ROWS = nR; COLS = nC;
    updateCanvas();
    autoSave();
  }

  function updateCanvas(){
    canvas.width = (COLS * SIZE) + OFFSET;
    canvas.height = (ROWS * SIZE) + OFFSET;
    draw();
  }

  // --- HJÆLPEFUNKTIONER TIL CELLEDATA ---
  function cellType(cell){
    if(!cell) return null;
    if(typeof cell === 'string') return cell; // "fill", "X", "O"
    return cell.type || null;
  }

  function cellColor(cell){
    if(!cell) return '#000000';
    if(typeof cell === 'string') return '#000000';
    return cell.color || '#000000';
  }

  function cellSymbol(cell){
    if(!cell) return '';
    if(typeof cell === 'object' && cell.symbol) return cell.symbol;
    return '';
  }

  // --- TEGN PÅ CANVAS ---
  function drawOnContext(tCtx, s, off, isExport){
    const margin = isExport ? 40 : 0;
    tCtx.fillStyle = "white";
    tCtx.fillRect(0,0,tCtx.canvas.width,tCtx.canvas.height);

    // Gridlinjer + nummerering
    for(let i=0;i<=COLS;i++){
      const x = i*s + off + margin;
      tCtx.beginPath();
      tCtx.strokeStyle = (i%10===0) ? "#000" : (i%5===0 ? "#888" : "#ddd");
      tCtx.lineWidth = (i%5===0) ? 1.5 : 0.8;
      tCtx.moveTo(x, off+margin);
      tCtx.lineTo(x, (ROWS*s)+off+margin);
      tCtx.stroke();
      if(i<COLS && ((i+1===1)||((i+1)%5===0))){
        tCtx.font = "bold 12px Arial";
        tCtx.fillStyle = "#000";
        tCtx.textAlign = "center";
        tCtx.fillText(i+1, x + s/2, off + margin - 12);
      }
    }

    for(let j=0;j<=ROWS;j++){
      const y = j*s + off + margin;
      tCtx.beginPath();
      tCtx.strokeStyle = (j%10===0) ? "#000" : (j%5===0 ? "#888" : "#ddd");
      tCtx.lineWidth = (j%5===0) ? 1.5 : 0.8;
      tCtx.moveTo(off+margin, y);
      tCtx.lineTo((COLS*s)+off+margin, y);
      tCtx.stroke();
      if(j<ROWS && ((j+1===1)||((j+1)%5===0))){
        tCtx.font = "bold 12px Arial";
        tCtx.fillStyle = "#000";
        tCtx.textAlign = "right";
        tCtx.fillText(j+1, off + margin - 10, y + s/1.5);
      }
    }

    // Celleindhold
    tCtx.textAlign = "center";
    for(let r=0;r<ROWS;r++){
      for(let c=0;c<COLS;c++){
        const cell = gridData[r][c];
        if(!cell) continue;
        const x = c*s + off + margin;
        const y = r*s + off + margin;
        const t = cellType(cell);
        const col = cellColor(cell);

        if(t === 'fill'){
          tCtx.fillStyle = col;
          tCtx.fillRect(x+1, y+1, s-1, s-1);
        } else if(t === 'symbol'){
          tCtx.fillStyle = col;
          tCtx.font = 'bold ' + (s*0.7) + 'px Arial';
          tCtx.fillText(cellSymbol(cell), x+s/2, y+s/1.3);
        } else {
          // X, O eller andre tekst-symboler
          tCtx.fillStyle = col;
          tCtx.font = 'bold ' + (s*0.7) + 'px Arial';
          const txt = (typeof cell === 'string') ? cell : t;
          tCtx.fillText(txt, x+s/2, y+s/1.3);
        }
      }
    }

    // Tegn linjer
    if(lineData.length > 0){
      for(const ln of lineData){
        const x1 = ln.c1*s + off + margin + s/2;
        const y1 = ln.r1*s + off + margin + s/2;
        const x2 = ln.c2*s + off + margin + s/2;
        const y2 = ln.r2*s + off + margin + s/2;
        tCtx.beginPath();
        tCtx.strokeStyle = ln.color || '#000000';
        tCtx.lineWidth = Math.max(2, s * 0.12);
        tCtx.lineCap = 'round';
        tCtx.moveTo(x1, y1);
        tCtx.lineTo(x2, y2);
        tCtx.stroke();
      }
    }

    // Vis streg-startpunkt (kun live view)
    if(!isExport && lineStart){
      const sx = lineStart.c*s + off + s/2;
      const sy = lineStart.r*s + off + s/2;
      tCtx.beginPath();
      tCtx.arc(sx, sy, s*0.25, 0, Math.PI*2);
      tCtx.fillStyle = 'rgba(52,152,219,0.5)';
      tCtx.fill();
    }
  }

  function draw(){ drawOnContext(ctx, SIZE, OFFSET, false); }

  // --- UNDO / REDO ---
  function saveHistory(){
    history.push(JSON.stringify({g:gridData,l:lineData}));
    if(history.length>60) history.shift();
    redoStack = [];
  }
  function undo(){
    if(history.length){
      redoStack.push(JSON.stringify({g:gridData,l:lineData}));
      const snap = JSON.parse(history.pop());
      gridData = snap.g; lineData = snap.l || [];
      draw(); autoSave();
    }
  }
  function redo(){
    if(redoStack.length){
      history.push(JSON.stringify({g:gridData,l:lineData}));
      const snap = JSON.parse(redoStack.pop());
      gridData = snap.g; lineData = snap.l || [];
      draw(); autoSave();
    }
  }

  // --- HIT TEST ---
  function getCellFromClient(clientX, clientY){
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left) / scale;
    const y = (clientY - rect.top) / scale;
    const c = Math.floor((x - OFFSET) / SIZE);
    const r = Math.floor((y - OFFSET) / SIZE);
    return {r, c};
  }

  function makeCellValue(){
    const m = document.getElementById('mode').value;
    if(m === 'erase') return null;
    if(m === 'fill')  return {type:'fill', color:currentColor};
    if(m === 'X')     return {type:'X', color:currentColor};
    if(m === 'O')     return {type:'O', color:currentColor};
    if(m === 'symbol'){
      const sym = document.getElementById('symbolSelect').value;
      return {type:'symbol', symbol:sym, color:currentColor};
    }
    return null;
  }

  function cellsEqual(a, b){
    if(a === b) return true;
    if(!a || !b) return false;
    if(typeof a === 'string' || typeof b === 'string') return a === b;
    return a.type === b.type && a.color === b.color &&
           (a.symbol || '') === (b.symbol || '');
  }

  function applyCell(r, c){
    if(r<0||r>=ROWS||c<0||c>=COLS) return;
    const next = makeCellValue();
    if(cellsEqual(gridData[r][c], next)){
      gridData[r][c] = null;
    } else {
      gridData[r][c] = next;
    }
  }

  function applyCellIfNew(r, c){
    if(r===lastCell.r && c===lastCell.c) return;
    lastCell = {r, c};
    applyCell(r, c);
  }

  // --- STREGVÆRKTØJ (line tool) ---
  // Bresenham's linje-algortime til at finde alle celler på linjen
  function bresenham(r1, c1, r2, c2){
    const cells = [];
    let dr = Math.abs(r2-r1), dc = Math.abs(c2-c1);
    let sr = r1<r2 ? 1 : -1, sc = c1<c2 ? 1 : -1;
    let err = dc - dr;
    let cr = r1, cc = c1;
    while(true){
      cells.push({r:cr, c:cc});
      if(cr===r2 && cc===c2) break;
      const e2 = 2*err;
      if(e2 > -dr){ err -= dr; cc += sc; }
      if(e2 < dc){ err += dc; cr += sr; }
    }
    return cells;
  }

  function handleLineClick(r, c){
    if(!lineStart){
      lineStart = {r, c};
      draw(); // Vis startpunkt
    } else {
      saveHistory();
      lineData.push({
        r1: lineStart.r, c1: lineStart.c,
        r2: r, c2: c,
        color: currentColor
      });
      lineStart = null;
      draw(); autoSave();
    }
  }

  // --- PAN / ZOOM ---
  function togglePan(){
    isPanLocked = !isPanLocked;
    document.getElementById('panBtn').classList.toggle('active-tool', isPanLocked);
  }

  function zoomAtCenter(mult){
    const beforeScale = scale;
    const newScale = clamp(scale * mult, minScale, maxScale);
    const vpRect = vp.getBoundingClientRect();
    const centerX = vpRect.left + vpRect.width/2;
    const centerY = vpRect.top + vpRect.height/2;
    const rect = canvas.getBoundingClientRect();
    const canvasX = (centerX - rect.left + vp.scrollLeft) / beforeScale;
    const canvasY = (centerY - rect.top + vp.scrollTop) / beforeScale;
    setScale(newScale);
    vp.scrollLeft = canvasX * newScale - (vpRect.width/2);
    vp.scrollTop  = canvasY * newScale - (vpRect.height/2);
  }

  // --- POINTER EVENTS ---
  let pinchStartDist = 0;
  let pinchStartScale = 1;
  let lastPanMid = null;
  let lastSinglePointerPos = null;

  function distance(a,b){
    const dx=a.x-b.x, dy=a.y-b.y;
    return Math.sqrt(dx*dx+dy*dy);
  }
  function midpoint(a,b){
    return {x:(a.x+b.x)/2, y:(a.y+b.y)/2};
  }

  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});

    if(pointers.size === 2){
      const pts = Array.from(pointers.values());
      pinchStartDist = distance(pts[0], pts[1]);
      pinchStartScale = scale;
      lastPanMid = midpoint(pts[0], pts[1]);
      drawing = false;
      lastCell = {r:-1, c:-1};
      return;
    }

    const shouldPan = isPanLocked || spaceDown;
    if(shouldPan){
      drawing = false;
      lastSinglePointerPos = {x:e.clientX, y:e.clientY};
      return;
    }

    const cell = getCellFromClient(e.clientX, e.clientY);
    if(cell.r>=0 && cell.c>=0 && cell.r<ROWS && cell.c<COLS){
      const m = document.getElementById('mode').value;
      if(m === 'line'){
        handleLineClick(cell.r, cell.c);
        return;
      }
      saveHistory();
      drawing = true;
      lastCell = {r:-1, c:-1};
      applyCellIfNew(cell.r, cell.c);
      draw(); autoSave();
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    if(!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});

    if(pointers.size === 2){
      const pts = Array.from(pointers.values());
      const d = distance(pts[0], pts[1]);
      const mid = midpoint(pts[0], pts[1]);

      if(pinchStartDist > 0){
        const factor = d / pinchStartDist;
        const newScale = clamp(pinchStartScale * factor, minScale, maxScale);
        const prevScale = scale;
        const vpRect = vp.getBoundingClientRect();
        const mx = (mid.x - vpRect.left) + vp.scrollLeft;
        const my = (mid.y - vpRect.top) + vp.scrollTop;
        const canvasX = mx / prevScale;
        const canvasY = my / prevScale;
        setScale(newScale);
        vp.scrollLeft = canvasX * newScale - (mid.x - vpRect.left);
        vp.scrollTop  = canvasY * newScale - (mid.y - vpRect.top);
      }

      if(lastPanMid){
        const dx = mid.x - lastPanMid.x;
        const dy = mid.y - lastPanMid.y;
        vp.scrollLeft -= dx;
        vp.scrollTop  -= dy;
      }
      lastPanMid = mid;
      return;
    }

    if(isPanLocked || spaceDown){
      const prev = lastSinglePointerPos;
      const cur = {x:e.clientX, y:e.clientY};
      if(prev){
        vp.scrollLeft -= (cur.x - prev.x);
        vp.scrollTop  -= (cur.y - prev.y);
      }
      lastSinglePointerPos = cur;
      return;
    }

    if(drawing){
      const cell = getCellFromClient(e.clientX, e.clientY);
      if(cell.r>=0 && cell.c>=0 && cell.r<ROWS && cell.c<COLS){
        applyCellIfNew(cell.r, cell.c);
        draw(); autoSave();
      }
    }
  });

  function endPointer(e){
    pointers.delete(e.pointerId);
    if(pointers.size < 2){
      pinchStartDist = 0;
      pinchStartScale = scale;
      lastPanMid = null;
    }
    if(pointers.size === 0){
      drawing = false;
      lastCell = {r:-1, c:-1};
      lastSinglePointerPos = null;
    }
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  // --- KEYBOARD ---
  let spaceDown = false;
  window.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();
    if(key === ' '){ spaceDown = true; e.preventDefault(); }
    const isMod = e.ctrlKey || e.metaKey;
    if(isMod && key === 'z' && !e.shiftKey){ e.preventDefault(); undo(); }
    if(isMod && (key === 'y' || (key === 'z' && e.shiftKey))){ e.preventDefault(); redo(); }
    if(key === '+' || key === '='){ e.preventDefault(); zoomAtCenter(1.15); }
    if(key === '-' || key === '_'){ e.preventDefault(); zoomAtCenter(1/1.15); }
    if(key === 'escape'){ lineStart = null; draw(); }
  });
  window.addEventListener('keyup', (e) => { if(e.key === ' ') spaceDown = false; });

  // --- EKSPORT PNG ---
  function exportPNG(){
    const url = canvas.toDataURL("image/png");
    const a = document.createElement('a');
    a.download = "haekle-design.png";
    a.href = url;
    a.click();
  }

  // --- EKSPORT PDF (A4, multi-page, kvalitetsvalg) ---
  function getPdfSettings(){
    const preset = document.getElementById('pdfPreset').value;
    if(preset === 'print')  return {exportScale:1.65, jpegQuality:0.82, render:"SLOW"};
    if(preset === 'small')  return {exportScale:1.20, jpegQuality:0.65, render:"FAST"};
    return                         {exportScale:1.45, jpegQuality:0.78, render:"SLOW"};
  }

  function canvasToJpegDataUrl(sourceCanvas, quality){
    return sourceCanvas.toDataURL("image/jpeg", quality);
  }

  async function exportPDF(){
    const {jsPDF} = window.jspdf;
    const {exportScale, jpegQuality, render} = getPdfSettings();
    const marginMm = 8;
    const pdf = new jsPDF({orientation:"p", unit:"mm", format:"a4", compress:true});
    const pageW=210, pageH=297;
    const usableW = pageW - marginMm*2;
    const usableH = pageH - marginMm*2;

    const tempCanvas = document.createElement("canvas");
    tempCanvas.width  = Math.ceil(((COLS*SIZE)+OFFSET+80)*exportScale);
    tempCanvas.height = Math.ceil(((ROWS*SIZE)+OFFSET+80)*exportScale);
    const tCtx = tempCanvas.getContext("2d");
    tCtx.scale(exportScale, exportScale);
    drawOnContext(tCtx, SIZE, OFFSET, true);

    const pxPerMm = tempCanvas.width / usableW;
    const pagePxH = Math.floor(usableH * pxPerMm);
    const sliceCanvas = document.createElement("canvas");
    sliceCanvas.width = tempCanvas.width;
    sliceCanvas.height = pagePxH;
    const sCtx = sliceCanvas.getContext("2d");
    const totalPages = Math.ceil(tempCanvas.height / pagePxH);

    for(let page=0; page<totalPages; page++){
      const sy = page * pagePxH;
      const sh = Math.min(pagePxH, tempCanvas.height - sy);
      if(sliceCanvas.height !== sh) sliceCanvas.height = sh;
      sCtx.fillStyle = "#ffffff";
      sCtx.fillRect(0,0,sliceCanvas.width,sliceCanvas.height);
      sCtx.drawImage(tempCanvas, 0,sy,tempCanvas.width,sh, 0,0,tempCanvas.width,sh);
      const imgData = canvasToJpegDataUrl(sliceCanvas, jpegQuality);
      if(page > 0) pdf.addPage();
      const imgH_mm = (sh / pxPerMm);
      pdf.addImage(imgData,"JPEG",marginMm,marginMm,usableW,imgH_mm,undefined,render);
    }

    pdf.save("haekle-moenster.pdf");
  }

  // --- IMPORT FOTO ---
  document.getElementById('imgInput').onchange = function(e){
    const file = e.target.files && e.target.files[0];
    if(!file) return;

    const reader = new FileReader();
    reader.onload = function(event){
      const img = new Image();
      img.onload = function(){
        saveHistory();
        const tCanvas = document.createElement('canvas');
        tCanvas.width = COLS; tCanvas.height = ROWS;
        const tCtx = tCanvas.getContext('2d');
        tCtx.drawImage(img, 0, 0, COLS, ROWS);
        const pix = tCtx.getImageData(0,0,COLS,ROWS).data;
        for(let i=0;i<pix.length;i+=4){
          const avg = (pix[i]+pix[i+1]+pix[i+2])/3;
          const r = Math.floor((i/4)/COLS);
          const c = (i/4)%COLS;
          gridData[r][c] = avg < 125 ? {type:'fill',color:'#000000'} : null;
        }
        draw(); autoSave();
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = "";
    const panel = document.getElementById('panel');
    if(panel.style.display === 'block') togglePanel();
  };

  function resetCanvas(){
    if(confirm("Vil du slette ALT?")){
      localStorage.clear();
      location.reload();
    }
  }

  init();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
