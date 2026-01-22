<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Safe Grid Editor</title>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; background: #f5f5f5; }
  header {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; background: #222; color: #fff;
  }
  header button { padding: 6px 10px; }

  #app { display: flex; height: calc(100vh - 48px); }

  #overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.4);
    display: none; z-index: 10;
  }

  #drawer {
    position: fixed; top: 48px; left: 0; bottom: 0;
    width: 260px; background: #fff; padding: 12px;
    box-shadow: 2px 0 10px rgba(0,0,0,0.2);
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    z-index: 11;
  }

  #drawer.open { transform: translateX(0); }
  #overlay.show { display: block; }

  #canvasWrap {
    flex: 1; overflow: auto; display: flex; justify-content: center; align-items: center;
  }

  canvas { background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
</style>
</head>
<body>

<header>
  <button id="menuBtn">☰</button>
  <button onclick="exportPNG()">⬇ PNG</button>
  <span style="flex:1"></span>
  <select id="tool">
    <option value="fill">■</option>
    <option value="cross">✖</option>
    <option value="circle">○</option>
    <option value="erase">🧽</option>
  </select>
</header>

<div id="overlay"></div>

<div id="drawer">
  <h3>Indstillinger</h3>
  <label>Grid størrelse</label><br />
  <input id="gridSize" type="number" value="120" min="120" max="400" />
  <button onclick="resizeGrid()">Anvend</button>
  <hr />
  <button onclick="exportPNG()">Eksport PNG</button>
</div>

<div id="app">
  <div id="canvasWrap">
    <canvas id="grid"></canvas>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
  var canvas = document.getElementById('grid');
  var ctx = canvas.getContext('2d');
  var size = 120;
  var cell = 20;
  var tool = 'fill';
  var grid = [];

  function initGrid() {
    grid = [];
    for (var y = 0; y < size; y++) {
      var row = [];
      for (var x = 0; x < size; x++) row.push(null);
      grid.push(row);
    }
    canvas.width = size * cell;
    canvas.height = size * cell;
    draw();
  }

  function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle = '#ccc';

    for (var y = 0; y < size; y++) {
      for (var x = 0; x < size; x++) {
        ctx.strokeRect(x*cell, y*cell, cell, cell);
        var v = grid[y][x];
        if (!v) continue;
        ctx.fillStyle = '#000';
        ctx.strokeStyle = '#000';
        if (v === 'fill') ctx.fillRect(x*cell+2,y*cell+2,cell-4,cell-4);
        if (v === 'cross') {
          ctx.beginPath();
          ctx.moveTo(x*cell+3,y*cell+3);
          ctx.lineTo(x*cell+cell-3,y*cell+cell-3);
          ctx.moveTo(x*cell+cell-3,y*cell+3);
          ctx.lineTo(x*cell+3,y*cell+cell-3);
          ctx.stroke();
        }
        if (v === 'circle') {
          ctx.beginPath();
          ctx.arc(x*cell+cell/2,y*cell+cell/2,cell/2-3,0,Math.PI*2);
          ctx.stroke();
        }
      }
    }
  }

  canvas.addEventListener('click', function(e){
    var rect = canvas.getBoundingClientRect();
    var x = Math.floor((e.clientX - rect.left)/cell);
    var y = Math.floor((e.clientY - rect.top)/cell);
    if (tool === 'erase') grid[y][x] = null;
    else grid[y][x] = tool;
    draw();
  });

  document.getElementById('tool').onchange = function(e){ tool = e.target.value; };

  function resizeGrid(){
    size = parseInt(document.getElementById('gridSize').value,10);
    initGrid();
  }

  function exportPNG(){
    html2canvas(canvas).then(function(c){
      c.toBlob(function(blob){
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'grid.png';
        a.click();
      });
    });
  }

  var drawer = document.getElementById('drawer');
  var overlay = document.getElementById('overlay');

  document.getElementById('menuBtn').onclick = function(){
    drawer.classList.add('open');
    overlay.classList.add('show');
  };

  overlay.onclick = function(){
    drawer.classList.remove('open');
    overlay.classList.remove('show');
  };

  initGrid();
</script>
</body>
</html>
