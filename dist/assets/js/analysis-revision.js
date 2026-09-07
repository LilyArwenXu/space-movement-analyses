/* Revision functions are inserted into each editable renderer before page initialization. */
const MIXLABELS=['年龄混合度','活动丰富度','身份倾向混合度','姿态丰富度','社交状态混合度'];
function fittedRegression(data){
 const a=data.filter(p=>finite(p[0])&&finite(p[1])),n=a.length;if(n<3)return null;
 const mx=a.reduce((s,p)=>s+p[0],0)/n,my=a.reduce((s,p)=>s+p[1],0)/n;
 const xx=a.reduce((s,p)=>s+(p[0]-mx)**2,0),yy=a.reduce((s,p)=>s+(p[1]-my)**2,0);if(xx<=0)return null;
 const slope=a.reduce((s,p)=>s+(p[0]-mx)*(p[1]-my),0)/xx,intercept=my-slope*mx;
 const residual=a.reduce((s,p)=>s+(p[1]-intercept-slope*p[0])**2,0),r2=yy>0?Math.max(0,Math.min(1,1-residual/yy)):null;
 const lo=Math.min(...a.map(p=>p[0])),hi=Math.max(...a.map(p=>p[0]));
 return {n,r2,slope,intercept,points:Array.from({length:61},(_,i)=>{const x=lo+(hi-lo)*i/60;return [x,intercept+slope*x,Math.sqrt(residual/(n-2)*(1/n+(x-mx)**2/xx))]})};
}
function regressionSeries(f,band=0,alwaysPink=false){if(!f)return [];
 const series=[{id:'regression',type:'line',silent:true,showSymbol:false,data:f.points.map(p=>p.slice(0,2)),lineStyle:{color:alwaysPink||f.r2>=.5?'#A45668':'#D59BA8',type:alwaysPink||f.r2>=.5?'solid':'dashed',width:2},z:3}];
 if(band>0)series.push({id:'regression-band',type:'custom',silent:true,data:[0],z:0,renderItem:(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+band*p[2]])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-band*p[2]]))]},style:{fill:'#D59BA8',opacity:.22}})});
 return series;
}
function linkedNodeCharts(){const active=charts.slice();active.forEach(c=>{c.setOption({series:[{id:'nodes',emphasis:{scale:1.6,itemStyle:{opacity:1},label:{show:true,position:'top',formatter:p=>p.data[2],fontFamily:FONT,color:'#292929',backgroundColor:'rgba(255,255,255,.9)',padding:3}}}]});
 c.on('mouseover',p=>{if(p.seriesId!=='nodes'&&p.seriesIndex!==0)return;const id=p.data[3];active.forEach(other=>{other.dispatchAction({type:'downplay'});const nodes=other.getOption().series.find(s=>s.id==='nodes');const index=nodes.data.findIndex(v=>v[3]===id);if(index>=0)other.dispatchAction({type:'highlight',seriesId:'nodes',dataIndex:index});});});
 c.on('globalout',()=>active.forEach(other=>other.dispatchAction({type:'downplay'})));});}
