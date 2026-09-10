function chartScale(value){
 if(!finite(value))return '#fff';
 const stops=['#072e55','#0071ee','#72a9bc','#ffffff','#cd96be','#9c23ad','#c90097','#ff0051'],t=value<0?(value+1)*3:3+value*4,j=Math.min(stops.length-2,Math.max(0,Math.floor(t))),f=Math.max(0,Math.min(1,t-j));
 const rgb=h=>[1,3,5].map(k=>parseInt(h.slice(k,k+2),16)),a=rgb(stops[j]),b=rgb(stops[j+1]);return 'rgb('+a.map((v,k)=>Math.round(v+(b[k]-v)*f)).join(',')+')';
}
function compositionColor(k,count){
 const ordered=['#072e55','#4d74a0','#0071ee','#72a9bc','#9094c1','#6f52d4','#9c23ad','#cd96be','#c90097','#ff0051'];
 return ordered[count<=2?[2,7][k]:count<=4?[0,3,4,7][k]:k%ordered.length];
}
function coefficient(kind){
 const letter={mix:'M',quality:'Q',vitality:'V'}[kind],box=el('section','coefficients'),img=el('img','coefficient-image',box);img.src='../assets/data/coefficients/'+letter+'.png';img.alt=letter+' 系数表征';
 const defs=kind==='mix'?[['w1','年龄混合度',.149],['w2','活动丰富度',.141],['w3','姿态丰富度',.250],['w4','社交状态混合度',.228],['w5','身份倾向混合度',.233]]:D.scoreWeights[kind].map((d,i)=>[(kind==='quality'?'x':'y')+(i+1),d[1],d[2]]);
 const lower=el('div','coefficient-tables',box),left=el('section','',lower),right=el('section','',lower);
 const table=el('table','coefficient-table',left);table.innerHTML='<thead><tr><th>指标</th><th>系数</th><th>权重</th></tr></thead><tbody>'+defs.map(d=>'<tr><td>'+d[1]+'</td><td>'+d[0]+'</td><td>'+d[2].toFixed(3)+'</td></tr>').join('')+'</tbody>';
 const label={mix:'混合度',quality:'界面品质',vitality:'活力度'}[kind],key=kind==='mix'?'mixScore':kind;el('h2','section-heading',right).textContent=label+'总表';
 const wrap=el('div','score-table-wrap',right),scores=el('table','coefficient-table score-table',wrap);scores.innerHTML='<thead><tr><th>地址</th><th>'+label+'</th></tr></thead><tbody>'+D.points.map(p=>'<tr><td>'+esc(p.address)+'</td><td>'+fmt(p[key],6)+'</td></tr>').join('')+'</tbody>';
 note(kind==='mix'?MFORM+'\n权重说明保留给定w1–w5名称；综合评分按指定M公式的维度顺序代入。':SFORM+'\n'+D.scoreWeights[kind].map(d=>d[1]+' '+d[2].toFixed(3)).join('；'));
}
function dimensionBars(i){
 const d=D.mixDimensions[i],points=D.points,c=chart(W,Math.max(650,points.length*28+140)),o=base();
 o.animation=true;o.title={text:d.label,left:'center',textStyle:{fontFamily:FONT,fontSize:18}};o.legend={type:'scroll',top:35,textStyle:{fontFamily:FONT}};o.grid={left:220,right:125,top:90,bottom:50};
 o.xAxis={...axis('类别权重 pₖ'),min:0,max:1,axisLabel:{formatter:v=>Math.round(v*100)+'%'}};o.yAxis={type:'category',inverse:true,data:points.map(p=>p.name+' · '+p.id),axisLabel:{interval:0,fontFamily:FONT,fontSize:12},axisTick:{show:false}};
 o.series=d.labels.map((name,k)=>({name,type:'bar',stack:'frequency',barWidth:18,itemStyle:{color:compositionColor(k,d.labels.length),borderColor:'#fff',borderWidth:.4,decal:k>=10?{symbol:'rect',dashArrayX:[1,3],dashArrayY:[2,5],color:'rgba(255,255,255,.5)'}:undefined},data:points.map(p=>{const a=p.mixCounts[d.key],sum=a.reduce((s,v)=>s+(v||0),0);return finite(p.metrics[d.key])?a[k]/sum:null})}));
 o.series.push({type:'scatter',name:d.label,symbolSize:0,silent:true,data:points.map((p,i)=>[1,i,p.metrics[d.key]]),label:{show:true,position:'right',distance:12,fontFamily:FONT,color:INK,formatter:p=>d.label.replace('混合度','H').replace('丰富度','H')+' = '+fmt(p.data[2])}});
 o.tooltip.formatter=p=>{const node=points[p.dataIndex],a=node.mixCounts[d.key];return esc(node.address)+' · '+esc(node.id)+'<br>'+d.labels.map((n,k)=>esc(n)+'：'+fmt(a[k])).join('<br>')+'<br>'+d.label+'：'+fmt(node.metrics[d.key])};c.setOption(o);
 note(d.label+'：纵轴为点位地址，横轴为类别频数占该维频数合计的权重。\nH_d=−Σ(p_k×ln p_k)/ln K_d；p_k=该类别频数/该维频数合计；K_d='+d.labels.length+'；0×ln0记0。全量总表缺失值或零合计不计算，右侧显示 —。\n'+(i===4?'身份倾向权重采用全量总表居民指数、游客指数的相对值。':'数据来自全量总表，不按行人记录重新推断。'));
}
function allPointRadar(parent){
 const dims=D.mixDimensions,pts=D.points.filter(p=>dims.every(d=>finite(p.metrics[d.key]))),c=chart(parent,760),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;
 const color=i=>PALETTE[i%PALETTE.length];
 o.animation=true;o.radar={indicator:dims.map(d=>({name:d.label,max:1})),center:['50%','54%'],radius:'57%',splitNumber:4,axisName:{fontFamily:FONT,color:INK},splitArea:{show:false}};
 o.legend={type:'scroll',top:15,left:20,right:20,data:pts.map(p=>p.name+' · '+p.id),textStyle:{fontFamily:FONT},selector:[{type:'all',title:'全选'},{type:'inverse',title:'反选'}]};
 o.series=pts.map((p,i)=>({type:'radar',name:p.name+' · '+p.id,data:[{name:p.name+' · '+p.id,value:dims.map(d=>p.metrics[d.key])}],symbol:['circle','rect','triangle','diamond'][Math.floor(i/10)%4],symbolSize:4,lineStyle:{width:1,opacity:.28,type:['solid','dashed','dotted'][Math.floor(i/40)%3],color:new echarts.graphic.LinearGradient(0,0,1,1,[{offset:0,color:color(i)},{offset:1,color:color((i+1)%pts.length)}])},itemStyle:{color:color(i)},areaStyle:{opacity:0},emphasis:{focus:'series',lineStyle:{width:3,opacity:1},itemStyle:{opacity:1}},blur:{lineStyle:{opacity:.04},itemStyle:{opacity:.08}}}));
 o.tooltip.formatter=p=>esc(pts[p.seriesIndex].address)+' · '+esc(pts[p.seriesIndex].id)+'<br>'+dims.map((d,i)=>d.label+'：'+fmt(p.value[i])).join('<br>');
 c.setOption(o);c.on('click',p=>{c.dispatchAction({type:'downplay'});c.dispatchAction({type:'highlight',seriesIndex:p.seriesIndex});});
 el('p','caption',parent).textContent='所有有效点位叠加在同一个五维雷达图。图例支持筛选；悬停或点击突出点位。连线由本点位颜色渐变到下一点位颜色（按总表顺序）。缺失任一维度的点位不绘制。';
}
function mixedTotal(){
 informationExplorer(W,'mix');const nav=W.querySelector('.subtabs'),host=nav.nextElementSibling,button=el('button','',nav);button.textContent='雷达图';button.setAttribute('role','tab');button.setAttribute('aria-selected','false');let radarHost=null;
 const original=[...nav.children].slice(0,2);original.forEach(b=>{const click=b.onclick;b.onclick=()=>{if(radarHost){radarHost.querySelectorAll('.plot').forEach(n=>echarts.getInstanceByDom(n)?.dispose());charts=charts.filter(c=>!c.isDisposed());radarHost.remove();}radarHost=null;host.hidden=false;click();charts.filter(c=>!c.isDisposed()).forEach(c=>c.resize());host.animate([{opacity:0},{opacity:1}],{duration:500})}});
 button.onclick=()=>{nav.querySelectorAll('button').forEach(b=>b.setAttribute('aria-selected',String(b===button)));host.hidden=true;if(!radarHost){radarHost=el('div','radar-host');allPointRadar(radarHost);}radarHost.animate([{opacity:0,transform:'translateY(16px)'},{opacity:1,transform:'none'}],{duration:550});note(MFORM)};
}
function effectAnalysis(){note('横轴：行人样本数；纵轴分别为视觉丰富度、历史感知度、路面状态、界面开放度、临界互动性。沿用道路联动和OLS回归。');const grid=el('div','chart-grid');[['Y','视觉丰富度'],['Z','历史感知度'],['AA','路面状态'],['U','界面开放度'],['V','临界互动性']].forEach(([k,t])=>scatter(grid,'AH',k,t));}
function matrixWithAxes(){
 covarianceMatrix();const wrap=W.querySelector('.covariance'),ys=Object.keys(D.ys),grid=wrap.querySelector('.covariance-grid');
 const top=el('div','matrix-column-labels',wrap);top.style.gridTemplateColumns='repeat('+ys.length+',1fr)';ys.forEach(k=>el('span','',top).textContent=D.ys[k]);
 const left=el('div','matrix-row-labels',wrap);left.style.gridTemplateRows='repeat('+D.fields.length+',1fr)';D.fields.forEach(f=>el('span','',left).textContent=f.label);
 const texts={
 'O:visitor':'节点的功能混合度越高，游客到访指数反而越低，游客更偏好功能相对纯粹的场所。',
 'R:resident':'商业消费类空间能够为本地居民提供日常活动载体，有效提升本地人群的到访意愿。',
 'R:activityMix':'消费型停留空间占比越高，活动丰富度和社交状态混合度越高。消费型停留空间可容纳不同社交模式的人群，支持更加多样化的停留行为。',
 'R:socialMix':'消费型停留空间占比越高，活动丰富度和社交状态混合度越高。消费型停留空间可容纳不同社交模式的人群，支持更加多样化的停留行为。',
 'Q:density':'行人不倾向于聚集在人均消费水平过高的场所。',
 'T:resident':'界面整体状态得分越高，居民到访指数反而越低。部分经过品质美化的街道界面，存在脱离居民真实使用需求的问题。',
 'U:ageMix':'开放度高的街道界面可以适配不同年龄群体的使用，有利于实现多元年龄人群的共存。',
 'V:gather':'临街互动性越高，人群集聚比例越低，活动大多以独立形式发生。',
 'AA:activityMix':'二者呈负相关，路面状态越好，行人的活动丰富度越低。'};
 const tooltip=el('aside','correlation-explanation',wrap);tooltip.id='correlation-explanation';tooltip.setAttribute('role','tooltip');tooltip.hidden=true;
 [...grid.children].forEach((cell,i)=>{const f=D.fields[Math.floor(i/ys.length)],k=ys[i%ys.length],r=D.correlations.find(r=>r.x===f.key&&r.y===k);cell.textContent=fmt(r.rho,2)+stars(r.p);cell.dataset.pair=f.key+':'+k;const value=chartScale(r.rho),rgb=(value.match(/\d+/g)||[255,255,255]).map(Number);cell.style.setProperty('color',rgb[0]*.299+rgb[1]*.587+rgb[2]*.114<135?'#fff':'#111','important');if(finite(r.p)&&r.p<.05)cell.classList.add('significant');
  const text=texts[cell.dataset.pair];if(text){cell.setAttribute('aria-describedby',tooltip.id);const show=()=>{tooltip.textContent=f.label+' × '+D.ys[k]+'\n'+text;tooltip.hidden=false;const rect=cell.getBoundingClientRect();tooltip.style.left=Math.max(12,Math.min(rect.left,window.innerWidth-384))+'px';tooltip.style.top=Math.max(12,Math.min(rect.bottom+10,window.innerHeight-tooltip.offsetHeight-12))+'px';};cell.addEventListener('pointerenter',show);cell.addEventListener('focus',show);cell.addEventListener('pointerleave',()=>tooltip.hidden=true);cell.addEventListener('blur',()=>tooltip.hidden=true);}
 });
 const legend=el('div','heat-legend correlation-legend');legend.innerHTML='负相关 −1 <span class="correlation-gradient"></span> 正相关 +1';
 el('p','caption').textContent='横坐标：'+ys.map(k=>D.ys[k]).join('、')+'。纵坐标：'+D.fields.map(f=>f.label).join('、')+'。黑色实线方框表示 p<0.05，保留 * / ** / ***。';
}
function shapAnalysis(label){
 const content=window.SHAP_CAPTIONS, single=label==='高活力度低混合度';
 el('h2','section-heading').textContent=label;
 const gallery=el('section','shap-gallery'),host=single?el('div','shap-triptych',gallery):gallery;
 const lines=s=>s.replace(/([；;。])\s*/g,'$1\n').trim();
 [1,2,3].forEach((number,index)=>{
  const figure=el('figure','shap-figure',host),row=single?figure:el('div','shap-row',figure),img=el('img','shap-image',row);
  img.src='../assets/data/shap/'+label+'/'+number+'.png';img.alt=label+' · '+number+'.png';
  let description=content.descriptions[index];
  if(index===2&&['高混合度低界面品质','高混合度低活力度','高活力度低混合度'].includes(label))description=description.replace('第三维变量不配得性U','第三维变量'+(label==='高活力度低混合度'?'U（不配得性）':'U（不配得性）'));
  const side=el(single?'figcaption':'aside',single?'shap-bottom':'shap-side',single?figure:row);side.textContent=lines(description);
  if(!single){
   side.textContent+='\n\n'+lines(content.groups[label][index]);
   const fit=()=>{
    if(!img.isConnected){observer.disconnect();return;}
    img.style.minHeight='';
    if(window.innerWidth>800)img.style.minHeight=side.scrollHeight+'px';
    side.style.setProperty('--image-height',img.getBoundingClientRect().height+'px');
   };
   img.addEventListener('load',fit);const observer=new ResizeObserver(fit);observer.observe(row);
  }
 });
 if(single)el('p','shap-conclusion',gallery).textContent=content.singleConclusion;
 note('');
}
function mismatchView(i){
 const config={qualityVitality:['quality','vitality','界面品质','活力度','界面品质的底层指标组合','活力度的底层指标'],qualityMix:['quality','mixScore','界面品质','混合度','界面品质的底层指标组合','混合度的底层指标'],mismatch:['vitality','mixScore','活力度','混合度','活力度的底层指标组合','混合度的底层指标']}[PAGE], [x,y,xlabel,ylabel,first,second]=config;
 const labels=PAGE==='mismatch'?['高混合度低活力度','高活力度低混合度']:['高'+xlabel+'低'+ylabel,'高'+ylabel+'低'+xlabel],mx=D.scoreMeans[x],my=D.scoreMeans[y];
 if(i){sectionTabs(labels,j=>shapAnalysis(labels[j]));return;}
 const c=chart(W,610),o=base();delete o.legend;o.grid={left:75,right:55,top:45,bottom:65};
 o.xAxis={...axis(xlabel),scale:true,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};o.yAxis={...axis(ylabel),scale:true,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};
 const pts=D.points.filter(p=>finite(p[x])&&finite(p[y]));o.series=[{type:'scatter',id:'nodes',data:pts.map(p=>({value:[p[x],p[y],p.address,p.id],itemStyle:{color:p.mismatchGroups[PAGE]===labels[0]?'#0071ee':p.mismatchGroups[PAGE]===labels[1]?'#c90097':'#9094c1',opacity:p.mismatchGroups[PAGE]?.85:.4}})),symbolSize:9,z:5,emphasis:{scale:1.6},markLine:{silent:true,symbol:'none',label:{show:true,position:'insideEndTop',formatter:p=>p.data.name,color:'#000',backgroundColor:'#fff',padding:3},lineStyle:{color:'#000',type:'solid',width:1.5},data:[{xAxis:mx,name:xlabel+'均值 '+fmt(mx,4)},{yAxis:my,name:ylabel+'均值 '+fmt(my,4)}]}}];
 o.tooltip.formatter=p=>{const a=p.value;return esc(a[2])+' · '+esc(a[3])+'<br>'+xlabel+'：'+fmt(a[0])+'<br>'+ylabel+'：'+fmt(a[1])};c.setOption(o);
 note('横轴：'+xlabel+'；纵轴：'+ylabel+'。按各指标全域有效评分的平均值划分四象限：'+xlabel+'均值='+fmt(mx,6)+'，'+ylabel+'均值='+fmt(my,6)+'。左上与右下两类点位纳入不配得性分析，等于均值归高组。\nQ、V、M与各总表综合评分完全一致，缺失评分不参与筛选。');el('p','caption').textContent=labels.map(label=>label+'：'+D.points.filter(p=>p.mismatchGroups[PAGE]===label).length+' 个点位').join('；');
}
if(PAGE==='heat')mainTabs(['热力分布图','样本数'],i=>mapView(1-i));
if(PAGE==='weights')mainTabs(['空间分析','系数表征','界面品质总表'],i=>{if(i===2)informationExplorer(W,'quality');else if(i===1)coefficient('quality');else sectionTabs(['有效空间分析','舒适度分析','效果分析'],j=>j<2?space(j):effectAnalysis());});
if(PAGE==='composition')mainTabs(['构成分析','系数表征','混合度总表'],i=>i===0?sectionTabs(D.mixDimensions.map(d=>d.label),dimensionBars):i===1?coefficient('mix'):mixedTotal());
if(PAGE==='memory')mainTabs(['系数表征','活力度总表'],i=>i?informationExplorer(W,'vitality'):coefficient('vitality'));
if(PAGE==='correlations')mainTabs(['空间行为相关性分析'],matrixWithAxes);
if(['qualityVitality','qualityMix','mismatch'].includes(PAGE))mainTabs(['筛选','不配得性分析'],mismatchView);
