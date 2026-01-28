import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Hækle Grid Pro v7.1 (Optimized)", layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit default header and footer, and set page background
st.markdown("""
<style>
header, footer, .stDeployButton, [data-testid="stHeader"] {display:none !important;}
.main .block-container {padding: 0px !important;}
body { background: #1a252f; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# Embed the HTML/JS app
html_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, maximum-scale=1.0, user-scalable=no">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.2/jspdf.umd.min.js"></script>  <!-- Updated jsPDF -->
<style>
  :root {
    --bg-dark: #2c3e50;
    --toolbar-bg: #ffffff;
    --btn-blue: #3498db;
    --btn-green: #27ae60;
    --btn-red: #e74c3c;
    --toolbar-h: 64px;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif;
    background: var(--bg-dark);
    height: 100vh;
    overflow: hidden;
    touch-action: none;
  }
  /* ... (CSS unchanged for toolbar, panel, etc.) ... */
  .viewport {
    width: 100vw;
    height: 100vh;
    overflow: auto;
    padding-top: calc(var(--toolbar-h) + 6px);
    background: #34495e;
    -webkit-overflow-scrolling: touch;
  }
  canvas {
    background: #fff;
    transform-origin: 0 0;
    display: block;
    box-shadow: 0 0 30px rgba(0,0,0,0.55);
    touch-action: none;
  }
  /* ... (rest of CSS unchanged) ... */
</style>
</head>
<body>

<div class="toolbar" id="toolbar">
  <!-- ... (toolbar HTML unchanged) ... -->
</div>

<!-- Panel Backdrop and Menu Panel -->
<div class="panel-backdrop" id="panelBackdrop" onclick="closePanelFromBackdrop(event)"></div>
<div class="panel" id="panel">
  <!-- ... (panel HTML unchanged) ... -->
</div>

<div class="viewport" id="vp">
  <canvas id="c"></canvas>
</div>

<!-- Help Modal -->
<div class="help-backdrop" id="helpBackdrop" onclick="closeHelpFromBackdrop(event)">
  <!-- ... (help dialog HTML unchanged) ... -->
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

  // Pointer and drawing tracking
  const pointers = new Map();
  let drawing = false;
  let lastCell = { r: -1, c: -1 };
  let hasDrawnSinceLastSave = false;  // Flag to indicate unsaved changes in current stroke

  // --- PANEL / HELP TOGGLE FUNCTIONS (unchanged) ---
  function togglePanel() { /* ... */ }
  function closePanelFromBackdrop(e) { /* ... */ }
  function toggleHelp() { /* ... */ }
  function closeHelpFromBackdrop(e) { /* ... */ }

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function setScale(newScale) {
    scale = clamp(newScale, minScale, maxScale);
    canvas.style.transform = `scale(${scale})`;
    localStorage.setItem('haekleGridScale', String(scale));
  }
  function measureToolbarHeight() {
    const tb = document.getElementById('toolbar');
    const h = tb.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--toolbar-h', `${Math.ceil(h)}px`);
  }
  window.addEventListener('resize', measureToolbarHeight);

  // --- AUTO-SAVE & INIT ---
  function init() {
    const saved = localStorage.getItem('haekleGridData');
    const sRows = localStorage.getItem('haekleGridRows');
    const sCols = localStorage.getItem('haekleGridCols');
    const sScale = localStorage.getItem('haekleGridScale');
    if (saved && sRows && sCols) {
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

  function autoSave() {
    // Save current grid state to localStorage
    localStorage.setItem('haekleGridData', JSON.stringify(gridData));
    localStorage.setItem('haekleGridRows', ROWS);
    localStorage.setItem('haekleGridCols', COLS);
    hasDrawnSinceLastSave = false;  // reset the dirty flag after saving
  }

  // --- GRID RESIZE ---
  function resizeGrid() {
    const nR = Math.max(1, parseInt(document.getElementById('rows').value || "1", 10));
    const nC = Math.max(1, parseInt(document.getElementById('cols').value || "1", 10));
    saveHistory();
    const oldData = JSON.parse(JSON.stringify(gridData));
    gridData = Array(nR).fill().map(() => Array(nC).fill(null));
    for (let r = 0; r < Math.min(ROWS, nR); r++) {
      for (let c = 0; c < Math.min(COLS, nC); c++) {
        gridData[r][c] = oldData[r][c];
      }
    }
    ROWS = nR; COLS = nC;
    updateCanvas();
    autoSave();  // save new size and grid to storage
  }

  function updateCanvas() {
    canvas.width = (COLS * SIZE) + OFFSET;
    canvas.height = (ROWS * SIZE) + OFFSET;
    draw();  // draw the entire grid
  }

  // --- DRAWING FUNCTIONS ---
  function drawOnContext(tCtx, s, off, isExport = false) {
    const margin = isExport ? 40 : 0;
    // Fill background white for export (no transparency issues)
    tCtx.fillStyle = "#ffffff";
    tCtx.fillRect(0, 0, tCtx.canvas.width, tCtx.canvas.height);
    // Draw grid lines and numbering
    for (let i = 0; i <= COLS; i++) {
      const x = i * s + off + margin;
      tCtx.beginPath();
      tCtx.strokeStyle = (i % 10 === 0) ? "#000" : (i % 5 === 0 ? "#888" : "#ddd");
      tCtx.lineWidth = (i % 5 === 0) ? 1.5 : 0.8;
      tCtx.moveTo(x, off + margin);
      tCtx.lineTo(x, (ROWS * s) + off + margin);
      tCtx.stroke();
      // Column numbers (every 5th column)
      if (i < COLS && ((i + 1 === 1) || ((i + 1) % 5 === 0))) {
        tCtx.font = "bold 12px Arial";
        tCtx.fillStyle = "#000";
        tCtx.textAlign = "center";
        tCtx.fillText(i + 1, x + s/2, off + margin - 12);
      }
    }
    for (let j = 0; j <= ROWS; j++) {
      const y = j * s + off + margin;
      tCtx.beginPath();
      tCtx.strokeStyle = (j % 10 === 0) ? "#000" : (j % 5 === 0 ? "#888" : "#ddd");
      tCtx.lineWidth = (j % 5 === 0) ? 1.5 : 0.8;
      tCtx.moveTo(off + margin, y);
      tCtx.lineTo((COLS * s) + off + margin, y);
      tCtx.stroke();
      // Row numbers (every 5th row)
      if (j < ROWS && ((j + 1 === 1) || ((j + 1) % 5 === 0))) {
        tCtx.font = "bold 12px Arial";
        tCtx.fillStyle = "#000";
        tCtx.textAlign = "right";
        tCtx.fillText(j + 1, off + margin - 10, y + s/1.5);
      }
    }
    // Draw the pattern content (fills, X's, O's)
    tCtx.textAlign = "center";
    tCtx.fillStyle = "#000";
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        if (!gridData[r][c]) continue;
        const x = c * s + off + margin;
        const y = r * s + off + margin;
        if (gridData[r][c] === 'fill') {
          // Filled square (leave 1px border to preserve grid lines)
          tCtx.fillRect(x + 1, y + 1, s - 1, s - 1);
        } else {
          // Draw symbol (X or O)
          tCtx.font = `bold ${s * 0.7}px Arial`;
          tCtx.fillText(gridData[r][c], x + s/2, y + s/1.3);
        }
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawOnContext(ctx, SIZE, OFFSET, false);
  }

  function saveHistory() {
    history.push(JSON.stringify(gridData));
    if (history.length > 60) history.shift();
    redoStack = [];
  }
  function undo() {
    if (history.length) {
      redoStack.push(JSON.stringify(gridData));
      gridData = JSON.parse(history.pop());
      draw();
      autoSave();
    }
  }
  function redo() {
    if (redoStack.length) {
      history.push(JSON.stringify(gridData));
      gridData = JSON.parse(redoStack.pop());
      draw();
      autoSave();
    }
  }

  // --- CELL STATE HELPERS ---
  function getCellFromClient(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left) / scale;
    const y = (clientY - rect.top) / scale;
    const c = Math.floor((x - OFFSET) / SIZE);
    const r = Math.floor((y - OFFSET) / SIZE);
    return { r, c };
  }

  function applyCell(r, c) {
    if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return;
    const mode = document.getElementById('mode').value;
    const nextState = (mode === 'erase') ? null : mode;
    // Toggle cell state (if already the same, clear it)
    gridData[r][c] = (gridData[r][c] === nextState) ? null : nextState;
    hasDrawnSinceLastSave = true;  // mark that a change has been made
  }

  function applyCellIfNew(r, c) {
    if (r === lastCell.r && c === lastCell.c) return;  // skip if it's the same cell as last time
    lastCell = { r, c };
    applyCell(r, c);
    // Redraw the canvas for the new change
    draw();
    // (We defer autoSave until after drawing completes or input ends)
  }

  // --- PAN & ZOOM CONTROLS ---
  function togglePan() {
    isPanLocked = !isPanLocked;
    document.getElementById('panBtn').classList.toggle('active-tool', isPanLocked);
  }

  function zoomAtCenter(mult) {
    const prevScale = scale;
    const newScale = clamp(scale * mult, minScale, maxScale);
    const vpRect = vp.getBoundingClientRect();
    const centerX = vpRect.left + vpRect.width / 2;
    const centerY = vpRect.top + vpRect.height / 2;
    const rect = canvas.getBoundingClientRect();
    // Calculate canvas coordinates for viewport center
    const canvasX = (centerX - rect.left + vp.scrollLeft) / prevScale;
    const canvasY = (centerY - rect.top + vp.scrollTop) / prevScale;
    setScale(newScale);
    // Adjust scrolling to keep the same center point in view
    vp.scrollLeft = canvasX * newScale - (vpRect.width / 2);
    vp.scrollTop  = canvasY * newScale - (vpRect.height / 2);
  }

  // --- POINTER EVENT HANDLERS ---
  let spaceDown = false;
  window.addEventListener('keydown', (e) => {
    if (e.key === ' ') { spaceDown = true; e.preventDefault(); }
    const mod = e.ctrlKey || e.metaKey;
    if (mod && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); }
    if (mod && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) {
      e.preventDefault();
      redo();
    }
    if (e.key === '+' || e.key === '=') { e.preventDefault(); zoomAtCenter(1.15); }
    if (e.key === '-' || e.key === '_') { e.preventDefault(); zoomAtCenter(1/1.15); }
  });
  window.addEventListener('keyup', (e) => {
    if (e.key === ' ') spaceDown = false;
  });

  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      // Two-finger touch: initialize pinch-zoom/pan
      const pts = Array.from(pointers.values());
      pinchStartDist = distance(pts[0], pts[1]);
      pinchStartScale = scale;
      lastPanMid = midpoint(pts[0], pts[1]);
      drawing = false;
      lastCell = { r: -1, c: -1 };
      return;
    }
    const shouldPan = isPanLocked || spaceDown;
    if (shouldPan) {
      // Pan mode (no drawing)
      drawing = false;
      lastSinglePointerPos = { x: e.clientX, y: e.clientY };
      return;
    }
    // Drawing mode:
    const cell = getCellFromClient(e.clientX, e.clientY);
    if (cell.r >= 0 && cell.r < ROWS && cell.c >= 0 && cell.c < COLS) {
      saveHistory();
      drawing = true;
      lastCell = { r: -1, c: -1 };
      applyCellIfNew(cell.r, cell.c);
      // Note: autoSave will be handled on pointerup to avoid rapid writes
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      // Handle pinch zoom and pan with two fingers
      const pts = Array.from(pointers.values());
      const dist = distance(pts[0], pts[1]);
      const mid = midpoint(pts[0], pts[1]);
      // Zoom handling
      if (pinchStartDist > 0) {
        const factor = dist / pinchStartDist;
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
      // Pan handling
      if (lastPanMid) {
        const dx = mid.x - lastPanMid.x;
        const dy = mid.y - lastPanMid.y;
        vp.scrollLeft -= dx;
        vp.scrollTop  -= dy;
      }
      lastPanMid = mid;
      return;
    }
    if (isPanLocked || spaceDown) {
      // Single-finger panning (when pan mode or spacebar)
      const prev = lastSinglePointerPos;
      const cur = { x: e.clientX, y: e.clientY };
      if (prev) {
        vp.scrollLeft -= (cur.x - prev.x);
        vp.scrollTop  -= (cur.y - prev.y);
      }
      lastSinglePointerPos = cur;
      return;
    }
    // Drawing mode pointer move
    if (drawing) {
      const cell = getCellFromClient(e.clientX, e.clientY);
      if (cell.r >= 0 && cell.r < ROWS && cell.c >= 0 && cell.c < COLS) {
        applyCellIfNew(cell.r, cell.c);
        // We still defer autoSave until pointerup for performance
      }
    }
  });

  function endPointer(e) {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) {
      pinchStartDist = 0;
      pinchStartScale = scale;
      lastPanMid = null;
    }
    if (pointers.size === 0) {
      // All touches/releases ended
      if (drawing) {
        drawing = false;
        lastCell = { r: -1, c: -1 };
      }
      lastSinglePointerPos = null;
      // Perform a single save after completing the draw action (if any changes made)
      if (hasDrawnSinceLastSave) {
        autoSave();
      }
    }
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  // Utility for pinch calculations
  function distance(a, b) { const dx = a.x - b.x, dy = a.y - b.y; return Math.sqrt(dx*dx + dy*dy); }
  function midpoint(a, b) { return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }; }

  // --- EXPORT FUNCTIONS ---
  function exportPNG() {
    // Export current canvas view as PNG image
    const url = canvas.toDataURL("image/png");
    const a = document.createElement('a');
    a.download = "haekle-design.png";
    a.href = url;
    a.click();
  }

  async function exportPDF() {
    const { jsPDF } = window.jspdf;
    const preset = document.getElementById('pdfPreset').value;
    // Choose export scale and JPEG quality based on preset
    let exportScale = 1.45, jpegQuality = 0.78, renderMode = "SLOW";
    if (preset === 'print') {
      exportScale = 1.65; jpegQuality = 0.82; renderMode = "SLOW";
    } else if (preset === 'small') {
      exportScale = 1.20; jpegQuality = 0.65; renderMode = "FAST";
    }
    // Calculate required canvas size for full pattern
    const baseW = (COLS * SIZE) + OFFSET + 80;
    const baseH = (ROWS * SIZE) + OFFSET + 80;
    // Adjust exportScale if canvas would be too large (to avoid browser limits)
    const maxDim = 16000;  // safe max dimension in pixels for canvas
    if (baseW * exportScale > maxDim || baseH * exportScale > maxDim) {
      const scaleW = maxDim / baseW;
      const scaleH = maxDim / baseH;
      exportScale = Math.min(exportScale, scaleW, scaleH);
      console.warn("Export scale adjusted to avoid oversized canvas");
    }
    // Create a temporary canvas for high-res rendering
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width  = Math.ceil(baseW * exportScale);
    tempCanvas.height = Math.ceil(baseH * exportScale);
    const tCtx = tempCanvas.getContext("2d");
    tCtx.scale(exportScale, exportScale);
    drawOnContext(tCtx, SIZE, OFFSET, true);
    // Set up PDF (A4 size)
    const pdf = new jsPDF({ orientation: "p", unit: "mm", format: "a4", compress: true });
    const pageW = 210, pageH = 297;
    const margin = 8;
    const usableW = pageW - margin * 2;
    const usableH = pageH - margin * 2;
    const pxPerMm = tempCanvas.width / usableW;
    const pagePxHeight = Math.floor(usableH * pxPerMm);
    const sliceCanvas = document.createElement("canvas");
    sliceCanvas.width = tempCanvas.width;
    sliceCanvas.height = pagePxHeight;
    const sCtx = sliceCanvas.getContext("2d");
    const totalPages = Math.ceil(tempCanvas.height / pagePxHeight);
    for (let page = 0; page < totalPages; page++) {
      const sy = page * pagePxHeight;
      const sh = Math.min(pagePxHeight, tempCanvas.height - sy);
      if (sliceCanvas.height !== sh) {
        sliceCanvas.height = sh;
      }
      // Fill background white on each slice to avoid transparency issues
      sCtx.fillStyle = "#ffffff";
      sCtx.fillRect(0, 0, sliceCanvas.width, sliceCanvas.height);
      // Draw portion of tempCanvas onto slice
      sCtx.drawImage(tempCanvas, 0, sy, tempCanvas.width, sh, 0, 0, tempCanvas.width, sh);
      const imgData = sliceCanvas.toDataURL("image/jpeg", jpegQuality);
      if (page > 0) pdf.addPage();
      const imgHeightMm = sh / pxPerMm;
      pdf.addImage(imgData, "JPEG", margin, margin, usableW, imgHeightMm, undefined, renderMode);
    }
    pdf.save("haekle-moenster.pdf");
  }

  // --- IMAGE IMPORT (Pattern from photo) ---
  document.getElementById('imgInput').onchange = function(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(event) {
      const img = new Image();
      img.onload = function() {
        saveHistory();
        // Draw image scaled to grid size on a temporary canvas
        const tCanvas = document.createElement('canvas');
        tCanvas.width = COLS;
        tCanvas.height = ROWS;
        const tCtx2 = tCanvas.getContext('2d');
        tCtx2.drawImage(img, 0, 0, COLS, ROWS);
        const pix = tCtx2.getImageData(0, 0, COLS, ROWS).data;
        for (let i = 0; i < pix.length; i += 4) {
          const avg = (pix[i] + pix[i+1] + pix[i+2]) / 3;
          const r = Math.floor((i/4) / COLS);
          const c = (i/4) % COLS;
          gridData[r][c] = avg < 128 ? 'fill' : null;  // threshold ~50% brightness
        }
        draw();
        autoSave();
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = "";
    // Close panel if open (for better UX on mobile after selecting an image)
    if (document.getElementById('panel').style.display === 'block') {
      togglePanel();
    }
  };

  function resetCanvas() {
    if (confirm("Vil du slette ALT?")) {
      localStorage.clear();
      location.reload();
    }
  }

  // Initialize the grid on page load
  init();
</script>
</body>
</html>
"""
components.html(html_code, height=1200, scrolling=False)
