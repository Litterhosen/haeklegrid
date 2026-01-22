import streamlit as st
import streamlit.components.v1 as components

html_code = '''
<canvas id="myCanvas" style="border:1px solid #ccc;"></canvas>
<button id="saveBtn">Gem billede</button>
<script>
// Opsæt canvas med HiDPI-opsætning
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");
const baseW = 300, baseH = 300;
const scale = window.devicePixelRatio || 1;
canvas.width = baseW * scale;
canvas.height = baseH * scale;
canvas.style.width = baseW + "px";
canvas.style.height = baseH + "px";
ctx.scale(scale, scale);
ctx.imageSmoothingEnabled = false;

// Tegn eksempelvis et simpelt grid
ctx.strokeStyle = "#888";
for(let x=0; x<=baseW; x+=50){
  ctx.beginPath();
  ctx.moveTo(x,0);
  ctx.lineTo(x, baseH);
  ctx.stroke();
}
for(let y=0; y<=baseH; y+=50){
  ctx.beginPath();
  ctx.moveTo(0,y);
  ctx.lineTo(baseW, y);
  ctx.stroke();
}

// Gem knap-funktion
document.getElementById("saveBtn").onclick = () => {
  canvas.toBlob(function(blob) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = "canvas_grafik.png";
    a.click();
  }, "image/png");
};
</script>
'''
components.html(html_code, height=400)
