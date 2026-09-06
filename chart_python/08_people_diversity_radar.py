"""08 五维混合度对比
修改下方 HTML / JAVASCRIPT 后运行本文件，即同步更新对应网页。
数据仍读取项目中的最新数据文件；不要修改 SOURCE_SCRIPT。
"""
from _export import export_chart

ROUTE = 'people_diversity_radar.html'
SOURCE_SCRIPT = 'people-studies.js'

HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五维混合度对比｜衡复风貌区</title><link rel="stylesheet" href="studies.css"><script src="echarts.min.js"></script><script src="people-data.js"></script></head>
<body data-study="10" data-number="8" data-title="五维混合度对比"><header><a href="../visualizations.html" aria-label="返回图表目录">←</a><h1>08 五维混合度对比</h1><span class="meta"></span></header><nav role="tablist" aria-label="切换分析图表"></nav><p class="note"></p><main id="workspace" aria-label="数据图表"></main><script src="people-studies.js"></script></body></html>'''

# 绘图代码：可修改 subtitle、轴名称、series、grid、symbolSize 等设置。
JAVASCRIPT = r'''/* 0905 pedestrian studies. Aggregate payload and explicit statistical denominators. */
const P=window.PEOPLE, page=Number(document.body.dataset.study);
const titles={9:'不配得性Ⅱ：街道人群构成',10:'五维混合度对比',11:'行为集中度：洛伦兹曲线',12:'点位年龄构成',13:'不配得性Ⅰ：点位混合度与置信区间',14:'人群、行为与空间关联',15:'不配得性Ⅱ：经济门槛与阶层排他',16:'不配得性Ⅱ：在地记忆的悬置'};
const workspace=document.querySelector('#workspace'),tabs=document.querySelector('nav'),note=document.querySelector('.note');
const WHITE='#f5f5f2',shades=['#f1f1ee','#c4c4c1','#969693','#696967','#444442'];
let charts=[];
const displayTitle=document.body.dataset.title||titles[page];
document.querySelector('h1').textContent=String(document.body.dataset.number||page).padStart(2,'0')+' '+displayTitle;
document.querySelector('.meta').textContent='2026人因空间·'+(page===15?P.economy.reduce((n,g)=>n+g.n,0):P.recordCount)+'RECORDS';
document.title=displayTitle+'｜衡复风貌区';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=v=>v==null?'—':Number(v).toFixed(3);
const pct=v=>v==null?'—':(v*100).toFixed(1)+'%';
const smallp=v=>v==null?'—':v.toPrecision(3);
const share=(arr)=>{const n=arr.reduce((a,b)=>a+b,0);return arr.map(v=>n?v/n:0);};
const nodeLabel=p=>`${p.name} · #${p.node} · n=${p.n}`;
function chart(height){const el=document.createElement('div');el.className='plot';if(height)el.style.height=height+'px';workspace.append(el);const c=echarts.init(el);charts.push(c);return c;}
function reset(){charts.forEach(c=>c.dispose());charts=[];workspace.replaceChildren();workspace.style.display='';workspace.style.overflowY='';note.style.whiteSpace='';}
function axis(name=''){return {type:'value',name,nameLocation:'middle',nameGap:35,axisLine:{show:true,lineStyle:{color:'#666'}},axisLabel:{color:'#bbb'},nameTextStyle:{color:'#ccc'},splitLine:{lineStyle:{color:'#272727'}}};}
function base(){return {animation:false,backgroundColor:'#090909',textStyle:{color:WHITE,fontFamily:'Times New Roman, SimSun, Songti SC, serif'},tooltip:{confine:true,backgroundColor:'#181818',borderColor:'#666',textStyle:{color:WHITE}},grid:{left:155,right:45,top:80,bottom:80},xAxis:axis(),yAxis:axis(),legend:{top:12,textStyle:{color:'#ccc'}}};}
function select(labels,render,initial=0){labels.forEach((label,i)=>{const b=document.createElement('button');b.textContent=label;b.setAttribute('role','tab');b.onclick=()=>{tabs.querySelectorAll('button').forEach(x=>x.setAttribute('aria-selected',String(x===b)));reset();render(i);};tabs.append(b);if(i===initial)b.click();});}
function stacked(i){
  const key=i===2?'identities':'ages',labels=i===2?P.identityLabels:P.ageLabels,sortIndex=i===0?3:i===1?1:0;
  const order=[sortIndex,...labels.map((_,j)=>j).filter(j=>j!==sortIndex)];
  const sorted=P.admins.slice().sort((a,b)=>share(b[key])[sortIndex]-share(a[key])[sortIndex]);
  const groups=[P.all,...sorted],baseline=share(P.all[key])[sortIndex];
  const c=chart(),o=base();o.xAxis={...axis('人数构成占比'),min:0,max:100,axisLabel:{color:'#bbb',formatter:'{value}%'}};
  o.yAxis={...axis(),type:'category',data:groups.map(g=>`${g.name} · n=${g.n}`),inverse:true,splitLine:{show:false}};
  o.series=order.map((j,k)=>({name:labels[j],type:'bar',stack:'composition',barMaxWidth:65,
    data:groups.map(g=>100*share(g[key])[j]),itemStyle:{color:shades[k],opacity:1},
    label:{show:true,color:k<2?'#111':'#fff',formatter:p=>p.value>=5?p.value.toFixed(1)+'%':''},
    emphasis:{focus:'none',itemStyle:{borderColor:'#fff',borderWidth:2}},
    ...(k===0?{markLine:{silent:true,symbol:'none',lineStyle:{color:'#fff',opacity:.65,type:'dashed',width:1},
      label:{color:'#ddd',formatter:`全域${labels[sortIndex]} ${pct(baseline)}`,position:'insideEndTop'},data:[{xAxis:baseline*100}]}}:{})}));
  o.tooltip.trigger='axis';o.tooltip.formatter=ps=>{const g=groups[ps[0].dataIndex];return `${esc(g.name)} · n=${g.n}<br>`+order.map(j=>`${esc(labels[j])}：${g[key][j]} 人 · ${pct(share(g[key])[j])}`).join('<br>');};
  c.setOption(o);note.textContent=`行政街道按${labels[sortIndex]}占比降序排列；虚线为全域基准，各行合计 100%。`+(i===2?' '+P.identityMethod:' 年龄分为幼年、青年、中年、老年。');
}
function radar(i){
  const c=chart(),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;
  const groups=i===0?[P.all,...P.admins]:[P.admins[i-1],...P.adminRoads[P.admins[i-1].name]];
  const dimensions=['年龄','活动','身份倾向','姿态','社交状态'];
  o.legend={type:'scroll',top:8,left:20,right:20,textStyle:{color:'#ccc'},pageTextStyle:{color:'#ccc'}};
  o.radar={center:['50%','55%'],radius:'64%',splitNumber:4,indicator:dimensions.map(name=>({name,max:1})),
    axisName:{color:WHITE,fontSize:14},axisLine:{lineStyle:{color:'#555'}},splitLine:{lineStyle:{color:'#444'}},splitArea:{show:false}};
  o.series=groups.map((g,k)=>({name:g.name,type:'radar',symbol:['circle','rect','triangle','diamond','roundRect'][k%5],symbolSize:6,
    lineStyle:{color:WHITE,opacity:k===0?.9:.45,width:k===0?2:1.2,type:k===0?'dashed':'solid'},
    itemStyle:{color:WHITE,opacity:.65},areaStyle:{color:WHITE,opacity:.008},emphasis:{lineStyle:{color:'#fff',opacity:1,width:3},itemStyle:{opacity:1}},data:[{name:g.name,value:g.mix}]}));
  o.tooltip.formatter=p=>{const g=groups.find(g=>g.name===p.name);return `${esc(g.name)} · n=${g.n}<br>`+dimensions.map((v,j)=>`${v}混合度：${num(g.mix[j])}`).join('<br>');};
  c.setOption(o);note.textContent='年龄、活动、身份倾向、姿态、社交状态五维混合度，均为标准化Shannon指数（0–1）。行政街道选项显示该街道域内及其下属各道路；图例可切换曲线。'+P.identityMethod;
}
function lorenz(i){
  const groups=P.roads,g=groups[i],c=chart(),o=base();
  o.xAxis={...axis('行为类型累计占比（按频数从低到高）'),min:0,max:1,axisLabel:{color:'#bbb',formatter:v=>Math.round(v*100)+'%'}};
  o.yAxis={...axis('行为出现次数累计占比'),min:0,max:1,axisLabel:{color:'#bbb',formatter:v=>Math.round(v*100)+'%'}};
  o.series=[{name:'完全均等线',type:'line',symbol:'none',data:[[0,0],[1,1]],lineStyle:{color:WHITE,opacity:.2,type:'dashed'}},
    {name:g.name,type:'line',data:g.lorenz.map((v,j)=>[j/P.behaviorLabels.length,v]),symbolSize:6,lineStyle:{color:WHITE,width:2},itemStyle:{color:WHITE},areaStyle:{color:WHITE,opacity:.04}}];
  o.graphic=[{type:'text',right:65,bottom:100,style:{text:`${g.name} · n=${g.n}\n基尼系数 G = ${num(g.gini)}\n前4类行为占比 = ${pct(g.top4)}\n行为出现次数 = ${g.actionTotal}`,fill:'#ccc',font:'14px SimSun',lineHeight:25,textAlign:'right'}}];
  o.tooltip.formatter=p=>`${esc(p.seriesName)}<br>行为类型累计：${pct(p.data[0])}<br>行为次数累计：${pct(p.data[1])}`;
  c.setOption(o);note.textContent='固定纳入14种行为（含零频类别），按频数升序绘制。行为为多选，同一人可贡献多次行为；基尼衡量行为频数集中程度，不表示人口收入差异。';
}
function ageHeat(){
  workspace.style.display='block';workspace.style.overflowY='auto';
  const nodes=P.points.slice().sort((a,b)=>share(b.ages)[3]-share(a.ages)[3]||b.n-a.n||a.node-b.node);
  const c=chart(nodes.length*27+110),o=base();o.grid={left:260,right:80,top:55,bottom:25};
  o.xAxis={...axis(),type:'category',data:P.ageLabels,position:'top',axisLabel:{color:'#ddd',fontSize:14},splitLine:{show:false}};
  o.yAxis={...axis(),type:'category',data:nodes.map(nodeLabel),inverse:true,axisLabel:{color:'#aaa',fontSize:11,interval:0},splitLine:{show:false}};
  o.visualMap={dimension:2,min:0,max:1,calculable:false,right:2,top:10,itemHeight:140,inRange:{color:['#383838','#f5f5f2']},textStyle:{color:'#bbb'},formatter:v=>Math.round(v*100)+'%'};
  o.series=[{type:'heatmap',data:nodes.flatMap((p,j)=>share(p.ages).map((v,k)=>[k,j,v,p])),itemStyle:{borderColor:'#090909',borderWidth:2},
    label:{show:true,fontSize:11,formatter:p=>`{${p.data[2]<.4?'light':'dark'}|${Math.round(p.data[2]*100)}%}`,rich:{light:{color:'#ddd'},dark:{color:'#111'}}}}];
  o.tooltip.formatter=p=>`${esc(p.data[3].address)}<br>点位 #${p.data[3].node} · n=${p.data[3].n}<br>${P.ageLabels[p.data[0]]}：${p.data[3].ages[p.data[0]]} 人 · ${pct(p.data[2])}`;
  c.setOption(o);note.textContent='按老年占比降序排列，仅呈现构成，不计算小样本混合度。';
}
function confidence(){
  const eligible=P.points.filter(p=>p.n>=5).sort((a,b)=>b.mix[0]-a.mix[0]||b.n-a.n),low=P.points.filter(p=>p.n<5);
  const c=chart(eligible.length*32+145),o=base();o.grid=[{left:250,right:'24%',top:70,bottom:65},{left:'83%',right:35,top:70,bottom:65}];
  const names=eligible.map(nodeLabel);
  o.xAxis=[{...axis('年龄混合度（标准化 Shannon）'),min:0,max:1},{...axis('样本量 n'),gridIndex:1,min:0,max:Math.ceil(Math.max(...eligible.map(p=>p.n))/5)*5}];
  o.yAxis=[{...axis(),type:'category',data:names,inverse:true,axisLabel:{color:'#bbb',fontSize:11,interval:0},splitLine:{show:false}},
    {type:'category',gridIndex:1,data:names,inverse:true,show:false}];
  o.series=[{name:'年龄混合度',type:'bar',barMaxWidth:14,data:eligible.map(p=>p.mix[0]),itemStyle:{color:WHITE,opacity:.35}},
    {name:'bootstrap 95% CI',type:'custom',data:eligible.map((p,j)=>[p.ci[0],p.ci[1],j]),encode:{x:[0,1],y:2},renderItem:(params,api)=>{
      const a=api.coord([api.value(0),api.value(2)]),b=api.coord([api.value(1),api.value(2)]);
      return {type:'group',children:[{type:'line',shape:{x1:a[0],y1:a[1],x2:b[0],y2:b[1]},style:{stroke:WHITE,lineWidth:1}},
        ...[a,b].map(p=>({type:'line',shape:{x1:p[0],y1:p[1]-4,x2:p[0],y2:p[1]+4},style:{stroke:WHITE,lineWidth:1}}))]};}},
    {name:'样本量',type:'scatter',xAxisIndex:1,yAxisIndex:1,data:eligible.map((p,j)=>[p.n,j]),symbolSize:v=>Math.sqrt(v[0])*3,
      itemStyle:{color:'#858583',opacity:1},label:{show:true,color:'#fff',position:'right',formatter:p=>p.data[0]}}];
  o.tooltip.formatter=p=>{const g=eligible[p.dataIndex];return `${esc(g.address)}<br>n=${g.n}<br>年龄混合度：${num(g.mix[0])}<br>bootstrap 95% CI：[${num(g.ci[0])}, ${num(g.ci[1])}]`;};
  c.setOption(o);
  const list=document.createElement('section');list.className='report low-sample';
  list.innerHTML=`<details><summary>${low.length} 个 n&lt;5 点位（灰色显示，不参与排名）</summary><table><thead><tr><th>点位</th><th>n</th><th>说明</th></tr></thead><tbody>`+
    low.map(p=>`<tr><td>${esc(p.address)} · #${p.node}</td><td>${p.n}</td><td>小样本，不估计混合度及置信区间</td></tr>`).join('')+'</tbody></table></details>';
  workspace.append(list);
  note.style.whiteSpace='pre-line';
  note.textContent='仅对n≥5的点位按照年龄混合度排序；\n横轴数值：该点位采集到的行人年龄分布分散程度；\n横向误差线（bootstrap 95% CI）：可信范围（线越短，样本数据一致性越高）。';
}
function relations(i){
  const original=P.matrices[i],config={...original,ys:original.ys.filter(k=>!(original.title==='人群x行为'&&k==='act5'))},c=chart(),o=base();o.grid={left:190,right:25,top:65,bottom:125};
  const axisLabel=k=>P.labels[k].replaceAll('占比','').replaceAll('人数','').replaceAll('(', '（').replaceAll(')', '）');
  o.xAxis={...axis(),type:'category',data:config.xs.map(axisLabel),axisLabel:{color:'#ccc',fontSize:11,interval:0,rotate:35},splitLine:{show:false}};
  o.yAxis={...axis(),type:'category',data:config.ys.map(axisLabel),inverse:true,axisLabel:{color:'#bbb',fontSize:11,interval:0},splitLine:{show:false}};
  o.visualMap={dimension:2,min:-1,max:1,orient:'horizontal',left:'center',top:5,inRange:{color:['#555','#aaa','#f5f5f2']},textStyle:{color:'#ccc'},text:['ρ = +1','ρ = −1']};
  const pairs=P.correlations.filter(r=>config.xs.includes(r.x)&&config.ys.includes(r.y)&&r.rho!==null);
  o.series=[{type:'heatmap',data:pairs.map(r=>({value:[config.xs.indexOf(r.x),config.ys.indexOf(r.y),r.rho,r],itemStyle:{borderColor:'#090909',borderWidth:1}})),
    label:{show:true,color:'#111',fontSize:10,formatter:p=>p.value[2].toFixed(2)}}];
  o.tooltip.formatter=p=>{const r=p.value[3];return `${esc(P.labels[r.x])} / ${esc(P.labels[r.y])}<br>ρ=${num(r.rho)} · n=${r.n} 个点位<br>置换 p=${smallp(r.p)}`;};
  c.setOption(o);note.textContent='以点位为分析单元，逐对排除缺失；小样本点位的占比波动较大，行为人数占比可重叠。';
}
function economy(){
  const c=chart(),o=base(),groups=P.economy.filter(g=>g.function!=='功能未记录').slice().sort((a,b)=>a.function.length-b.function.length||a.function.localeCompare(b.function,'zh-CN'));
  o.grid={left:90,right:165,top:95,bottom:160};
  o.xAxis={...axis('功能类型'),type:'category',data:groups.map(g=>g.function),axisLabel:{color:'#bbb',fontSize:11,interval:0,rotate:40},nameGap:130,splitLine:{show:false}};
  o.yAxis=[{...axis('人均消费水平（元/人）'),nameLocation:'end',nameGap:24,position:'left'},
    {...axis('消费型停留空间占比（%）'),nameLocation:'end',nameGap:46,position:'right',min:0,max:100,splitLine:{show:false}},
    {...axis('可承载停留人数（人）'),nameLocation:'end',nameGap:24,position:'right',offset:85,splitLine:{show:false}}];
  o.series=[['人均消费水平','cost',.85],['消费型停留空间占比','consumerShare',.5],['可承载停留人数','capacity',.25]].map(([name,key,opacity],i)=>({
    name,type:'bar',yAxisIndex:i,barGap:'15%',data:groups.map(g=>g[key]),itemStyle:{color:WHITE,opacity},emphasis:{itemStyle:{opacity:1}}}));
  o.tooltip.trigger='axis';o.tooltip.formatter=ps=>{const g=groups[ps[0].dataIndex];return `${esc(g.function)} · ${g.n} 个点位<br>人均消费水平：${num(g.cost)} 元/人（有效 n=${g.costN}）<br>消费型停留空间占比：${num(g.consumerShare)}%（有效 n=${g.consumerShareN}）<br>可承载停留人数：${num(g.capacity)} 人（有效 n=${g.capacityN}）`;};
  c.setOption(o);note.textContent='按功能类型汇总三个指标有效值均值。';
}
function memory(i){
  const g=P.memory[i],c=chart(),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;delete o.legend;
  const left=[...new Set(g.links.map(v=>v.source))],right=[...new Set(g.links.map(v=>v.target))];
  const nodes=[...left.map(name=>({name:'假设：'+name,depth:0})),...right.map(name=>({name:'当前：'+name,depth:1}))];
  o.graphic=[{type:'text',left:30,top:18,style:{text:'原初功能假设（代际偏好推演）',fill:'#ddd',font:'16px SimSun'}},
    {type:'text',right:30,top:18,style:{text:'当前功能类型',fill:'#ddd',font:'16px SimSun'}}];
  o.series=[{type:'sankey',left:'18%',right:'22%',top:65,bottom:35,nodeWidth:15,nodeGap:20,nodeAlign:'justify',draggable:false,
    data:nodes,links:g.links.map(v=>({source:'假设：'+v.source,target:'当前：'+v.target,value:v.value})),
    itemStyle:{color:WHITE,borderWidth:0},lineStyle:{color:WHITE,opacity:.18,curveness:.5},
    label:{color:'#ddd',fontSize:12,formatter:p=>p.name.replace(/^(假设：|当前：)/,'')},
    levels:[{depth:0,label:{position:'left'}},{depth:1,label:{position:'right'}}],emphasis:{focus:'adjacency',lineStyle:{opacity:.6}}}];
  o.tooltip.formatter=p=>p.dataType==='edge'?`${esc(p.data.source)} → ${esc(p.data.target)}<br>${p.data.value} 条${g.cohort}观测记录<br>连线是功能假设映射，不是已证实的历史用途转换。`:`${esc(p.name)}<br>代际偏好推演，非历史实测`;
  c.setOption(o);note.style.whiteSpace='pre-line';note.textContent=(`${g.cohort}群体 · n=${g.n}。`+P.memoryMethod).replace(/[。；;]/g,'$&\n').trim();
}
if(page===9)select(['年龄 · 青年占比排序','点位年龄构成','身份倾向 · 居民占比排序'],i=>i===1?ageHeat():stacked(i===0?1:2),window.location?.hash==='#age'?1:0);
if(page===10)select(['全域与所有街道',...P.admins.map(g=>g.name)],radar);
if(page===11)select(P.roads.map(g=>g.name),lorenz);
if(page===12)ageHeat();
if(page===13)confidence();
if(page===14)select(P.matrices.map(m=>m.title),relations);
if(page===15)economy();
if(page===16)select(P.memory.map(m=>m.cohort+'群体代际偏好推演'),memory);
new ResizeObserver(()=>charts.forEach(c=>c.resize())).observe(workspace);
'''

if __name__ == '__main__':
    export_chart(ROUTE, HTML, JAVASCRIPT, SOURCE_SCRIPT)
