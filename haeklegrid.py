import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v6 (Mobilvenlig)", layout="wide", initial_sidebar_state="collapsed")

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
    --toolbar-h:160px;
  }

  * { box-sizing: border-box; }
  body{
    margin:0;
    font-family:-apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif;
    background:var(--bg-dark);
    height:100vh;
    overflow:hidden;
    touch-action:none; /* vigtigt: vi styrer touch selv */
  }

  /* TOP BAR */
  .toolbar{
    position:fixed; top:0; left:0; right:0;
    background:var(--toolbar-bg);
    padding:10px;
    display:flex; flex-direction:column; gap:8px;
    box-shadow:0 6px 18px rgba(0,0,0,0.35);
    z-index:1000;
  }

  .row{
    display:flex;
    align-items:center;
    gap:8px;
    flex-wrap:wrap;
  }

  .group{
    display:flex;
    align-items:center;
    gap:6px;
    background:#f1f3f5;
    padding:6px 10px;
    border-radius:12px;
    border:1px solid #dee2e6;
  }

  button, select, input{
    height:44px;
    border-radius:10px;
    border:1px solid #cfd4da;
    font-size:14px;
    font-weight:700;
    cursor:pointer;
    background:white;
    -webkit-tap-highlight-color: transparent;
  }

  button:active{ transform: translateY(1px); }

  .btn-icon{
    width:46px;
    display:flex; align-items:center; justify-content:center;
    font-size:18px;
  }

  .btn-text{
    padding:0 12px;
    flex:1 1 auto;
    min-width:120px;
  }

  .btn-blue{ background:var(--btn-blue); color:#fff; border:none; }
  .btn-green{ background:var(--btn-green); color:#fff; border:none; }
  .btn-red{ background:var(--btn-red); color:#fff; border:none; }
  .active-tool{ background:#f1c40f !important; color:#000 !important; }

  .size-input{ width:72px; text-align:center; font-size:16px; }
  #imgInput{ display:none; }

  /* VIEWPORT */
  .viewport{
    width:100vw;
    height:100vh;
    overflow:auto;
    padding-top: calc(var(--toolbar-h) + 6px);
    background:#34495e;
    -webkit-overflow-scrolling:touch;
  }

  /* Canvas: vi skalerer via CSS transform (zoom) */
  canvas{
    background:#fff;
    transform-origin:0 0;
    display:block;
    box-shadow:0 0 30px rgba(0,0,0,0.55);
    touch-action:none;
  }

  /* Lille statuslinje */
  .status{
    font-size:12px;
    font-weight:700;
    opacity:0.85;
    padding:0 6px;
    white-space:nowrap;
  }

  /* Hjælp modal */
  .modal-backdrop{
    position:fixed; inset:0;
    background:rgba(0,0,0,0.45);
    display:none;
    align-items:center; justify-content:center;
    z-index:2000;
    padding:16px;
  }
  .modal{
    width:min(720px, 96vw);
    max-height: min(80vh, 720px);
    overflow:auto;
    background:#fff;
    border-radius:16px;
    box-shadow:0 18px 60px rgba(0,0,0,0.5);
    padding:14px 14px 10px;
  }
  .modal h2{ margin:0 0 6px; font-size:18px; }
  .modal p, .modal li{ font-size:14px; line-height:1.35; }
  .modal .close-row{ display:flex; justify-content:flex-end; gap:8px; margin-top:10px; }
  .pill{
    display:inline-block; padding:2px 8px; border-radius:999px;
    background:#f1f3f5; border:1px solid #dee2e6;
    font-weight:800; font-size:12px;
  }

  /* Små skærme: knapper lidt mere kompakte */
  @media (max-width: 520px){
    button, select, input{ height:42px; font-size:13px; }
    .btn-text{ min-width: 0; }
    .group{ padding:6px 8px; }
    .size-input{ width:64px; }
  }
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
  <div class="row">
    <div class="group">
      <input type="number" id="rows" value="114" class="size-input" inputmode="numeric"> rk
      <span style="font-weight:900;">×</span>
      <input type="number" id="cols" value="23" class="size-input" inputmode="numeric"> mk
      <button class="btn-text" onclick="resizeGrid()" style="background:#d9dde1;">OK</button>
    </div>

    <div class="group">
      <button class="btn-icon" onclick="undo()" title="Fortryd (Ctrl/Cmd+Z)">↩️</button>
      <button class="btn-icon" onclick="redo()" title="Gendan (Ctrl/Cmd+Y)">↪️</button>
    </div>

    <div class="group" style="margin-left:auto;">
      <button class="btn-text" onclick="toggleHelp()" title="Kort brugsguide">❓ Hjælp</button>
    </div>
  </div>

  <div class="row">
    <select id="mode" style="flex:2 1 220px;" title="Vælg symbol/farve">
      <option value="fill">⚫ SORT</option>
      <option value="X">❌ X-MASKE</option>
      <option value="O">⭕ O-MASKE</option>
      <option value="erase">⚪ SLET</option>
    </select>

    <button id="panBtn" class="btn-icon" onclick="togglePan()" title="Pan-lås (på touch kan du også pan med 2 fingre)">✋</button>

    <div class="group">
      <button class="btn-icon" onclick="zoomAtCenter(1.15)" title="Zoom ind (+)">➕</button>
      <button class="btn-icon" onclick="zoomAtCenter(1/1.15)" title="Zoom ud (-)">➖</button>
      <div class="status" id="status">Zoom: 100%</div>
    </div>
  </div>

  <div class="row">
    <button class="btn-text btn-blue" onclick="document.getElementById('imgInput').click()">📥 HENT FOTO</button>
    <input type="file" id="imgInput" accept="image/*">

    <button class="btn-text btn-green" onclick="exportPDF()">📄 GEM PDF</button>
    <button class="btn-text" onclick="exportPNG()">🖼️ PNG</button>

    <button class="btn-icon btn-red" onclick="resetCanvas()" title="Slet alt">🗑️</button>
  </div>
</div>

<div class="viewport" id="vp">
  <canvas id="c"></canvas>
</div>

<!-- Hjælp modal -->
<div class="modal-backdrop" id="helpBackdrop" onclick="closeHelpFromBackdrop(event)">
  <div class="modal" role="dialog" aria-modal="true" aria-label="Brugsguide">
    <h2>Brugsguide (hurtig)</h2>
    <p>
      Dette grid kan bruges til <b>hækling</b>, <b>strik</b>, <b>perleplader</b>, <b>korssting</b>, <b>broderi</b>
      og andre mønstre – for både børn, unge og voksne.
    </p>

    <ul>
      <li><span class="pill">1</span> Vælg en markering i menuen: <b>Sort</b>, <b>X</b>, <b>O</b> eller <b>Slet</b>.</li>
      <li><span class="pill">2</span> Tryk på en firkant for at sætte/fjerne markering. Du kan også <b>trække</b> for at tegne hurtigt.</li>
      <li><span class="pill">3</span> Flyt rundt:
        <ul>
          <li><b>Mobil/Tablet:</b> Brug <b>2 fingre</b> for at flytte. Knib (pinch) for zoom.</li>
          <li><b>Desktop:</b> Hold <b>Mellemrum</b> nede og træk for at flytte, eller slå ✋ til.</li>
        </ul>
      </li>
      <li><span class="pill">4</span> Zoom: brug ➕/➖ eller knib med 2 fingre.</li>
      <li><span class="pill">5</span> Fortryd/Gendan: ↩️/↪️ (desktop: <b>Ctrl/Cmd+Z</b> og <b>Ctrl/Cmd+Y</b>).</li>
      <li><span class="pill">6</span> Gem:
        <ul>
          <li><b>PDF</b> er godt til print og deling.</li>
          <li><b>PNG</b> er godt som billede (fx til telefonen).</li>
        </ul>
      </li>
      <li><span class="pill">Tip</span> Grid gemmer automatisk i din browser. Hvis du lukker siden og åbner igen, ligger dit mønster der typisk stadig.</li>
    </ul>

    <div class="close-row">
      <button onclick="toggleHelp()" class="btn-text" style="background:#d9dde1;">Luk</button>
    </div>
  </div>
</div>

<script>
  // --- GRID STATE ---
  let COLS = 23, ROWS = 114, SIZE = 25, OFFSET = 45;
  let gridData = [], history = [], redoStack = [];

  // Navigation state
  let isPanLocked = false;          // ✋ knappen
  let scale = 1.0;                  // zoom
  const minScale = 0.2, maxScale = 4.0;

  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  const vp = document.getElementById('vp');
  const statusEl = document.getElementById('status');

  // Pointer tracking for multi-touch
  const pointers = new Map(); // pointerId -> {x,y}
  let drawing = false;
  let lastCell = { r: -1, c: -1 };

  // --- UX HELPERS ---
  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

  function setScale(newScale){
    scale = clamp(newScale, minScale, maxScale);
    canvas.style.transform = `scale(${scale})`;
    statusEl.textContent = `Zoom: ${Math.round(scale*100)}%`;
  }

  function measureToolbarHeight(){
    const tb = document.getElementById('toolbar');
    const h = tb.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--toolbar-h', `${Math.ceil(h)}px`);
  }

  window.addEventListener('resize', () => {
    measureToolbarHeight();
  });

  function toggleHelp(){
    const bd = document.getElementById('helpBackdrop');
    const isOpen = bd.style.display === 'flex';
    bd.style.display = isOpen ? 'none' : 'flex';
  }

  function closeHelpFromBackdrop(e){
    if(e.target && e.target.id === 'helpBackdrop') toggleHelp();
  }

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
    localStorage.setItem('haekleGridScale', String(scale));
  }

  // --- GRID RESIZE ---
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

  // --- DRAWING ---
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

  // --- HIT TEST (skærm -> celle) ---
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

    // toggle (tryk samme igen -> fjern)
    gridData[r][c] = (gridData[r][c] === next) ? null : next;
  }

  // Når man trækker: undgå at tegne samme celle igen og igen
  function applyCellIfNew(r, c){
    if(r===lastCell.r && c===lastCell.c) return;
    lastCell = { r, c };
    applyCell(r, c);
  }

  // --- PAN / ZOOM CONTROLS ---
  function togglePan(){
    isPanLocked = !isPanLocked;
    document.getElementById('panBtn').classList.toggle('active-tool', isPanLocked);
  }

  function zoomAtCenter(mult){
    // Zoom omkring midten af viewport
    const beforeScale = scale;
    const newScale = clamp(scale * mult, minScale, maxScale);

    // viewport center i canvas-koordinater
    const vpRect = vp.getBoundingClientRect();
    const centerX = vpRect.left + vpRect.width/2;
    const centerY = vpRect.top + vpRect.height/2;
    const rect = canvas.getBoundingClientRect();

    const canvasX = (centerX - rect.left + vp.scrollLeft) / beforeScale;
    const canvasY = (centerY - rect.top + vp.scrollTop) / beforeScale;

    setScale(newScale);

    // juster scroll så center forbliver center-ish
    vp.scrollLeft = canvasX * newScale - (vpRect.width/2);
    vp.scrollTop  = canvasY * newScale - (vpRect.height/2);

    autoSave();
  }

  // --- POINTER EVENTS: DRAW + TWO-FINGER PAN + PINCH ---
  let pinchStartDist = 0;
  let pinchStartScale = 1;
  let lastPanMid = null;

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

    // Hvis 2 fingre/mus-pointere: start pinch/pan
    if(pointers.size === 2){
      const pts = Array.from(pointers.values());
      pinchStartDist = distance(pts[0], pts[1]);
      pinchStartScale = scale;
      lastPanMid = midpoint(pts[0], pts[1]);
      drawing = false;
      lastCell = { r:-1, c:-1 };
      return;
    }

    // 1 pointer: tegn eller pan afhængigt af lock + keyboard space
    const shouldPan = isPanLocked || spaceDown;
    if(shouldPan){
      drawing = false;
      lastCell = { r:-1, c:-1 };
      return;
    }

    // tegn (start)
    const cell = getCellFromClient(e.clientX, e.clientY);
    if(cell.r>=0 && cell.c>=0 && cell.r<ROWS && cell.c<COLS){
      saveHistory();
      drawing = true;
      lastCell = { r:-1, c:-1 };
      applyCellIfNew(cell.r, cell.c);
      draw();
      autoSave();
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    if(!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

    // 2 pointers: pinch zoom + pan
    if(pointers.size === 2){
      const pts = Array.from(pointers.values());
      const d = distance(pts[0], pts[1]);
      const mid = midpoint(pts[0], pts[1]);

      // Zoom
      if(pinchStartDist > 0){
        const factor = d / pinchStartDist;
        const newScale = clamp(pinchStartScale * factor, minScale, maxScale);
        const prevScale = scale;

        // zoom omkring midtpunktet
        const vpRect = vp.getBoundingClientRect();
        const rect = canvas.getBoundingClientRect();

        const mx = mid.x - vpRect.left + vp.scrollLeft;
        const my = mid.y - vpRect.top + vp.scrollTop;

        const canvasX = mx / prevScale;
        const canvasY = my / prevScale;

        setScale(newScale);

        vp.scrollLeft = canvasX * newScale - (mid.x - vpRect.left);
        vp.scrollTop  = canvasY * newScale - (mid.y - vpRect.top);
      }

      // Pan (2-finger)
      if(lastPanMid){
        const dx = mid.x - lastPanMid.x;
        const dy = mid.y - lastPanMid.y;
        vp.scrollLeft -= dx;
        vp.scrollTop  -= dy;
      }
      lastPanMid = mid;

      autoSave();
      return;
    }

    // 1 pointer:
    if(isPanLocked || spaceDown){
      // pan med musebevægelse / finger (når lock/space)
      // movementX/Y fungerer ikke altid på touch, så vi bruger delta fra last position
      const prev = lastSinglePointerPos;
      const cur = { x: e.clientX, y: e.clientY };
      if(prev){
        vp.scrollLeft -= (cur.x - prev.x);
        vp.scrollTop  -= (cur.y - prev.y);
      }
      lastSinglePointerPos = cur;
      return;
    }

    // draw while dragging
    if(drawing){
      const cell = getCellFromClient(e.clientX, e.clientY);
      if(cell.r>=0 && cell.c>=0 && cell.r<ROWS && cell.c<COLS){
        applyCellIfNew(cell.r, cell.c);
        draw();
        autoSave();
      }
    }
  });

  let lastSinglePointerPos = null;

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
  canvas.addEventListener('pointerout', (e) => {
    // hvis pointer forlader canvas, stop tegning (mere for desktop)
    if(e.pointerType === 'mouse') drawing = false;
  });

  // --- KEYBOARD SHORTCUTS (desktop) ---
  let spaceDown = false;
  window.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();

    // Undgå at browseren scroller ved space
    if(key === ' '){
      spaceDown = true;
      e.preventDefault();
    }

    // Undo/Redo
    const isMod = e.ctrlKey || e.metaKey;
    if(isMod && key === 'z'){ e.preventDefault(); undo(); }
    if(isMod && (key === 'y' || (key === 'z' && e.shiftKey))){ e.preventDefault(); redo(); }

    // Zoom
    if(key === '+' || key === '=' ){ e.preventDefault(); zoomAtCenter(1.15); }
    if(key === '-' || key === '_' ){ e.preventDefault(); zoomAtCenter(1/1.15); }
  });

  window.addEventListener('keyup', (e) => {
    if(e.key === ' ') spaceDown = false;
  });

  // --- EXPORT ---
  function exportPNG(){
    const url = canvas.toDataURL("image/png");
    const a = document.createElement('a');
    a.download = "haekle-design.png";
    a.href = url;
    a.click();
  }

  async function exportPDF(){
    const { jsPDF } = window.jspdf;

    const tempCanvas = document.createElement('canvas');
    const exportScale = 2;
    tempCanvas.width = ((COLS * SIZE) + OFFSET + 80) * exportScale;
    tempCanvas.height = ((ROWS * SIZE) + OFFSET + 80) * exportScale;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.scale(exportScale, exportScale);
    drawOnContext(tempCtx, SIZE, OFFSET, true);

    const imgData = tempCanvas.toDataURL("image/png");

    const pdfW = 210;
    const pdfH = (tempCanvas.height * pdfW) / tempCanvas.width;

    const pdf = new jsPDF('p', 'mm', [pdfW, pdfH]);
    pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH);
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
  };

  function resetCanvas(){
    if(confirm("Vil du slette ALT?")){
      localStorage.clear();
      location.reload();
    }
  }

  // Kickoff
  init();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
