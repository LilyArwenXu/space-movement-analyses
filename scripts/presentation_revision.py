"""Shared chart ink, localized heat kernels, and sentence-based subtitles."""
def renderer(js):
    js=js.replace("function note(text){NOTE.textContent=text;}", "function note(text){NOTE.textContent=String(text).replace(/。\\s*/g,'。\\n').trim();NOTE.hidden=!NOTE.textContent;}")
    js=js.replace('charts.push(c);enableChartDownload(c,n);', '''
 const setOption=c.setOption.bind(c);
 c.setOption=(option,...args)=>{
  ['xAxis','yAxis'].forEach(key=>{if(option[key])([].concat(option[key])).forEach(a=>{
   a.axisLine={...a.axisLine,show:true,lineStyle:{...a.axisLine?.lineStyle,color:'#000',opacity:1}};
   a.axisTick={...a.axisTick,lineStyle:{...a.axisTick?.lineStyle,color:'#000'}};
   a.splitLine={...a.splitLine,lineStyle:{...a.splitLine?.lineStyle,color:'#d0d0d0'}};
  });});
  if(option.radar)([].concat(option.radar)).forEach(a=>{a.axisLine={lineStyle:{color:'#000'}};a.splitLine={...a.splitLine,lineStyle:{color:'#d0d0d0'}};});
  const darken=style=>{if(style&&['#72a9bc','#0071ee','#4d74a0','#607e95','#a8c3d6'].includes(String(style.color).toLowerCase())){style.color='#064b86';style.opacity=Math.max(.75,style.opacity??1);}};
  ([].concat(option.series||[])).forEach(s=>{
   if(s.type==='scatter'){darken(s.itemStyle);darken(s.emphasis?.itemStyle);(s.data||[]).forEach(p=>darken(p?.itemStyle));}
   if(s.type==='line'&&(s.name==='回归线'||String(s.id||'').startsWith('road-fit-'))){s.lineStyle={...s.lineStyle,color:'#000',opacity:1};s.emphasis={...s.emphasis,lineStyle:{...s.emphasis?.lineStyle,color:'#000',opacity:1}};}
  });
  return setOption(option,...args);
 };
 charts.push(c);enableChartDownload(c,n);''')
    start=js.index("  if(mode){const canvas=document.createElement('canvas')")
    end=js.index("  D.points.forEach(p=>{if(!p.position)return;const n=",start)
    js=js[:start]+'''  if(mode){
   const width=1400,height=Math.round(width*.70638),sigma=width*.100;
   const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
   const ctx=canvas.getContext('2d'),values=new Float32Array(width*height);let peak=0;
   D.points.forEach(p=>{
    if(!p.position)return;const weight=Math.max(0,p.values.AH||0)/max;if(!weight)return;
    const cx=p.position.x_percent/100*width,cy=p.position.y_percent/100*height;
    for(let y=Math.max(0,Math.floor(cy-3*sigma));y<Math.min(height,cy+3*sigma);y++)for(let x=Math.max(0,Math.floor(cx-3*sigma));x<Math.min(width,cx+3*sigma);x++){
     const distance=(x-cx)**2+(y-cy)**2;if(distance>9*sigma*sigma)continue;
     const v=values[y*width+x]+=weight*Math.exp(-distance/(2*sigma*sigma));peak=Math.max(peak,v);
    }
   });
   const pixels=ctx.createImageData(width,height),colors=[[0,64,255],[0,180,255],[255,255,128],[255,128,0],[220,0,0]];
   values.forEach((v,i)=>{if(!v||!peak)return;const t=v/peak;if(t<.005)return;const f=t*4,j=Math.min(3,Math.floor(f));
    for(let k=0;k<3;k++)pixels.data[i*4+k]=colors[j][k]*(1-(f-j))+colors[j+1][k]*(f-j);
    pixels.data[i*4+3]=255*Math.min(.82,t*5);
   });
   ctx.putImageData(pixels,0,0);const image=document.createElementNS(NS,'image');image.setAttribute('href',canvas.toDataURL());image.setAttribute('width','1000');image.setAttribute('height','706.38');svg.append(image);
  }
'''+js[end:]
    js=js.replace('墨蓝色表示人数少，洋红色表示人数多','蓝色表示人数少，红色表示人数多')
    js=js.replace('σ=底图宽度的1.8%', 'σ=底图宽度的0.9%，以原始点位坐标为中心，核半径截断为3σ')
    return js
