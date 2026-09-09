function coefficient(kind){
 const letter={mix:'M',quality:'Q',vitality:'V'}[kind],box=el('section','coefficients'),img=el('img','coefficient-image',box);img.src='../assets/data/coefficients/'+letter+'.png';img.alt=letter+' 系数表征';
 const defs=kind==='mix'?[['w1','年龄混合度',.149],['w2','活动丰富度',.141],['w3','姿态丰富度',.250],['w4','社交状态混合度',.228],['w5','身份倾向混合度',.233]]:D.scoreWeights[kind].map((d,i)=>[(kind==='quality'?'x':'y')+(i+1),d[1],d[2]]);
 const table=el('table','coefficient-table',box);table.innerHTML='<thead><tr><th>指标</th><th>系数</th><th>权重</th></tr></thead><tbody>'+defs.map(d=>'<tr><td>'+d[1]+'</td><td>'+d[0]+'</td><td>'+d[2].toFixed(3)+'</td></tr>').join('')+'</tbody>';
 note(kind==='mix'?MFORM+'\n权重说明保留给定w1–w5名称；综合评分按指定M公式的维度顺序代入。':SFORM+'\n'+D.scoreWeights[kind].map(d=>d[1]+' '+d[2].toFixed(3)).join('；'));
}
function dimensionBars(i){
 const d=D.mixDimensions[i],points=D.points,c=chart(W,Math.max(650,points.length*28+140)),o=base();
 o.animation=true;o.title={text:d.label,left:'center',textStyle:{fontFamily:FONT,fontSize:18}};o.legend={type:'scroll',top:35,textStyle:{fontFamily:FONT}};o.grid={left:220,right:125,top:90,bottom:50};
 o.xAxis={...axis('类别权重 pₖ'),min:0,max:1,axisLabel:{formatter:v=>Math.round(v*100)+'%'}};o.yAxis={type:'category',inverse:true,data:points.map(p=>p.name+' · '+p.id),axisLabel:{interval:0,fontFamily:FONT,fontSize:12},axisTick:{show:false}};
 o.series=d.labels.map((name,k)=>({name,type:'bar',stack:'frequency',barWidth:18,itemStyle:{color:['#607E95','#A45668','#8C793E','#497F73','#806A96','#BD7546','#A8C3D6','#D59BA8','#B7AB7A','#84B4A6','#B0A1C2','#D5AD8F','#59646C','#A59E93'][k]},data:points.map(p=>{const a=p.mixCounts[d.key],sum=a.reduce((s,v)=>s+(v||0),0);return finite(p.metrics[d.key])?a[k]/sum:null})}));
 o.series.push({type:'scatter',name:d.label,symbolSize:0,silent:true,data:points.map((p,i)=>[1,i,p.metrics[d.key]]),label:{show:true,position:'right',distance:12,fontFamily:FONT,color:INK,formatter:p=>d.label.replace('混合度','H').replace('丰富度','H')+' = '+fmt(p.data[2])}});
 o.tooltip.formatter=p=>{const node=points[p.dataIndex],a=node.mixCounts[d.key];return esc(node.address)+' · '+esc(node.id)+'<br>'+d.labels.map((n,k)=>esc(n)+'：'+fmt(a[k])).join('<br>')+'<br>'+d.label+'：'+fmt(node.metrics[d.key])};c.setOption(o);
 note(d.label+'：纵轴为点位地址，横轴为类别频数占该维频数合计的权重。\nH_d=−Σ(p_k×ln p_k)/ln K_d；p_k=该类别频数/该维频数合计；K_d='+d.labels.length+'；0×ln0记0。全量总表缺失值或零合计不计算，右侧显示 —。\n'+(i===4?'身份倾向权重采用全量总表居民指数、游客指数的相对值。':'数据来自全量总表，不按行人记录重新推断。'));
}
function allPointRadar(parent){
 const dims=D.mixDimensions,pts=D.points.filter(p=>dims.every(d=>finite(p.metrics[d.key]))),c=chart(parent,760),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;
 const color=i=>'hsl('+Math.round(i*137.508%360)+',43%,46%)';
 o.animation=true;o.radar={indicator:dims.map(d=>({name:d.label,max:1})),center:['50%','54%'],radius:'57%',splitNumber:4,axisName:{fontFamily:FONT,color:INK},splitArea:{show:false}};
 o.legend={type:'scroll',top:15,left:20,right:20,data:pts.map(p=>p.name+' · '+p.id),textStyle:{fontFamily:FONT},selector:[{type:'all',title:'全选'},{type:'inverse',title:'反选'}]};
 o.series=pts.map((p,i)=>({type:'radar',name:p.name+' · '+p.id,data:[{name:p.name+' · '+p.id,value:dims.map(d=>p.metrics[d.key])}],symbolSize:4,lineStyle:{width:1,opacity:.28,color:new echarts.graphic.LinearGradient(0,0,1,1,[{offset:0,color:color(i)},{offset:1,color:color((i+1)%pts.length)}])},itemStyle:{color:color(i)},areaStyle:{opacity:0},emphasis:{focus:'series',lineStyle:{width:3,opacity:1},itemStyle:{opacity:1}},blur:{lineStyle:{opacity:.04},itemStyle:{opacity:.08}}}));
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
 [...grid.children].forEach((cell,i)=>{const f=D.fields[Math.floor(i/ys.length)],k=ys[i%ys.length],r=D.correlations.find(r=>r.x===f.key&&r.y===k);cell.textContent=fmt(r.rho,2)+stars(r.p);if(finite(r.p)&&r.p<.05)cell.classList.add('significant');});
 el('p','caption').textContent='横坐标：'+ys.map(k=>D.ys[k]).join('、')+'。纵坐标：'+D.fields.map(f=>f.label).join('、')+'。黑色实线方框表示 p<0.05，保留 * / ** / ***。';
}
function mismatchView(i){
 const config={qualityVitality:['quality','vitality','界面品质','活力度','界面品质的底层指标组合','活力度的底层指标'],qualityMix:['quality','mixScore','界面品质','混合度','界面品质的底层指标组合','混合度的底层指标'],mismatch:['vitality','mixScore','活力度','混合度','活力度的底层指标组合','混合度的底层指标']}[PAGE], [x,y,xlabel,ylabel,first,second]=config;
 const labels=['高'+ylabel+'低'+xlabel,'高'+xlabel+'低'+ylabel];
 if(i){sectionTabs(labels,j=>{const selected=D.points.filter(p=>p.mismatchGroups[PAGE]===labels[j]);el('h2','section-heading').textContent=labels[j]+'，研究'+(j?second:first)+'对不配得性的影响';el('p','caption').textContent='筛选点位 '+selected.length+' 个';const list=el('ul','selected-points');selected.forEach(p=>el('li','',list).textContent=p.address+' · '+p.id+' ｜ '+xlabel+' '+fmt(p[x])+' / '+ylabel+' '+fmt(p[y]));note('两类点位使用相同筛选规则和最终综合评分。后续分析图表暂不制作。');});return;}
 const c=chart(W,610),o=base();delete o.legend;o.grid={left:75,right:55,top:45,bottom:65};
 o.xAxis={...axis(xlabel),min:0,max:1,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};o.yAxis={...axis(ylabel),min:0,max:1,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};
 const pts=D.points.filter(p=>finite(p[x])&&finite(p[y]));o.series=[{type:'scatter',id:'nodes',data:pts.map(p=>({value:[p[x],p[y],p.address,p.id],itemStyle:{color:p.mismatchGroups[PAGE]===labels[0]?'#607E95':p.mismatchGroups[PAGE]===labels[1]?'#A45668':'#B8AEA6',opacity:p.mismatchGroups[PAGE]?.85:.4}})),symbolSize:9,z:5,emphasis:{scale:1.6},markLine:{silent:true,symbol:'none',label:{show:false},lineStyle:{color:'#000',type:'solid',width:1.5},data:[{xAxis:.5},{yAxis:.5}]}}];
 o.tooltip.formatter=p=>{const a=p.value;return esc(a[2])+' · '+esc(a[3])+'<br>'+xlabel+'：'+fmt(a[0])+'<br>'+ylabel+'：'+fmt(a[1])};c.setOption(o);
 note('横轴：'+xlabel+'；纵轴：'+ylabel+'。黑色十字轴在0.5居中划分四象限；左上与右下两类点位纳入不配得性分析。\nQ、V、M与各总表综合评分完全一致，缺失评分不参与筛选。');el('p','caption').textContent=labels.map(label=>label+'：'+D.points.filter(p=>p.mismatchGroups[PAGE]===label).length+' 个点位').join('；');
}
if(PAGE==='heat')mainTabs(['热力分布图','样本数'],i=>mapView(1-i));
if(PAGE==='weights')mainTabs(['空间分析','界面品质总表'],i=>{if(i)informationExplorer(W,'quality');else sectionTabs(['有效空间分析','舒适度分析','系数表征','效果分析'],j=>j<2?space(j):j===2?coefficient('quality'):effectAnalysis());});
if(PAGE==='composition')mainTabs([...D.mixDimensions.map(d=>d.label),'系数表征','混合度总表'],i=>i<5?dimensionBars(i):i===5?coefficient('mix'):mixedTotal());
if(PAGE==='memory')mainTabs(['系数表征','活力度总表'],i=>i?informationExplorer(W,'vitality'):coefficient('vitality'));
if(PAGE==='correlations')mainTabs(['空间行为相关性分析'],matrixWithAxes);
if(['qualityVitality','qualityMix','mismatch'].includes(PAGE))mainTabs(['筛选','不配得性分析'],mismatchView);
