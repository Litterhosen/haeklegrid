import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v7 (Mobilmenu + bedre PDF)", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
.main .block-container {padding: 0px !important;}
body { background: #1a252f; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

html_code = r"""
<!DOCTYPE html>
<html>
<head>
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

  * { box-sizing: border-box; }
  body{
    margin:0;
    font-family:-apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif;
    background:var(--bg-dark);
    height:100vh;
    overflow:hidden;
    touch-action:none;
  }

  /* === KOMPAKT TOPBAR (ALTID) === */
  .toolbar{
    position:fixed; top:0; left:0; right:0;
    background:var(--toolbar-bg);
    z-index:1000;
    box-shadow:0 6px 18px rgba(0,0,0,0.25);
  }

  .topbar{
    display:flex;
    align-items:center;
    gap:8px;
    padding:8px 10px;
  }

  .spacer{ flex:1; }

  button, select, input{
    height:42px;
    border-radius:10px;
    border:1px solid #cfd4da;
    font-size:14px;
    font-weight:700;
    cursor:pointer;
    background:#fff;
    -webkit-tap-highlight-color: transparent;
  }
  button:active{ transform: translateY(1px); }

  .btn-icon{
    width:44px;
    display:flex; align-items:center; justify-content:center;
    font-size:18px;
  }
  .btn-text{
    padding:0 12px;
    display:flex; align-items:center; gap:8px;
    white-space:nowrap;
  }
  .btn-blue{ background:var(--btn-blue); color:#fff; border:none; }
  .btn-green{ background:var(--btn-green); color:#fff; border:none; }
  .btn-red{ background:var(--btn-red); color:#fff; border:none; }
  .active-tool{ background:#f1c40f !important; color:#000 !important; }

  .mode{
    min-width: 170px;
    max-width: 240px;
  }

  /* === FOLD-UD MENU PANEL === */
  .panel-backdrop{
    position:fixed; inset:0;
    background:rgba(0,0,0,0.45);
    display:none;
    z-index:1500;
  }
  .panel{
    position:fixed;
    top:56px;
    left:10px; right:10px;
    background:#fff;
    border-radius:14px;
    box-shadow:0 18px 60px rgba(0,0,0,0.35);
    padding:12px;
    display:none;
    z-index:1600;
  }
  .panel h3{
    margin:0 0 10px;
    font-size:16px;
  }
  .panel-row{
    display:flex; gap:10px; align-items:center; flex-wrap:wrap;
    margin-bottom:10px;
  }
  .group{
    display:flex; gap:8px; align-items:center; flex-wrap:wrap;
    background:#f1f3f5;
    border:1px solid #dee2e6;
    padding:8px 10px;
    border-radius:12px;
  }
  .size-input{ width:90px; text-align:center; font-size:16px; }
  #imgInput{ display:none; }

  /* === VIEWPORT === */
  .viewport{
    width:100vw;
    height:100vh;
    overflow:auto;
    padding-top: calc(var(--toolbar-h) + 6px);
    background:#34495e;
    -webkit-overflow-scrolling:touch;
  }
  canvas{
    background:#fff;
    transform-origin:0 0;
    display:block;
    box-shadow:0 0 30px rgba(0,0,0,0.55);
    touch-action:none;
  }

  /* === HJÆLP MODAL === */
  .help-backdrop{
    position:fixed; inset:0;
    background:rgba(0,0,0,0.45);
    display:none;
    align-items:center; justify-content:center;
    z-index:2000;
    padding:16px;
  }
  .help{
    width:min(720px, 96vw);
    max-height:min(80vh, 720px);
    overflow:auto;
    background:#fff;
    border-radius:16px;
    box-shadow:0 18px 60px rgba(0,0,0,0.5);
    padding:14px 14px 10px;
  }
  .help h2{ margin:0 0 6px; font-size:18px; }
  .help p, .help li{ font-size:14px; line-height:1.35; }
  .pill{
    display:inline-block; padding:2px 8px; border-radius:999px;
    background:#f1f3f5; border:1px solid #dee2e6;
    font-weight:800; font-size:12px;
  }

  /* === MOBIL OPTIMERING === */
  @media (max-width: 560px){
    :root{ --toolbar-h: 56px; }
    .topbar{ padding:7px 8px; gap:6px; }
    button, select, input{ height:40px; font-size:13px; }
    .mode{ min-width: 150px; max-width: 170px; }
    .btn-text{ padding:0 10px; }
    .panel{ top:52px; }
  }
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
  <div class="topbar">
    <button class="btn-text" onclick="togglePanel()" title="Åbn/luk menu">☰ Menu</button>

    <select id="mode" class="mode" title="Vælg hvad du vil tegne">
      <option value="fill">⚫ Fyld (sort)</option>
      <option value="X">❌ X-maske</option>
      <option value="O">⭕ O-maske</option>
      <option value="erase">🧽 Viskelæder</option>
    </select>

    <button class="btn-icon" onclick="undo()" title="Fortryd (Ctrl/Cmd+Z)">↩️</button>
    <button class="btn-icon" onclick="redo()" title="Gendan (Ctrl/Cmd+Y)">↪️</button>

    <button id="panBtn" class="btn-icon" onclick="togglePan()" title="Pan-lås (2 fingre pan virker altid på touch)">✋</button>

    <button class="btn-icon" onclick="zoomAtCenter(1.15)" title="Zoom ind">➕</button>
    <button class="btn-icon" onclick="zoomAtCenter(1/1.15)" title="Zoom ud">➖</button>

    <div class="spacer"></div>

    <button class="btn-text btn-green" onclick="exportPDF()" title="Gem som PDF (A4, pladsoptimeret)">📄 PDF</button>
    <button class="btn-icon" onclick="toggleHelp()" title="Kort brugsguide">❓</button>
  </div>
</div>

<!-- Fold-ud panel -->
<div class="panel-backdrop" id="panelBackdrop" onclick="closePanelFromBackdrop(event)"></div>
<div class="panel" id="panel">
  <div class="panel-row" style="justify-content:space-between;">
    <h3>Menu</h3>
    <button class="btn-icon" onclick="togglePanel()" title="Luk">✖️</button>
  </div>

  <div class="panel-row">
    <div class="group" aria-label="Størrelse på grid">
      <label style="font-weight:900;">Størrelse:</label>
      <input type="number" id="rows" value="114" class="size-input" inputmode="numeric" title="Antal rækker"> Rækker
      <span style="font-weight:900;">×</span>
      <input type="number" id="cols" value="23" class="size-input" inputmode="numeric" title="Antal kolonner/masker"> Kolonner
      <button class="btn-text" onclick="resizeGrid()" style="background:#d9dde1;" title="Anvend ny størrelse">Anvend</button>
    </div>
  </div>

  <div class="panel-row">
    <div class="group" aria-label="Eksport indstillinger">
      <label style="font-weight:900;">PDF-kvalitet:</label>
      <select id="pdfPreset" title="Vælg balance mellem kvalitet og filstørrelse">
        <option value="normal" selected>Normal (anbefalet)</option>
        <option value="print">Print (skarpere)</option>
        <option value="small">Lille fil</option>
      </select>
      <span style="font-size:12px; font-weight:800; opacity:0.75;">A4-sider</span>
    </div>
  </div>

  <div class="panel-row">
    <div class="group" aria-label="Import og eksport">
      <button class="btn-text btn-blue" onclick="document.getElementById('imgInput').click()" title="Lav mønster ud fra et billede">📥 Hent foto</button>
      <input type="file" id="imgInput" accept="image/*">

      <button class="btn-text" onclick="exportPNG()" title="Gem som billede (PNG)">🖼️ PNG</button>
      <button class="btn-text btn-red" onclick="resetCanvas()" title="Slet alt på grid">🗑️ Slet alt</button>
    </div>
  </div>

  <div class="panel-row">
    <div class="group" aria-label="Hurtige tips">
      <span class="pill">Tip</span>
      <span style="font-size:13px; font-weight:800;">
        Mobil: 1 finger tegner • 2 fingre flytter • knib for zoom
      </span>
    </div>
  </div>
</div>

<div class="viewport" id="vp">
  <canvas id="c"></canvas>
</div>

<!-- Hjælp -->
<div class="help-backdrop" id="helpBackdrop" onclick="closeHelpFromBackdrop(event)">
  <div class="help" role="dialog" aria-modal="true" aria-label="Brugsguide">
    <h2>Brugsguide (hurtig)</h2>
    <p>
      Brug griddet til <b>hækling</b>, <b>strik</b>, <b>korssting</b>, <b>broderi</b>, <b>perleplader</b> og andre mønstre.
    </p>
    <ul>
      <li><span class="pill">1</span> Vælg værktøj: <b>Fyld</b>, <b>X</b>, <b>O</b> eller <b>Viskelæder</b>.</li>
      <li><span class="pill">2</span> Tryk eller træk på griddet for at tegne.</li>
      <li><span class="pill">3</span> Flyt/zoom:
        <ul>
          <li><b>Mobil/Tablet:</b> 2 fingre = flyt, knib = zoom.</li>
          <li><b>Desktop:</b> Hold <b>Mellemrum</b> nede og træk for at flytte.</li>
        </ul>
      </li>
      <li><span class="pill">4</span> ↩️/↪️ fortryd/gedan (desktop: Ctrl/Cmd+Z / Ctrl/Cmd+Y).</li>
      <li><span class="pill">5</span> PDF: “Normal” er bedst til deling. “Print” er skarpere.</li>
    </ul>
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:10px;">
      <button onclick="toggleHelp()" class="btn-text" style="background:#d9dde1;">Luk</button>
    </div>
  </div>
</div>

<script>
  // --- GRID STATE ---
  let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 45;
  let gridData = [], history = [], redoStack = [];

  let isPanLocked = false;
  let scale = 1.0;
  const minScale = 0.2, maxScale = 4.0;

  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const vp = document.getElementById('vp');

  // Pointer tracking
  const pointers = new Map();
  let drawing = false;
  let lastCell = { r: -1, c: -1 };

  // --- PANEL / HELP ---
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

  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

  function setScale(newScale){
    scale = clamp(newScale, minScale, maxScale);
    canvas.style.transform = `scale(${scale})`;
    localStorage.setItem('haekleGridScale', String(scale));
  }

  function measureToolbarHeight(){
    const tb = document.getElementById('toolbar');
    const h = tb.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--toolbar-h', `${Math.ceil(h)}px`);
  }
  window.addEventListener('resize', measureToolbarHeight);

  // --- AUTO-SAVE ---
  function init(){
    const saved = localStorage.getItem('haekleGridData');
    const sRows = localStorage.getItem('haekleGridRows');
    const sCols = localStorage.getItem('haekleGridCols');
    const sScale = localStorage.getItem('haekleGridScale');

    if(saved && sRows && sCols){
      gridData = JSON.parse(saved);
      ROWS = parseInt(sRows, 10);
      COLS = parseInt(sCols, 10);
      document.getElementById('rows').value = ROWS;
      document.getElementById('cols').value = COLS;
    } else {
      gridData = Array(ROWS).fill().map(() => Array(COLS).fill(null));
    }

    updateCanvas();
    setScale(sScale ? parseFloat(sScale) : 1.0);
    measureToolbarHeight();
  }

  function autoSave(){
    localStorage.setItem('haekleGridData', JSON.stringify(gridData));
    localStorage.setItem('haekleGridRows', ROWS);
    localStorage.setItem('haekleGridCols', COLS);
  }

  // --- RESIZE ---
  function resizeGrid(){
    const nR = Math.max(1, parseInt(document.getElementById('rows').value || "1", 10));
    const nC = Math.max(1, parseInt(document.getElementById('cols').value || "1", 10));
    saveHistory();

    const old = JSON.parse(JSON.stringify(gridData));
    gridData = Array(nR).fill().map(() => Array(nC).fill(null));

    for(let r=0; r<Math.min(ROWS, nR); r++){
      for(let c=0; c<Math.min(COLS, nC); c++){
        gridData[r][c] = old[r][c];
      }
    }

    ROWS = nR; COLS = nC;
    updateCanvas();
    autoSave();
  }

  function updateCanvas(){
    canvas.width = (COLS * SIZE) + OFFSET;
    canvas.height = (ROWS * SIZE) + OFFSET;
    draw();
  }

  // --- DRAW ---
  function drawOnContext(tCtx, s, off, isExport=false){
    const margin = isExport ? 40 : 0;
    tCtx.fillStyle = "white";
    tCtx.fillRect(0,0,tCtx.canvas.width,tCtx.canvas.height);

    // Grid lines + numbering
    for(let i=0;i<=COLS;i++){
      const x = i*s + off + margin;
      tCtx.beginPath();
      tCtx.strokeStyle = (i%10===0) ? "#000" : (i%5===0 ? "#888" : "#ddd");
      tCtx.lineWidth = (i%5===0) ? 1.5 : 0.8;
      tCtx.moveTo(x, off+margin);
      tCtx.lineTo(x, (ROWS*s)+off+margin);
      tCtx.stroke();

      if(i<COLS && ((i+1===1) || ((i+1)%5===0))){
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

      if(j<ROWS && ((j+1===1) || ((j+1)%5===0))){
        tCtx.font = "bold 12px Arial";
        tCtx.fillStyle = "#000";
        tCtx.textAlign = "right";
        tCtx.fillText(j+1, off + margin - 10, y + s/1.5);
      }
    }

    // Content
    tCtx.textAlign="center";
    for(let r=0;r<ROWS;r++){
      for(let c=0;c<COLS;c++){
        if(!gridData[r][c]) continue;
        const x = c*s + off + margin;
        const y = r*s + off + margin;

        if(gridData[r][c]==='fill'){
          tCtx.fillStyle="black";
          tCtx.fillRect(x+1,y+1,s-1,s-1);
        } else {
          tCtx.fillStyle="black";
          tCtx.font = `bold ${s*0.7}px Arial`;
          tCtx.fillText(gridData[r][c], x+s/2, y+s/1.3);
        }
      }
    }
  }

  function draw(){ drawOnContext(ctx, SIZE, OFFSET, false); }

  function saveHistory(){
    history.push(JSON.stringify(gridData));
    if(history.length>60) history.shift();
    redoStack = [];
  }
  function undo(){
    if(history.length){
      redoStack.push(JSON.stringify(gridData));
      gridData = JSON.parse(history.pop());
      draw(); autoSave();
    }
  }
  function redo(){
    if(redoStack.length){
      history.push(JSON.stringify(gridData));
      gridData = JSON.parse(redoStack.pop());
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
    return { r, c };
  }

  function applyCell(r, c){
    if(r<0 || r>=ROWS || c<0 || c>=COLS) return;
    const m = document.getElementById('mode').value;
    const next = (m === 'erase') ? null : m;
    gridData[r][c] = (gridData[r][c] === next) ? null : next;
  }

  function applyCellIfNew(r, c){
    if(r===lastCell.r && c===lastCell.c) return;
    lastCell = { r, c };
    applyCell(r, c);
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

  // --- POINTER: DRAW + TWO-FINGER PAN + PINCH ---
  let pinchStartDist = 0;
  let pinchStartScale = 1;
  let lastPanMid = null;
  let lastSinglePointerPos = null;

  function distance(a,b){
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    return Math.sqrt(dx*dx + dy*dy);
  }
  function midpoint(a,b){
    return { x:(a.x+b.x)/2, y:(a.y+b.y)/2 };
  }

  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

    if(pointers.size === 2){
      const pts = Array.from(pointers.values());
      pinchStartDist = distance(pts[0], pts[1]);
      pinchStartScale = scale;
      lastPanMid = midpoint(pts[0], pts[1]);
      drawing = false;
      lastCell = { r:-1, c:-1 };
      return;
    }

    const shouldPan = isPanLocked || spaceDown;
    if(shouldPan){
      drawing = false;
      lastSinglePointerPos = { x: e.clientX, y: e.clientY };
      return;
    }

    const cell = getCellFromClient(e.clientX, e.clientY);
    if(cell.r>=0 && cell.c>=0 && cell.r<ROWS && cell.c<COLS){
      saveHistory();
      drawing = true;
      lastCell = { r:-1, c:-1 };
      applyCellIfNew(cell.r, cell.c);
      draw(); autoSave();
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    if(!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

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
      const cur = { x: e.clientX, y: e.clientY };
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
      lastCell = { r:-1, c:-1 };
      lastSinglePointerPos = null;
    }
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  // --- KEYBOARD (desktop) ---
  let spaceDown = false;
  window.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();
    if(key === ' '){ spaceDown = true; e.preventDefault(); }
    const isMod = e.ctrlKey || e.metaKey;
    if(isMod && key === 'z'){ e.preventDefault(); undo(); }
    if(isMod && (key === 'y' || (key === 'z' && e.shiftKey))){ e.preventDefault(); redo(); }
    if(key === '+' || key === '='){ e.preventDefault(); zoomAtCenter(1.15); }
    if(key === '-' || key === '_'){ e.preventDefault(); zoomAtCenter(1/1.15); }
  });
  window.addEventListener('keyup', (e) => { if(e.key === ' ') spaceDown = false; });

  // --- EXPORT PNG ---
  function exportPNG(){
    const url = canvas.toDataURL("image/png");
    const a = document.createElement('a');
    a.download = "haekle-design.png";
    a.href = url;
    a.click();
  }

  // --- PDF EXPORT (A4 + KVALITETSPRESETS) ---
  function getPdfSettings(){
    const preset = document.getElementById('pdfPreset').value;
    if(preset === 'print')  return { exportScale: 1.65, jpegQuality: 0.82, render: "SLOW" };
    if(preset === 'small')  return { exportScale: 1.20, jpegQuality: 0.65, render: "FAST" };
    return                  { exportScale: 1.45, jpegQuality: 0.78, render: "SLOW" }; // normal
  }

  function canvasToJpegDataUrl(sourceCanvas, quality){
    return sourceCanvas.toDataURL("image/jpeg", quality);
  }

  async function exportPDF() {
    const { jsPDF } = window.jspdf;
    const { exportScale, jpegQuality, render } = getPdfSettings();
    const marginMm = 8;

    const pdf = new jsPDF({ orientation: "p", unit: "mm", format: "a4", compress: true });

    const pageW = 210, pageH = 297;
    const usableW = pageW - marginMm * 2;
    const usableH = pageH - marginMm * 2;

    const tempCanvas = document.createElement("canvas");
    tempCanvas.width  = Math.ceil(((COLS * SIZE) + OFFSET + 80) * exportScale);
    tempCanvas.height = Math.ceil(((ROWS * SIZE) + OFFSET + 80) * exportScale);

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

    for (let page = 0; page < totalPages; page++) {
      const sy = page * pagePxH;
      const sh = Math.min(pagePxH, tempCanvas.height - sy);
      if (sliceCanvas.height !== sh) sliceCanvas.height = sh;

      sCtx.fillStyle = "#ffffff";
      sCtx.fillRect(0, 0, sliceCanvas.width, sliceCanvas.height);

      sCtx.drawImage(tempCanvas, 0, sy, tempCanvas.width, sh, 0, 0, tempCanvas.width, sh);

      const imgData = canvasToJpegDataUrl(sliceCanvas, jpegQuality);

      if (page > 0) pdf.addPage();

      const imgH_mm = (sh / pxPerMm);
      pdf.addImage(imgData, "JPEG", marginMm, marginMm, usableW, imgH_mm, undefined, render);
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

        const pix = tCtx.getImageData(0, 0, COLS, ROWS).data;
        for(let i=0; i<pix.length; i+=4){
          const avg = (pix[i] + pix[i+1] + pix[i+2]) / 3;
          const r = Math.floor((i/4)/COLS);
          const c = (i/4) % COLS;
          gridData[r][c] = avg < 125 ? 'fill' : null;
        }

        draw(); autoSave();
      }
      img.src = event.target.result;
    }
    reader.readAsDataURL(file);
    e.target.value = "";
    // Luk menu for app-følelse
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
