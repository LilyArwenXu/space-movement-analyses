function caseStudy(kind){
 document.body.classList.remove('screen-analysis');document.body.classList.add('case-analysis');
 note('仅使用本组案例各自的节点 CSV 与行人 CSV。右侧同时显示本组所有点位；切换地址时高亮对应散点，悬停查看指标与数值。');
 const cases=D.cases[kind],nav=el('div','subtabs'),host=el('div'),groupPoints=cases.flatMap((example,caseIndex)=>example.analysis.points.map(p=>({...p,caseIndex,caseAddress:example.address})));let selectedX=0;
 tabs(nav,cases.map(c=>c.address),i=>{
  charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();
  const example=cases[i],analysis=example.analysis,layout=el('div','case-layout',host),left=el('div','case-photos',layout);
  example.photos.forEach(src=>{const figure=el('figure','',left),img=el('img','',figure);img.src=src;img.alt=example.address;el('figcaption','',figure).textContent=example.caption;});
  const links=el('div','case-links',left);example.csv.forEach((src,j)=>{const a=el('a','',links);a.href=src;a.textContent=j?'行人记录 CSV':'节点记录 CSV';a.download='';});
  const xkind=kind==='mismatch'?'vitality':'quality',ykind=kind==='qualityVitality'?'vitality':'mix',xdims=D.caseDimensions[xkind],ydims=D.caseDimensions[ykind];
  const below=el('section','case-scatter',layout);el('h2','section-heading',below).textContent='指标散点图 · '+example.address;
  const xnav=el('div','subtabs case-x-tabs',below),plotRow=el('div','case-plot-row',below),legend=el('div','case-legend',plotRow),plotHost=el('div','case-plot-host',plotRow),c=chart(plotHost,420),caption=el('p','caption',below);
  const score=ykind==='vitality'?'vitality':'mixScore',dimensions=[[score,ykind==='vitality'?'活力度综合评分':'混合度综合评分'],...ydims];
  const units={sample:'人',clusters:'个',density:'人/㎡',gather:'比例',resident:'指数',visitor:'指数',vitality:'评分',mixScore:'评分',ageMix:'指数',activityMix:'指数',identityMix:'指数',postureMix:'指数',socialMix:'指数'};
  legend.setAttribute('aria-label','纵轴指标图例');
  dimensions.forEach(([key,label],j)=>{const item=el('div','case-legend-item',legend),dot=el('span','case-legend-dot',item);dot.style.background=PALETTE[j%PALETTE.length];dot.setAttribute('aria-hidden','true');el('span','',item).textContent=label+'（'+units[key]+'）';});
  const previousX=selectedX;
  tabs(xnav,xdims.map(d=>d[1]),index=>{
   selectedX=index;
   const [x,xlabel]=xdims[index],getx=p=>(xkind==='quality'?p.values:p.metrics)[x],gety=(p,y)=>y===score?p[score]:p.metrics[y];
   const o=base();o.animation=true;o.animationDurationUpdate=600;o.grid={left:55,right:25,top:35,bottom:70,containLabel:true};o.xAxis=axis(xlabel);o.yAxis=axis('指标原始值（单位见图例）');
   const xs=groupPoints.map(getx).filter(finite);if(xs.length){const lo=Math.min(...xs),hi=Math.max(...xs),padding=Math.max((hi-lo)*.2,Math.max(Math.abs(lo),Math.abs(hi))*.05,.1);o.xAxis.min=lo-padding;o.xAxis.max=hi+padding;}
   o.legend={show:false};
   o.series=dimensions.map(([key,label],j)=>({id:'case-metric-'+key,name:label+'（'+units[key]+'）',type:'scatter',
    data:groupPoints.filter(p=>finite(getx(p))&&finite(gety(p,key))).sort((a,b)=>Number(a.caseIndex===i)-Number(b.caseIndex===i)).map(p=>({value:[getx(p),gety(p,key),p.caseAddress,p.id,p.caseIndex],symbolSize:p.caseIndex===i?17:10,itemStyle:{opacity:p.caseIndex===i?1:.3,borderWidth:0}})),
    itemStyle:{color:PALETTE[j%PALETTE.length],borderWidth:0},emphasis:{scale:1.4,itemStyle:{opacity:1,borderWidth:0},label:{show:false}},label:{show:false}}));
   if(!o.series.some(s=>s.data.length))o.graphic=[{type:'text',left:'center',top:'middle',style:{text:'本组案例均缺少“'+xlabel+'”，无法绘制该横轴下的散点',font:'16px Microsoft YaHei',fill:'#686868'}}];
   o.tooltip.formatter=p=>{const value=p.data.value||p.data;return esc(value[2])+'<br>'+esc(xlabel)+'：'+fmt(value[0])+'<br>'+esc(p.seriesName)+'：'+fmt(value[1]);};
   c.setOption(o,{notMerge:true});
   const missing=dimensions.filter(([key])=>!analysis.points.some(p=>finite(getx(p))&&finite(gety(p,key)))).map(d=>d[1]);
   caption.textContent='本组 '+cases.length+' 个案例点位同时显示；当前地址的点加大并加深，其余点保留为淡色。每种颜色对应一个纵轴指标；点上不显示文字，悬停查看地址和数值。横轴按同组全部点位统一取值并留出边距，切换地址不改变范围。不同指标单位不同，不按纵坐标高低比较优劣。'+(missing.length?'\n当前选中案例无法绘制：'+missing.join('、')+'。缺失值不填零，也不使用其他点位补足。':'')+'\n节点样本不足时，不绘制回归线或显著差异圈。';
  });
  if(previousX)xnav.children[previousX].click();
 });
}