function vitalityInformation(){
 const nav=el('div','subtabs'),host=el('div'),c=informationScatter(host,'vitality'),original=c.getOption();host.querySelector('.caption').textContent='颜色区分指标；悬停显示原始数值及点位名称。校准展示以点大小编码该指标的相对大小，散点图以各自独立纵轴编码原始数值。';
 const keys=['sample','clusters','density','gather','resident','visitor'],labels=[...keys.map(k=>D.ys[k]),'综合评分'],values=keys.map(k=>D.points.map(p=>p.metrics[k]));values.push(D.points.map(p=>p.vitality));let mode=0;
 c.off('mouseover');c.off('globalout');
 tabs(nav,['校准展示','散点图'],i=>{mode=i;const compact=window.innerWidth<700,step=compact?24:42;
 const axes=i?labels.map((name,j)=>({id:'metric-'+j,type:'value',min:'dataMin',max:'dataMax',position:j<4?'left':'right',offset:(j<4?j:j-4)*step,name:String(j+1),nameLocation:'end',nameTextStyle:{color:PALETTE[j],fontFamily:FONT},axisLine:{show:true,lineStyle:{color:PALETTE[j]}},axisLabel:{fontSize:compact?8:10,color:'#4B4B4B',formatter:v=>Number(v.toPrecision(3)).toString()},splitLine:{show:false}})):original.yAxis;
 const series=labels.map((name,j)=>({id:'info-'+j,type:'scatter',name,yAxisIndex:i?j:0,data:values[j].map((v,k)=>({id:String(D.points[k].id),value:[k,i?v:j,v]})),symbolSize:i?(v=>finite(v[2])?(j===6?10:7):0):original.series[j].symbolSize,itemStyle:{color:PALETTE[j],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}}}));
 series.push({id:'focus-ring',type:'scatter',yAxisIndex:i?6:0,data:[]});
 c.setOption({animation:true,animationDurationUpdate:850,animationEasingUpdate:'cubicInOut',grid:{left:i?step*3+40:150,right:i?step*2+40:25,top:40,bottom:50},yAxis:axes,series}, {replaceMerge:'yAxis'});
 note((i?'七组散点叠加，各指标使用独立纵轴，轴号1–7依次对应：'+labels.join('、')+'。每组纵轴均从小到大，不能直接比较不同指标的绝对高度。':'每列代表一个节点，每行代表一个指标，圆点大小显示该行相对大小。')+'\n悬停联动同点位，综合评分加外圈；切换视图时点位平滑移动。\n'+SFORM);
 });
 c.on('mouseover',p=>{if(p.seriesIndex>=7)return;const i=p.data.value?p.data.value[0]:p.data[0];c.dispatchAction({type:'downplay'});labels.forEach((_,j)=>c.dispatchAction({type:'highlight',seriesIndex:j,dataIndex:i}));c.setOption({series:[{id:'focus-ring',data:finite(values[6][i])?[[i,mode?values[6][i]:6]]:[]}]});});
 c.on('globalout',()=>{c.dispatchAction({type:'downplay'});c.setOption({series:[{id:'focus-ring',data:[]}]});});
 c.setOption({tooltip:{formatter:p=>{const i=(p.data.value||p.data)[0];return esc(D.points[i].address)+'<br>'+labels.map((name,j)=>esc(name)+'：'+fmt(values[j][i])).join('<br>')}}});
}
function informationScatter(parent,kind){
 const mix=kind==='mix',keys=mix?['ageMix','activityMix','identityMix','postureMix','socialMix']:['sample','clusters','density','gather','resident','visitor'],labels=[...keys.map(k=>D.ys[k]),'综合评分'];
 const c=chart(parent,Math.max(440,Math.min(650,window.innerHeight*.68))),o=base();delete o.legend;
 o.grid={left:150,right:25,top:25,bottom:50};o.xAxis={type:'category',data:D.points.map(p=>p.name),axisLabel:{show:false},axisTick:{show:false},name:'所有点位（按总表顺序）',nameLocation:'middle',nameGap:28};
 o.yAxis={type:'category',data:labels,inverse:true,axisLabel:{color:'#4B4B4B',fontFamily:FONT,fontSize:12,interval:0},axisTick:{show:false},splitLine:{show:true,lineStyle:{color:'#F3EEE8'}}};
 const values=keys.map(k=>D.points.map(p=>p.metrics[k]));values.push(D.points.map(p=>p[mix?'mixScore':'vitality']));
 const ranges=values.map(a=>{const v=a.filter(finite);return [Math.min(...v),Math.max(...v)]});
 o.series=labels.map((name,j)=>({id:'info-'+j,name,type:'scatter',data:values[j].map((v,i)=>[i,j,v]),symbolSize:v=>{if(!finite(v[2]))return 0;const [lo,hi]=ranges[j];return 5+9*Math.sqrt(hi>lo?(v[2]-lo)/(hi-lo):.5)},itemStyle:{color:PALETTE[j%7],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}},blur:{itemStyle:{opacity:.5}}}));
 o.series.push({id:'focus-ring',type:'scatter',silent:true,data:[],symbolSize:27,itemStyle:{color:'transparent',borderColor:PALETTE[6],borderWidth:2,opacity:1},z:10});
 o.tooltip.formatter=p=>{const i=p.data[0],node=D.points[i];return esc(node.address)+'<br>'+labels.map((name,j)=>esc(name)+'：'+fmt(values[j][i])).join('<br>')};c.setOption(o);
 c.on('mouseover',p=>{if(p.seriesIndex>=labels.length)return;const i=p.data[0];c.dispatchAction({type:'downplay'});labels.forEach((_,j)=>c.dispatchAction({type:'highlight',seriesIndex:j,dataIndex:i}));c.setOption({series:[{id:'focus-ring',data:finite(values.at(-1)[i])?[[i,labels.length-1]]:[]}]});});
 c.on('globalout',()=>{c.dispatchAction({type:'downplay'});c.setOption({series:[{id:'focus-ring',data:[]}]});});
 el('p','caption',parent).textContent='每列为一个节点，圆点大小表示该行指标的相对大小，颜色区分指标；悬停同一节点联动，综合评分加外圈。缺失值不绘制。\n点半径按该行指标的最小最大值标准化后平方根缩放，原始数值见悬停信息。';
 return c;
}
function mixingInformation(){
 const nav=el('div','subtabs'),host=el('div');tabs(nav,['全域与所有街道',...D.admins.map(g=>g.name)],i=>{
  charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();
  note('雷达图越外扩，该维越多样；选择街道后点击道路可展开道路及各节点。\n'+MFORM);
  const groups=i?[D.admins[i-1],...D.admins[i-1].roads]:[D.all,...D.admins];const c=radar(host,groups,i?D.admins[i-1].name:'全域与所有街道');
  if(!i){const button=el('button','',host);button.textContent='信息散点图';const detail=el('section','drill',host);button.onclick=()=>{while(charts.length>1)charts.pop().dispose();detail.replaceChildren();el('h2','section-heading',detail).textContent='混合度信息散点图';el('p','caption',detail).textContent=MFORM;informationExplorer(detail,'mix');detail.scrollIntoView({behavior:'smooth',block:'start'})};return;}
  const admin=D.admins[i-1],buttons=el('div','road-buttons',host),drill=el('section','drill',host);
  function open(road){while(charts.length>1)charts.pop().dispose();drill.replaceChildren();el('h2','section-heading',drill).textContent=road;const group=admin.roads.find(g=>g.name===road),pts=D.points.filter(p=>p.admin===admin.name&&p.road===road&&p.n),grid=el('div','chart-grid',drill);radar(el('div','',grid),[group,...pts],road+'及各点位',480);lorenz(el('div','',grid),group);scorePlot(el('div','',grid),pts,'mixScore','点位混合度综合评分');el('p','caption',drill).textContent=MFORM;drill.scrollIntoView({behavior:'smooth',block:'start'})}
  admin.roads.forEach(g=>{const b=el('button','',buttons);b.textContent=g.name;b.onclick=()=>open(g.name)});c.on('legendselectchanged',p=>{if(admin.roads.some(g=>g.name===p.name)){c.dispatchAction({type:'legendSelect',name:p.name});open(p.name)}});c.on('click',p=>{if(admin.roads.some(g=>g.name===p.name))open(p.name)});
 });
}
function covarianceMatrix(){
 note('颜色由蓝到玫红表示负相关到正相关，近零为浅色。悬停格子时显示指标名称、系数、显著性和有效样本数。\nρ=两变量平均秩的Pearson相关系数；逐对排除缺失，并列值取平均秩。\nB1编码：无退让a=0、局部c=1、区域b=2、整体d=3；B2可视度a/b/c/d=0/1/2/3。\nB3a、b、c分别为对应构件子类出现数量；C尺度层级按C1至C4编码1至4。\n附属设施加权指数采用当前源表已计算的加权指数；未记录保留缺失。\n* p<0.05，** p<0.01，*** p<0.001，双侧近似检验，未做多重校正。');
 const wrap=el('div','covariance'),ys=Object.keys(D.ys),rows=D.fields.length,cols=ys.length;wrap.style.setProperty('--cols',cols);wrap.style.setProperty('--rows',rows);
 const grid=el('div','covariance-grid',wrap),hover=el('div','covariance-focus',wrap),rowbar=el('div','cov-row',hover),colbar=el('div','cov-col',hover),rowlabel=el('span','cov-row-label',hover),collabel=el('span','cov-col-label',hover),detail=el('div','cov-detail',wrap);hover.hidden=true;detail.hidden=true;
 function color(value){if(!finite(value))return '#F3EEE8';if(value>0){const a=value<.2?[243,238,232]:[213,155,168],b=value<.2?[213,155,168]:[164,86,104],t=value<.2?value/.2:Math.min(1,(value-.2)/.3);return 'rgb('+a.map((v,i)=>Math.round(v+(b[i]-v)*t)).join(',')+')';}const stops=['#607E95','#A8C3D6','#B8AEA6','#F3EEE8','#E2D0BC','#D59BA8','#A45668'],n=(value+1)*3,i=Math.min(5,Math.floor(n)),f=n-i,hex=h=>[1,3,5].map(k=>parseInt(h.slice(k,k+2),16)),a=hex(stops[i]),b=hex(stops[i+1]);return `rgb(${a.map((v,k)=>Math.round(v+(b[k]-v)*f)).join(',')})`}
 D.fields.forEach((field,y)=>ys.forEach((key,x)=>{const r=D.correlations.find(r=>r.x===field.key&&r.y===key),cell=el('button','cov-cell',grid);cell.style.background=color(r.rho);cell.setAttribute('aria-label',field.label+' / '+D.ys[key]+' '+fmt(r.rho));
  const activate=()=>{wrap.classList.add('has-focus');grid.querySelectorAll('button').forEach(b=>b.classList.toggle('chosen',b===cell));hover.hidden=false;detail.hidden=false;rowbar.style.top=(y/rows*100)+'%';rowbar.style.height=(100/rows)+'%';colbar.style.left=(x/cols*100)+'%';colbar.style.width=(100/cols)+'%';rowlabel.textContent=field.label;rowlabel.style.top=(y/rows*100)+'%';rowlabel.style.height=(100/rows)+'%';rowlabel.style.left=x>cols/2?'1%':'auto';rowlabel.style.right=x>cols/2?'auto':'1%';collabel.textContent=D.ys[key];collabel.style.left=((x+.5)/cols*100)+'%';collabel.style.top=y>rows/2?'2%':'auto';collabel.style.bottom=y>rows/2?'auto':'2%';detail.textContent=`ρ=${fmt(r.rho)}${stars(r.p)} · p=${finite(r.p)?r.p.toPrecision(3):'—'} · n=${r.n}`;};
  cell.addEventListener('pointerenter',activate);cell.addEventListener('focus',activate);
 }));const clear=()=>{wrap.classList.remove('has-focus');hover.hidden=true;detail.hidden=true;grid.querySelectorAll('button').forEach(b=>b.classList.remove('chosen'))};wrap.addEventListener('pointerleave',clear);wrap.addEventListener('focusout',e=>{if(!wrap.contains(e.relatedTarget))clear()});
 el('p','caption').textContent='负相关 −1　'+ '　—　接近0　—　'+'　正相关 +1';
}
function correlations(i){document.body.classList.remove('screen-analysis');if(i===0){covarianceMatrix();return;}if(i===1){note('每列代表一个节点，每行是一个指标；悬停显示同节点的全部信息并圈出综合评分。居民/游客指数用于对照展示，不纳入活动强度评分，以免把身份倾向当作活力高低。\n'+SFORM);vitalityInformation();return;}mixingInformation();}
function qualityChart(kind){const selected=D.qualityFields,desc=selected.map(k=>D.headers[k]).join('、');
 note('每个点为一个节点；横轴是从显著正相关空间指标构建的界面品质，纵轴为'+(kind==='qualityMix'?'混合度':'活力度')+'。\n指标筛选：'+(D.qualityRule||'ρ≥0.5 且 p<0.05')+'，相同空间指标只计一次。\nQ=(Σ z_j)/m，z_j=(x_j−min x_j)/(max x_j−min x_j)，m为筛出的空间指标数；任一输入缺失则Q缺失。\n本次入选：'+(desc||'无符合项，无法计算界面品质')+'。');
 if(!selected.length){el('p','empty').textContent='当前没有符合筛选标准的空间指标，界面品质暂无可计算结果。';return;}
 const key=kind==='qualityMix'?'mixScore':'vitality',c=chart(W,570),o=base();delete o.legend;o.xAxis={...axis('界面品质 Q'),min:0,max:1};o.yAxis={...axis(kind==='qualityMix'?'混合度 M':'活力度 V'),min:0,max:1};const pts=D.points.filter(p=>finite(p.quality)&&finite(p[key]));o.series=[{type:'scatter',data:pts.map(p=>[p.quality,p[key],p.address]),symbolSize:9,itemStyle:{color:PALETTE[0],opacity:.65}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>Q='+fmt(p.data[0])+'<br>评分='+fmt(p.data[1]);const f=fittedRegression(o.series[0].data);
 const controls=el('label','band-controls'),slider=el('input','',controls),value=el('span','',controls);slider.type='range';slider.min='0';slider.max='4';slider.step='0.05';slider.value='1.96';slider.setAttribute('aria-label','回归条带宽度');
 function update(){const k=Number(slider.value);value.textContent='回归条带宽度：'+k.toFixed(2)+' × 标准误';c.setOption({series:[o.series[0],...regressionSeries(f,Math.max(.000001,k),true)]},{replaceMerge:'series'});}
 c.setOption(o);update();slider.oninput=update;slider.disabled=!f;
 el('p','caption').textContent=(f?'OLS：y='+fmt(f.slope)+'x + '+fmt(f.intercept)+'；R²='+fmt(f.r2)+'；n='+f.n:'有效点不足或横轴恒定，无法拟合回归。')+'\n条带=拟合均值 ± k×SE，SE=s√[1/n+(x−x̄)²/Σ(xᵢ−x̄)²]，s=√[Σ(yᵢ−ŷᵢ)²/(n−2)]。滑条只调整k；这是可调标准误条带，不是固定置信水平。';
}
function mismatch(i){document.body.classList.add('screen-analysis');if(!i){note('越右越活跃，越上越多样；0.5划分高低，悬停查看节点。\n'+SFORM+'\n'+MFORM+'\nU=ln[(1+V)/(1+M)]；V=M时为0，V>M为正，V<M为负。');const c=chart(W,500),o=base();delete o.legend;o.grid={left:60,right:25,top:28,bottom:55,containLabel:true};o.xAxis={...axis('活力度 V'),min:0,max:1};o.yAxis={...axis('混合度 M'),min:0,max:1};const pts=D.points.filter(p=>finite(p.vitality)&&finite(p.mixScore));o.series=[{type:'scatter',id:'nodes',data:pts.map(p=>[p.vitality,p.mixScore,p.address,p.id]),symbolSize:8,itemStyle:{color:PALETTE[0],opacity:.6},markArea:{silent:true,itemStyle:{color:'rgba(164,86,104,0.14)'},label:{show:false},data:[[{xAxis:0.5,yAxis:0},{xAxis:1,yAxis:0.5}]]},markLine:{symbol:'none',silent:true,lineStyle:{color:'#B8AEA6',type:'dashed'},label:{show:false},data:[{xAxis:.5},{yAxis:.5}]}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>V='+fmt(p.data[0])+' / M='+fmt(p.data[1]);c.setOption(o);linkedNodeCharts();return;}
 note('仅显示高活力低混合节点。每个点对应一个节点，悬停查看名称和指标数值。\nU=ln[(1+V)/(1+M)]，横轴越大说明活力度相对混合度越高。\n附属设施加权指数及其余纵轴指标直接采用当前总表。\nOLS线性回归：R²≥0.5为深粉色实线，其余为浅粉色虚线；横轴恒定或有效点少于3不拟合。');
 const groups=[['有效空间',['K','L','M','S']],['功能',['O','P']],['界面基本品质',['T','U','V','W']],['界面舒适度',['Y','Z','AE','AF']],['配套设施品质',['AA','facility']]],nav=el('div','subtabs'),host=el('div','mismatch-panels');tabs(nav,groups.map(v=>v[0]),j=>{charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();const grid=el('div','fixed-grid',host);groups[j][1].forEach(key=>{const c=chart(grid,300),o=base();delete o.legend;o.title={text:D.headers[key],left:'center',top:3,textStyle:{fontFamily:FONT,fontSize:14}};o.grid={left:60,right:20,top:45,bottom:50,containLabel:true};o.xAxis=axis('不配得性 U');o.xAxis.nameGap=25;o.yAxis=axis();const pts=D.points.filter(p=>p.quadrant==='高活力低混合'&&finite(p.values[key]));o.series=[{id:'nodes',type:'scatter',symbolSize:7,data:pts.map(p=>[p.mismatch,p.values[key],p.address,p.id]),itemStyle:{color:'#607E95',opacity:.65}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>U='+fmt(p.data[0])+'<br>'+esc(D.headers[key])+'：'+fmt(p.data[1]);const f=fittedRegression(o.series[0].data);o.series.push(...regressionSeries(f));o.graphic=[{type:'text',right:22,bottom:5,style:{text:f?'R²='+fmt(f.r2)+' · n='+f.n:'无法拟合（缺失或恒定）',font:'11px '+FONT,fill:'#4B4B4B'}}];c.setOption(o);});linkedNodeCharts();requestAnimationFrame(()=>charts.forEach(c=>c.resize()));});}




