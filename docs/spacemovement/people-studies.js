/* 0905 pedestrian studies. Aggregate payload and explicit statistical denominators. */
const P=window.PEOPLE, page=Number(document.body.dataset.study);
const titles={9:'街道人群构成',10:'四维混合度对比',11:'行为集中度：洛伦兹曲线',12:'点位年龄构成',13:'点位混合度与置信区间',14:'人群、行为与空间关联'};
const workspace=document.querySelector('#workspace'),tabs=document.querySelector('nav'),note=document.querySelector('.note');
const WHITE='#f5f5f2',shades=['#f1f1ee','#c4c4c1','#969693','#696967','#444442'];
let charts=[];
document.querySelector('h1').textContent=String(page).padStart(2,'0')+' '+titles[page];
document.querySelector('.meta').textContent='0905 / '+P.recordCount+' OBSERVATIONS';
document.title=titles[page]+'｜巨富长街区';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=v=>v==null?'—':Number(v).toFixed(3);
const pct=v=>v==null?'—':(v*100).toFixed(1)+'%';
const smallp=v=>v==null?'—':v.toPrecision(3);
const share=(arr)=>{const n=arr.reduce((a,b)=>a+b,0);return arr.map(v=>n?v/n:0);};
const nodeLabel=p=>`${p.name} · #${p.node} · n=${p.n}`;
function chart(height){const el=document.createElement('div');el.className='plot';if(height)el.style.height=height+'px';workspace.append(el);const c=echarts.init(el);charts.push(c);return c;}
function reset(){charts.forEach(c=>c.dispose());charts=[];workspace.replaceChildren();}
function axis(name=''){return {type:'value',name,nameLocation:'middle',nameGap:35,axisLine:{show:true,lineStyle:{color:'#666'}},axisLabel:{color:'#bbb'},nameTextStyle:{color:'#ccc'},splitLine:{lineStyle:{color:'#272727'}}};}
function base(){return {animation:false,backgroundColor:'#090909',textStyle:{color:WHITE,fontFamily:'Arial, Microsoft YaHei'},tooltip:{confine:true,backgroundColor:'#181818',borderColor:'#666',textStyle:{color:WHITE}},grid:{left:155,right:45,top:80,bottom:80},xAxis:axis(),yAxis:axis(),legend:{top:12,textStyle:{color:'#ccc'}}};}
function select(labels,render){labels.forEach((label,i)=>{const b=document.createElement('button');b.textContent=label;b.setAttribute('role','tab');b.onclick=()=>{tabs.querySelectorAll('button').forEach(x=>x.setAttribute('aria-selected',String(x===b)));reset();render(i);};tabs.append(b);if(i===0)b.click();});}
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
  const groups=i===0?[P.all,...P.admins]:[P.all,P.admins[i-1]];
  o.radar={center:['50%','53%'],radius:'65%',splitNumber:4,indicator:['年龄','性别','活动','身份倾向'].map(name=>({name,max:1})),
    axisName:{color:WHITE,fontSize:14},axisLine:{lineStyle:{color:'#555'}},splitLine:{lineStyle:{color:'#444'}},splitArea:{show:false}};
  o.series=groups.map((g,k)=>({name:g.name,type:'radar',symbol:['circle','rect','triangle','diamond','roundRect'][k],symbolSize:7,
    lineStyle:{color:shades[k],width:g.name==='全域'?2:1.5,type:g.name==='全域'?'dashed':'solid'},
    itemStyle:{color:shades[k],opacity:1},areaStyle:{color:WHITE,opacity:.015},data:[{name:g.name,value:g.mix}]}));
  o.tooltip.formatter=p=>{const g=groups.find(g=>g.name===p.name);return `${esc(g.name)} · n=${g.n}<br>`+['年龄','性别','活动','身份倾向'].map((v,j)=>`${v}混合度：${num(g.mix[j])}`).join('<br>');};
  c.setOption(o);note.textContent='混合度 = −Σp·ln(p) / ln(K)，K 固定为年龄4类、性别2类、行为14类、身份倾向2类。行为以出现次数归一化；3条无法判断性别记录不参与性别维度。'+P.identityMethod;
}
function lorenz(i){
  const groups=[P.all,...P.admins],g=groups[i],c=chart(),o=base();
  o.xAxis={...axis('行为类型累计占比（按频数从低到高）'),min:0,max:1,axisLabel:{color:'#bbb',formatter:v=>Math.round(v*100)+'%'}};
  o.yAxis={...axis('行为出现次数累计占比'),min:0,max:1,axisLabel:{color:'#bbb',formatter:v=>Math.round(v*100)+'%'}};
  o.series=[{name:'完全均等线',type:'line',symbol:'none',data:[[0,0],[1,1]],lineStyle:{color:WHITE,opacity:.2,type:'dashed'}},
    {name:g.name,type:'line',data:g.lorenz.map((v,j)=>[j/P.behaviorLabels.length,v]),symbolSize:6,lineStyle:{color:WHITE,width:2},itemStyle:{color:WHITE},areaStyle:{color:WHITE,opacity:.04}}];
  o.graphic=[{type:'text',right:65,bottom:100,style:{text:`${g.name} · n=${g.n}\n基尼系数 G = ${num(g.gini)}\n前4类行为占比 = ${pct(g.top4)}\n行为出现次数 = ${g.actionTotal}`,fill:'#ccc',font:'14px sans-serif',lineHeight:25,textAlign:'right'}}];
  o.tooltip.formatter=p=>`${esc(p.seriesName)}<br>行为类型累计：${pct(p.data[0])}<br>行为次数累计：${pct(p.data[1])}`;
  c.setOption(o);note.textContent='固定纳入14种行为（含零频类别），按频数升序绘制。行为为多选，同一人可贡献多次行为；基尼衡量行为频数集中程度，不表示人口收入差异。';
}
function ageHeat(){
  const nodes=P.points.slice().sort((a,b)=>share(b.ages)[3]-share(a.ages)[3]||b.n-a.n||a.node-b.node);
  const c=chart(nodes.length*27+110),o=base();o.grid={left:260,right:80,top:55,bottom:25};
  o.xAxis={...axis(),type:'category',data:P.ageLabels,position:'top',axisLabel:{color:'#ddd',fontSize:14},splitLine:{show:false}};
  o.yAxis={...axis(),type:'category',data:nodes.map(nodeLabel),inverse:true,axisLabel:{color:'#aaa',fontSize:11,interval:0},splitLine:{show:false}};
  o.visualMap={dimension:2,min:0,max:1,calculable:false,right:2,top:10,itemHeight:140,inRange:{color:['#383838','#f5f5f2']},textStyle:{color:'#bbb'},formatter:v=>Math.round(v*100)+'%'};
  o.series=[{type:'heatmap',data:nodes.flatMap((p,j)=>share(p.ages).map((v,k)=>[k,j,v,p])),itemStyle:{borderColor:'#090909',borderWidth:2},
    label:{show:true,fontSize:11,formatter:p=>`{${p.data[2]<.4?'light':'dark'}|${Math.round(p.data[2]*100)}%}`,rich:{light:{color:'#ddd'},dark:{color:'#111'}}}}];
  o.tooltip.formatter=p=>`${esc(p.data[3].address)}<br>点位 #${p.data[3].node} · n=${p.data[3].n}<br>${P.ageLabels[p.data[0]]}：${p.data[3].ages[p.data[0]]} 人 · ${pct(p.data[2])}`;
  c.setOption(o);note.textContent='以点位ID区分111个点位，按老年占比降序排列；每行归一化为100%，仅呈现构成，不计算小样本混合度。上下滚动查看；同地址的不同点位用编号区分。';
}
function confidence(){
  const eligible=P.points.filter(p=>p.n>=10).sort((a,b)=>b.mix[0]-a.mix[0]||b.n-a.n),low=P.points.filter(p=>p.n<10);
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
      itemStyle:{color:WHITE,opacity:.5},label:{show:true,color:'#fff',position:'right',formatter:p=>p.data[0]}}];
  o.tooltip.formatter=p=>{const g=eligible[p.dataIndex];return `${esc(g.address)}<br>n=${g.n}<br>年龄混合度：${num(g.mix[0])}<br>bootstrap 95% CI：[${num(g.ci[0])}, ${num(g.ci[1])}]`;};
  c.setOption(o);
  const list=document.createElement('section');list.className='report low-sample';
  list.innerHTML=`<details><summary>${low.length} 个 n&lt;10 点位（灰色显示，不参与排名）</summary><table><thead><tr><th>点位</th><th>n</th><th>说明</th></tr></thead><tbody>`+
    low.map(p=>`<tr><td>${esc(p.address)} · #${p.node}</td><td>${p.n}</td><td>小样本，不估计混合度及置信区间</td></tr>`).join('')+'</tbody></table></details>';
  workspace.append(list);
  note.textContent=`仅对 n≥10 的 ${eligible.length} 个点位按年龄混合度排序；点位内行人重采样 ${P.bootstrap} 次，百分位法95%CI，固定随机种子。气泡面积正比于 n；单一年龄样本可能出现零宽区间，不代表总体不存在其他年龄。`;
}
function relations(i){
  const config=P.matrices[i],c=chart(),o=base();o.grid={left:190,right:25,top:65,bottom:125};
  o.xAxis={...axis(),type:'category',data:config.xs.map(k=>P.labels[k]),axisLabel:{color:'#ccc',fontSize:11,interval:0,rotate:35},splitLine:{show:false}};
  o.yAxis={...axis(),type:'category',data:config.ys.map(k=>P.labels[k]),inverse:true,axisLabel:{color:'#bbb',fontSize:11,interval:0},splitLine:{show:false}};
  o.visualMap={dimension:2,min:-1,max:1,orient:'horizontal',left:'center',top:5,inRange:{color:['#555','#aaa','#f5f5f2']},textStyle:{color:'#ccc'},text:['ρ = +1','ρ = −1']};
  const pairs=P.correlations.filter(r=>config.xs.includes(r.x)&&config.ys.includes(r.y)&&r.rho!==null);
  o.series=[{type:'heatmap',data:pairs.map(r=>({value:[config.xs.indexOf(r.x),config.ys.indexOf(r.y),r.rho,r],itemStyle:{borderColor:r.q<.05?'#fff':'#090909',borderWidth:r.q<.05?3:1}})),
    label:{show:true,color:'#111',fontSize:10,formatter:p=>p.value[2].toFixed(2)+(p.value[3].q<.05?'*':'')}}];
  o.tooltip.formatter=p=>{const r=p.value[3];return `${esc(P.labels[r.x])} / ${esc(P.labels[r.y])}<br>ρ=${num(r.rho)} · n=${r.n} 个点位<br>置换 p=${smallp(r.p)} · FDR q=${smallp(r.q)}<br>${r.q<.05?'通过 FDR 0.05':'未通过 FDR 0.05'}`;};
  c.setOption(o);note.textContent=`以点位为分析单元，逐对排除缺失；${P.permutations}次双侧置换检验，三个矩阵共${P.testCount}项有效检验统一做BH-FDR校正。*与白框表示q<0.05，空白表示常量或无法计算。小样本点位的占比波动较大；行为人数占比可重叠。空间指标按点位ID关联全量总表(0906)。`;
}
if(page===9)select(['年龄 · 老年占比排序','年龄 · 青年占比排序','身份倾向 · 居民占比排序'],stacked);
if(page===10)select(['全域与所有街道',...P.admins.map(g=>g.name)],radar);
if(page===11)select(['全域',...P.admins.map(g=>g.name)],lorenz);
if(page===12)ageHeat();
if(page===13)confidence();
if(page===14)select(P.matrices.map(m=>m.title),relations);
new ResizeObserver(()=>charts.forEach(c=>c.resize())).observe(workspace);
