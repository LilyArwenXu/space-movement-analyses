function rankedInformationPoints(kind){const key=kind==='quality'?'quality':kind==='mix'?'mixScore':'vitality';return D.points.map((p,i)=>({p,i})).sort((a,b)=>{const x=a.p[key],y=b.p[key];return finite(x)&&finite(y)?x-y||a.i-b.i:finite(x)?-1:finite(y)?1:a.i-b.i;}).map(v=>v.p);}
function positionAxisControls(controls,c,count){
 const compact=window.innerWidth<700,step=compact?23:42,leftCount=Math.ceil(count/2),width=c.getWidth(),height=c.getHeight();
 const left=step*(leftCount-1)+42,right=step*(count-leftCount-1)+42;
 controls.style.top=(height-65)+'px';
 Array.from(controls.children).forEach((card,j)=>{card.style.left=(j<leftCount?left-j*step:width-right+(j-leftCount)*step)+'px';});
}
function enableChartDownload(c,node){
 const original=c.setOption.bind(c);
 c.setOption=(option,...args)=>original({...option,toolbox:{show:true,right:4,bottom:3,itemSize:15,showTitle:true,iconStyle:{borderColor:'#999',borderWidth:1},emphasis:{iconStyle:{borderColor:'#333'}},feature:{saveAsImage:{type:'png',name:(document.title||'图表').split('｜')[0],title:'下载 PNG',pixelRatio:2,backgroundColor:'#fff',excludeComponents:['toolbox']}}}},...args);
}
function saveCanvasPNG(canvas,name){const link=document.createElement('a');link.download=name+'.png';link.href=canvas.toDataURL('image/png');link.click();}
async function exportDOMChart(node){
 const rect=node.getBoundingClientRect(),canvas=document.createElement('canvas');canvas.width=Math.ceil(rect.width*2);canvas.height=Math.ceil(rect.height*2);const ctx=canvas.getContext('2d');ctx.scale(2,2);ctx.fillStyle='#fff';ctx.fillRect(0,0,rect.width,rect.height);
 if(node.classList.contains('map-stage')){
  const base=node.querySelector('img');if(base){await base.decode();ctx.drawImage(base,0,0,rect.width,rect.height);}
  const source=node.querySelector('svg'),clone=source.cloneNode(true),originals=[source,...source.querySelectorAll('*')],copies=[clone,...clone.querySelectorAll('*')];
  originals.forEach((el,i)=>{const css=getComputedStyle(el);['fill','fill-opacity','stroke','stroke-width','stroke-opacity','opacity','font-size','font-family'].forEach(k=>copies[i].style.setProperty(k,css.getPropertyValue(k)));});
  clone.setAttribute('width',rect.width);clone.setAttribute('height',rect.height);clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
  const blob=new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml;charset=utf-8'}),url=URL.createObjectURL(blob);
  try{const image=new Image();image.src=url;await image.decode();ctx.drawImage(image,0,0,rect.width,rect.height);}finally{URL.revokeObjectURL(url);}
 }else{
  node.querySelectorAll('.cov-cell').forEach(cell=>{const r=cell.getBoundingClientRect();ctx.fillStyle=getComputedStyle(cell).backgroundColor;ctx.fillRect(r.left-rect.left,r.top-rect.top,r.width,r.height);});
  node.querySelectorAll('.cov-row-label,.cov-col-label,.cov-detail').forEach(label=>{if(!label.getClientRects().length||label.closest('[hidden]'))return;const r=label.getBoundingClientRect(),css=getComputedStyle(label);ctx.fillStyle='rgba(255,255,255,.92)';ctx.fillRect(r.left-rect.left,r.top-rect.top,r.width,r.height);ctx.font=css.font;ctx.fillStyle=css.color;ctx.textBaseline='middle';ctx.fillText(label.textContent,r.left-rect.left+5,r.top-rect.top+r.height/2,r.width-10);});
 }
 saveCanvasPNG(canvas,(document.title||'图表').split('｜')[0]);
}
function attachDOMDownloads(){document.querySelectorAll('.map-stage,.covariance').forEach(node=>{if(node.querySelector('.dom-chart-download'))return;const button=document.createElement('button');button.className='dom-chart-download';button.title='下载 PNG';button.setAttribute('aria-label','下载图表 PNG');button.textContent='⇩';button.onclick=async event=>{event.stopPropagation();button.disabled=true;try{await exportDOMChart(node);}catch(error){button.title='下载失败，请重试';console.error(error);}finally{button.disabled=false;}};node.append(button);});}
if(typeof MutationObserver!=='undefined'){new MutationObserver(attachDOMDownloads).observe(W,{childList:true,subtree:true});attachDOMDownloads();}
if(document.fonts)document.fonts.load('16px SimSun').then(()=>charts.forEach(c=>{if(!c.isDisposed())c.resize();}));
