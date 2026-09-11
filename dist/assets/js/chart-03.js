/* Stable light-theme charts. All calculated values come from the shared point-ID dataset. */
'use strict';
const D=window.INCLUSIVE, PAGE=document.body.dataset.page;
const W=document.querySelector('.workspace'),NAV=document.querySelector('.tabs'),NOTE=document.querySelector('.readme');
const FONT='SimSun, Songti SC, serif', INK='#292929', PALETTE=['#cd96be', '#c90097', '#ff0051', '#9c23ad', '#9094c1', '#6f52d4', '#072e55', '#0071ee', '#4d74a0', '#72a9bc'];
let charts=[];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const finite=Number.isFinite, fmt=(v,n=3)=>finite(v)?v.toFixed(n):'—';
const sum=a=>a.reduce((s,v)=>s+(finite(v)?v:0),0),mean=a=>{a=a.filter(finite);return a.length?sum(a)/a.length:null;};
const stars=p=>!finite(p)?'':p<.001?'***':p<.01?'**':p<.05?'*':'';
const SFORM='各底层指标 z=(x−全域最小值)/(全域最大值−全域最小值)，常量记0；缺失则综合评分缺失。综合评分=Σ(w×z)，采用系数表征的指定权重，不额外缩放。';
const MFORM='H_d=−Σ(p_k×ln p_k)/ln K_d；p_k=类别频数/该维频数合计，0×ln0记0。零合计或缺失不评分。M=0.149H年龄+0.141H活动+0.250H身份倾向+0.228H姿态+0.233H社交状态。权重按给定公式顺序使用，不二次归一化。';
document.querySelector('.meta').textContent=`2026人因空间·${['composition','memory','diversity'].includes(PAGE)?D.recordCount:D.rows}RECORDS`;
function el(tag,cls,parent=W){const n=document.createElement(tag);if(cls)n.className=cls;parent.append(n);return n;}
function reset(){document.body.classList.remove('case-analysis');charts.forEach(c=>c.dispose());charts=[];W.replaceChildren();document.querySelector('.map-tooltip')?.remove();}
function tabs(parent,labels,render){parent.replaceChildren();labels.forEach((s,i)=>{const b=el('button','',parent);b.textContent=s;b.setAttribute('role','tab');b.onclick=()=>{parent.querySelectorAll('button').forEach(v=>v.setAttribute('aria-selected',String(v===b)));render(i);};if(!i)b.click();});}
function mainTabs(labels,render){tabs(NAV,labels,i=>{reset();render(i);});}
function note(text){NOTE.textContent=String(text).replace(/。\s*/g,'。\n').trim();NOTE.hidden=!NOTE.textContent;}
function chart(parent=W,height=520){const n=el('div','plot',parent);n.style.height=height+'px';const c=echarts.init(n,null,{renderer:'canvas'});
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
 charts.push(c);enableChartDownload(c,n);return c;}
function base(){return {animation:false,backgroundColor:'#fff',color:PALETTE,textStyle:{color:INK,fontFamily:FONT,fontSize:15},title:{textStyle:{color:INK,fontFamily:FONT,fontSize:17,fontWeight:400}},tooltip:{confine:true,backgroundColor:'#fff',borderColor:'#72a9bc',textStyle:{color:INK,fontFamily:FONT}},grid:{left:75,right:35,top:65,bottom:90,containLabel:true},legend:{top:38,left:20,right:20,type:'scroll',textStyle:{color:'#4B4B4B',fontFamily:FONT}},xAxis:axis(),yAxis:axis()};}
function axis(name=''){return {type:'value',name,nameLocation:'middle',nameGap:40,nameTextStyle:{color:'#4B4B4B',fontFamily:FONT},axisLabel:{color:'#4B4B4B',fontFamily:FONT},axisLine:{show:true,lineStyle:{color:'#72a9bc'}},splitLine:{lineStyle:{color:'#9094c1'}}};}
function regression(a){if(a.length<2)return null;const mx=mean(a.map(p=>p[0])),my=mean(a.map(p=>p[1]));let xx=0,xy=0,yy=0;a.forEach(([x,y])=>{xx+=(x-mx)**2;xy+=(x-mx)*(y-my);yy+=(y-my)**2;});if(!xx)return null;return {b:xy/xx,a:my-xy/xx*mx,r2:yy?xy*xy/xx/yy:null,n:a.length,min:Math.min(...a.map(p=>p[0])),max:Math.max(...a.map(p=>p[0]))};}
function highlight(road){charts.forEach(c=>(c.getOption().series||[]).forEach((s,i)=>c.dispatchAction({type:s.name===road?'highlight':'downplay',seriesIndex:i})));}
function scatter(parent,xkey,ykey,title){const c=chart(parent),o=base(),series=[],all=[];delete o.legend;o.title={text:title,left:'center',textStyle:{fontFamily:FONT,fontSize:16,color:INK}};o.xAxis=axis(D.headers[xkey]);o.yAxis=axis(D.headers[ykey]);
 [...new Set(D.points.map(p=>p.road))].forEach(road=>{const data=D.points.filter(p=>p.road===road&&finite(p.values[xkey])&&finite(p.values[ykey])).map(p=>[p.values[xkey],p.values[ykey],p.address]);all.push(...data);if(data.length)series.push({name:road,type:'scatter',data,symbolSize:8,itemStyle:{color:'#72a9bc',opacity:1},emphasis:{itemStyle:{color:'#292929'},scale:1.4}});});
 const f=regression(all);if(f){series.push({name:'回归线',type:'line',data:[[f.min,f.a+f.b*f.min],[f.max,f.a+f.b*f.max]],symbol:'none',silent:true,lineStyle:{color:'#292929',opacity:.18,type:f.r2>=.5?'solid':'dashed'}});o.graphic=[{type:'text',right:18,bottom:8,style:{text:`y=${fmt(f.b)}x+${fmt(f.a)}\nR²=${fmt(f.r2)} · n=${f.n}`,fill:'#4B4B4B',font:'12px '+FONT,lineHeight:17,textAlign:'right'}}];}
 o.series=series;o.tooltip.formatter=p=>p.seriesType==='scatter'?`${esc(p.data[2])}<br>${esc(D.headers[xkey])}：${fmt(p.data[0])}<br>${esc(D.headers[ykey])}：${fmt(p.data[1])}`:'';c.setOption(o);c.on('mouseover',p=>{if(p.seriesType==='scatter')highlight(p.seriesName)});c.on('globalout',()=>highlight(null));}

function mapView(mode){note(mode===0?'选择活动查看原点位人数；圈越大人数越多，悬停时同一道路同时变实。\n圆半径 r=3+22×√(该点人数/当前指标最大人数)；按底图宽高的百分比定位。\n活动人数读取总表对应人数列；缺失观测仅在此地图按0显示。':'灰色表示人数少，橙色表示人数多；色块叠加展示人群在底图上的集中区域。\n权重 w=该点行人样本数/全域最大行人样本数。\n热度 h(x,y)=Σ[w_i×exp(−距离²/(2×σ²))]，σ=底图宽度的0.9%，以原始点位坐标为中心，核半径截断为3σ；热度按全图最大值归一化，缺失人数仅在此地图按0处理。');
 const tools=el('div','map-tools');let selected='AU';const pick=el('select','',tools);['AU','AV','AX','AY','BA','BB'].forEach(k=>{const option=el('option','',pick);option.value=k;option.textContent=D.headers[k]});if(mode===1)pick.hidden=true;
 const stage=el('div','map-stage'),img=el('img','',stage);img.src='../assets/data/map.jpg';img.alt='衡复风貌区调研底图';
 const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox','0 0 1000 706.38');svg.setAttribute('role','img');svg.setAttribute('aria-label',mode?'行人样本数热力分布':'活动样本数地图');stage.append(svg);
 const tip=el('div','map-tooltip',document.body);tip.hidden=true;
 function hover(ev,p,key){tip.innerHTML=esc(p.address)+'<br>'+esc(D.headers[key])+'：'+fmt(p.values[key]??0,0);tip.hidden=false;tip.style.left=Math.min(ev.clientX+12,window.innerWidth-280)+'px';tip.style.top=Math.max(10,Math.min(ev.clientY+12,window.innerHeight-100))+'px';}
 function draw(){svg.replaceChildren();const key=mode?'AH':selected,max=Math.max(1,...D.points.map(p=>p.values[key]||0));
  if(mode){
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
  D.points.forEach(p=>{if(!p.position)return;const n=p.values[key]||0,g=document.createElementNS(NS,'g');g.classList.add('map-point');g.dataset.road=p.road;g.setAttribute('tabindex','0');g.setAttribute('aria-label',p.address+' '+n+'人');g.setAttribute('transform',`translate(${p.position.x_percent*10},${p.position.y_percent*7.0638})`);
   const radius=mode?4:3+22*Math.sqrt(n/max);(mode?[1]:[1,.76,.5]).forEach((scale,i)=>{const c=document.createElementNS(NS,'circle');c.setAttribute('r',radius*scale);c.setAttribute('fill',mode?'#292929':(['#064b3b','#9c23ad','#6f52d4','#0071ee','#40316b','#ff0051'][['AU','AV','AX','BA','AY','BB'].indexOf(selected)]||'#4d74a0'));c.setAttribute('fill-opacity',mode?'.04':n===0?'.04':String(.12+i*.08));c.setAttribute('stroke','#292929');c.setAttribute('stroke-opacity',mode?'0':'.13');g.append(c)});
   const activate=e=>{svg.querySelectorAll('.map-point').forEach(v=>v.classList.toggle('active',v.dataset.road===p.road));if(e.clientX!==undefined)hover(e,p,key);};g.addEventListener('pointerenter',activate);g.addEventListener('pointermove',e=>hover(e,p,key));g.addEventListener('focus',activate);const clear=()=>{svg.querySelectorAll('.active').forEach(v=>v.classList.remove('active'));tip.hidden=true};g.addEventListener('pointerleave',clear);g.addEventListener('blur',clear);svg.append(g);
  });
 }
 pick.onchange=()=>{selected=pick.value;draw()};draw();if(mode){const legend=el('div','heat-legend');legend.innerHTML='低人数 <span class="heat-gradient"></span> 高人数';}
}

function weights(){note('每行代表一条道路，六段长度表示各项评分均值；悬停查看评分及所占比例。\n道路某项均值=该道路有效评分之和/有效点位数。\n遮荫评分=遮荫率(%)/20。\n六项合计=开放度+互动性+视觉丰富度+历史感知度+遮荫评分+路面状态，满分30。\n某项构成比例=该项均值/六项均值合计×100%。');const c=chart(W,Math.max(650,D.weights.length*29+120)),o=base(),names=['界面开放度','临街互动性','视觉丰富度','历史感知度','遮荫率','路面状态'];o.grid={left:100,right:30,top:70,bottom:35};o.xAxis=axis();o.yAxis={type:'category',data:D.weights.map(g=>g.road),axisLabel:{fontFamily:FONT,interval:0},inverse:true};o.series=names.map((name,j)=>({name,type:'bar',stack:'total',data:D.weights.map(g=>g.values[j]),itemStyle:{color:['#292929','#4B4B4B','#72a9bc','#9094c1','#9c23ad','#72a9bc'][j],opacity:j===5?.55:1},label:{show:true,color:j<2?'#fff':'#292929',formatter:p=>fmt(p.value,1)}}));o.tooltip.trigger='axis';o.tooltip.formatter=ps=>esc(ps[0].name)+'<br>'+ps.map(p=>`${esc(p.seriesName)}：${fmt(p.value,2)} (${fmt(p.value/sum(ps.map(v=>v.value))*100,1)}%)`).join('<br>');c.setOption(o);}
function composition(i){const age=i!==2,key=age?'ages':'identities',labels=age?['幼年','青年','中年','老年']:['居民倾向','游客倾向'];let groups=i===1?D.points.filter(p=>p.n>=4).slice().sort((a,b)=>b.ages[3]/sum(b.ages)-a.ages[3]/sum(a.ages)):[D.all,...D.admins.slice().sort((a,b)=>b[key][age?1:0]/sum(b[key])-a[key][age?1:0]/sum(a[key]))];note('每行总长为该群体的有效构成，悬停查看人数；点位年龄构成按老年比例排序。\n类别比例=该类人数/该维有效人数×100%。\n居民指数>游客指数记居民倾向，反之记游客倾向；相等或缺失不计入身份构成。');const c=chart(W,Math.max(490,groups.length*28+120)),o=base();o.grid={left:i===1?240:140,right:35,top:70,bottom:40};o.xAxis={...axis('构成（%）'),max:100};o.yAxis={type:'category',data:groups.map(g=>g.name+' · n='+g.n),inverse:true,axisLabel:{interval:0,fontSize:14,fontFamily:FONT}};o.series=labels.map((name,j)=>({name,type:'bar',stack:'share',data:groups.map(g=>sum(g[key])?g[key][j]/sum(g[key])*100:null),itemStyle:{color:['#292929','#72a9bc','#9094c1','#9c23ad'][j],opacity:!age&&j===1?.35:1},label:{show:true,color:j===0?'#fff':'#292929',formatter:p=>p.value>=8?fmt(p.value,1)+'%':''}}));o.tooltip.trigger='axis';c.setOption(o);}
function memory(i){note('连线宽度表示该年龄群体的观测条数；左侧是活动推演的原初功能，右侧是点位当前功能。\n映射按饮食→餐饮/饮品、光顾→零售、工作→生产/办公、打卡→文化展示优先匹配，其余归为生活服务。\n每条记录只进入一个映射，连线人数=对应映射的记录条数。\n这是代际偏好假设，非历史用途实测，也不把年龄层直接换算为具体年份。');const g=D.memory[i],c=chart(W,Math.max(550,Math.min(850,window.innerHeight*.8))),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;delete o.legend;const left=[...new Set(g.links.map(v=>v.source))],right=[...new Set(g.links.map(v=>v.target))];
 const layout=()=>{const narrow=c.getWidth()<650;return {series:[{type:'sankey',left:narrow?8:'19%',right:narrow?8:'23%',top:35,bottom:25,nodeWidth:12,nodeGap:16,draggable:false,data:[...left.map(name=>({name:'假设：'+name,depth:0})),...right.map(name=>({name:'当前：'+name,depth:1}))],links:g.links.map(v=>({source:'假设：'+v.source,target:'当前：'+v.target,value:v.value})),itemStyle:{color:'#292929',borderWidth:0},lineStyle:{color:'#292929',opacity:.16},label:{color:'#292929',fontFamily:FONT,fontSize:narrow?10:12,width:narrow?120:180,overflow:'break',formatter:p=>p.name.replace(/^(假设：|当前：)/,'')},levels:[{depth:0,label:{position:narrow?'right':'left'}},{depth:1,label:{position:narrow?'left':'right'}}],emphasis:{focus:'adjacency',lineStyle:{opacity:.5}}}]};};o.tooltip.formatter=p=>p.dataType==='edge'?`${esc(p.data.source)} → ${esc(p.data.target)}<br>${p.data.value}条观测`:esc(p.name);c.setOption({...o,...layout()});c.reflow=()=>c.setOption(layout());}
function space(i){note('每个点代表一个节点，悬停同步突出同一道路；灰色短线为各道路回归，悬停同路点位时一起高亮；整体回归为深粉色实线（R²≥0.5）或浅粉色虚线（R²<0.5），道路回归也按同一标准区分实虚线；有效点少于3或横轴恒定不拟合。右下角显示回归方程、R²和有效点位数。\n斜率 b=Σ[(x−x̄)(y−ȳ)]/Σ(x−x̄)²。\n截距 a=ȳ−b×x̄，预测值 ŷ=a+bx。\nR²=1−Σ(y−ŷ)²/Σ(y−ȳ)²；分母为0时不定义，缺失值逐对排除。\n节点空间长度、有效面积、承载人数、消费空间占比及各舒适度指标直接采用总表记录。');if(i===0){const sub=el('div','subtabs'),host=el('div','single-space-chart');const options=[['M','空间有效性分析'],['S','空间承载力分析'],['R','消费空间占比分析']];tabs(sub,options.map(v=>v[1]),j=>{charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();scatter(host,'K',options[j][0],options[j][1]);});}else{const grid=el('div','chart-grid');[['AE','遮荫率'],['AF','声环境舒适度'],['AG','气味环境']].forEach(([y,t])=>scatter(grid,'AH',y,t));}}

function radar(parent,groups,title,height=530){const c=chart(parent,height),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;const dims=['年龄混合度','活动丰富度','身份倾向混合度','姿态丰富度','社交状态混合度'];o.title={text:title,left:'center',top:0,textStyle:{fontSize:16,fontFamily:FONT}};o.legend.top=30;o.radar={center:['50%','57%'],radius:'59%',indicator:dims.map(name=>({name,max:1})),axisName:{color:'#292929',fontFamily:FONT},splitArea:{show:false},axisLine:{lineStyle:{color:'#9094c1'}},splitLine:{lineStyle:{color:'#9094c1'}}};o.series=groups.filter(g=>g.mix.every(finite)).map((g,j)=>({name:g.name,type:'radar',symbol:['circle','rect','triangle','diamond'][j%4],symbolSize:5,lineStyle:{color:PALETTE[j%PALETTE.length],opacity:j?.7:1,type:j?'solid':'dashed',width:j?1:2},itemStyle:{color:PALETTE[j%PALETTE.length]},data:[{name:g.name,value:g.mix}],emphasis:{lineStyle:{width:3,opacity:1}}}));o.tooltip.formatter=p=>esc(p.name)+'<br>'+dims.map((v,j)=>v+'：'+fmt(p.value[j])).join('<br>');c.setOption(o);return c;}
function scorePlot(parent,points,key,title){const compact=key==='mixScore',valid=points.filter(p=>finite(p[key])),container=el('div',compact?'score-wrap score-fit':'score-wrap',parent),c=chart(container,480),o=base();delete o.legend;o.title={text:title,left:'center',textStyle:{fontFamily:FONT,fontSize:16}};o.grid={left:60,right:24,top:80,bottom:compact?45:120,containLabel:true};o.xAxis={...axis(),type:'category',data:valid.map(p=>p.name),axisTick:{show:!compact},axisLabel:{show:!compact,rotate:45,interval:0,fontSize:13,fontFamily:FONT}};o.yAxis={...axis('综合评分'),min:0,max:1};o.series=[{type:'scatter',symbolSize:7,data:valid.map(p=>p[key]),itemStyle:{color:'#4B4B4B',opacity:1},label:{show:true,position:'top',color:'#292929',fontFamily:FONT,fontSize:13,formatter:p=>fmt(p.value,2)}}];o.tooltip.formatter=p=>esc(valid[p.dataIndex].address)+'<br>评分：'+fmt(p.value)+'<br>行人样本 n='+valid[p.dataIndex].n;c.setOption(o);return c;}
function lorenz(parent,g){const c=chart(parent,480),o=base(),order=g.actions.map((v,j)=>({v,j})).sort((a,b)=>a.v-b.v||a.j-b.j);o.title={text:'行为集中度：洛伦兹曲线',left:'center',top:5,textStyle:{fontFamily:FONT,fontSize:16}};o.legend={...o.legend,top:40,left:10,right:10};o.grid={left:55,right:20,top:92,bottom:115,containLabel:true};o.xAxis={...axis(),type:'category',data:['起点',...order.map(p=>D.behaviorLabels[p.j])],axisLabel:{rotate:55,interval:0,fontSize:13,fontFamily:FONT}};o.yAxis={...axis('行为出现次数累计比例'),min:0,max:1};o.series=[{name:'均等线',type:'line',data:Array.from({length:15},(_,i)=>i/14),symbol:'none',lineStyle:{color:'#72a9bc',type:'dashed'}},{name:g.name,type:'line',data:g.lorenz||[],symbolSize:4,lineStyle:{color:'#292929'},itemStyle:{color:'#292929'}}];o.tooltip.trigger='axis';c.setOption(o);}
function diversity(i){note('五边形越外扩，群体在相应维度越多样；点击行政街道内的道路，向下查看该道路及点位、行为曲线和综合评分。小样本点位仍显示，但 n<5 的结果容易波动。\n'+MFORM+'\n洛伦兹纵坐标 L_j=前j类行为频数累计/14类行为频数合计，行为按频数从低到高排序。');const groups=i===0?[D.all,...D.admins]:[D.admins[i-1],...D.admins[i-1].roads];const c=radar(W,groups,i===0?'全域与所有街道':D.admins[i-1].name);if(!i)return;const admin=D.admins[i-1],buttons=el('div','road-buttons'),drill=el('section','drill');
 function open(road){while(charts.length>1){charts.pop().dispose()}drill.replaceChildren();el('h2','section-heading',drill).textContent=road+' · 道路与节点';const group=admin.roads.find(g=>g.name===road),pts=D.points.filter(p=>p.admin===admin.name&&p.road===road&&p.n);const grid=el('div','chart-grid',drill),a=el('div','',grid),b=el('div','',grid),d=el('div','',grid);radar(a,[group,...pts],road+'及各点位',480);lorenz(b,group);scorePlot(d,pts,'mixScore','点位混合度综合评分');el('p','caption',drill).textContent='点位标注为地址，悬停可查看样本量。\n'+MFORM;drill.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});}
 admin.roads.forEach(g=>{const b=el('button','',buttons);b.textContent=g.name;b.onclick=()=>open(g.name)});c.on('legendselectchanged',p=>{if(admin.roads.some(g=>g.name===p.name)){c.dispatchAction({type:'legendSelect',name:p.name});open(p.name)}});c.on('click',p=>{if(admin.roads.some(g=>g.name===p.name))open(p.name)});
}

function correlations(i){if(i===1){note('每个点显示一个节点的活力度评分，点上方标出分数；分数越高，当前观测下的活动强度越高。缺少评分输入的点位列在图后。\n'+SFORM);scorePlot(W,D.points,'vitality','活力度综合评分');missingScores('vitality');return;}
 note('圆越大，关联越强；实心表示正相关，空心表示负相关；数值下方显示星号显著性，—表示数据不足或指标不变化。\nρ=Σ[(R_x−R̄_x)(R_y−R̄_y)]/√[Σ(R_x−R̄_x)²×Σ(R_y−R̄_y)²]，并列值采用平均秩，逐对排除缺失。\nA、B1、B2、B3、C、D按具体类别展开：某类别出现=1，未出现=0；整项未记录保留缺失。\n'+SFORM+'\n年龄混合度 H=−Σ(p_k ln p_k)/ln4。\n居民/游客指数=该点位行人表相应指数的有效值均值。\n* p<0.05，** p<0.01，*** p<0.001；p为双侧Spearman近似检验，未做多重检验校正。');
 const ys=Object.keys(D.ys),wrap=el('div','table-scroll');let html='<table><thead><tr><th>空间指标 / 行人指标</th>'+ys.map(k=>'<th>'+esc(D.ys[k])+'</th>').join('')+'</tr></thead><tbody>';
 D.fields.forEach(f=>{html+='<tr><th>'+esc(f.label)+'</th>'+ys.map(y=>{const r=D.correlations.find(r=>r.x===f.key&&r.y===y);if(!finite(r.rho))return '<td title="有效配对 '+r.n+'">—</td>';const size=32+36*Math.sqrt(Math.abs(r.rho));return `<td class="circle-cell" title="n=${r.n}; p=${r.p}"><span class="circle ${r.rho<0?'negative':'positive'}" style="width:${size}px;height:${size}px;--alpha:${.5+.5*Math.abs(r.rho)}">${fmt(r.rho)}${stars(r.p)}</span></td>`}).join('')+'</tr>';});wrap.innerHTML=html+'</tbody></table>';
 const heading=el('h2','section-heading');heading.textContent='Spearman相关系数';const table=el('div','table-scroll');table.innerHTML='<table><thead><tr><th>空间指标 / 行人指标</th>'+ys.map(k=>'<th>'+esc(D.ys[k])+'</th>').join('')+'</tr></thead><tbody>'+D.fields.map(f=>'<tr><th>'+esc(f.label)+'</th>'+ys.map(y=>{const r=D.correlations.find(r=>r.x===f.key&&r.y===y);return '<td>'+fmt(r.rho)+stars(r.p)+'</td>'}).join('')+'</tr>').join('')+'</tbody></table>';
}
function missingScores(key){const pts=D.points.filter(p=>!finite(p[key]));if(pts.length){const p=el('p','notice');p.textContent=`${pts.length} 个点位缺少评分输入，未将缺失填为0：`+pts.map(p=>p.name).join('、');}}
function mismatch(i){if(!i){note('横轴活力度、纵轴混合度，越右越活跃、越上越多样；虚线以0.5划分高低，悬停查看节点。缺少任一评分的点位不绘制。\n'+SFORM+'\n'+MFORM+'\n高活力低混合：V≥0.5且M<0.5；双高：V≥0.5且M≥0.5。');const c=chart(W,600),o=base();o.xAxis={...axis('活力度 V'),min:0,max:1};o.yAxis={...axis('混合度 M'),min:0,max:1};const pts=D.points.filter(p=>finite(p.vitality)&&finite(p.mixScore));o.series=[{type:'scatter',symbolSize:9,data:pts.map(p=>[p.vitality,p.mixScore,p.address,p.n]),itemStyle:{color:'#4B4B4B',opacity:1},markLine:{silent:true,symbol:'none',lineStyle:{color:'#72a9bc',type:'dashed'},label:{show:false},data:[{xAxis:.5},{yAxis:.5}]},markArea:{silent:true,itemStyle:{color:'#00000003'},label:{color:'#4B4B4B',fontFamily:FONT},data:[[{name:'低活力高混合',xAxis:0,yAxis:.5},{xAxis:.5,yAxis:1}],[{name:'双高',xAxis:.5,yAxis:.5},{xAxis:1,yAxis:1}],[{name:'双低',xAxis:0,yAxis:0},{xAxis:.5,yAxis:.5}],[{name:'高活力低混合',xAxis:.5,yAxis:0},{xAxis:1,yAxis:.5}]]}}];o.tooltip.formatter=p=>`${esc(p.data[2])}<br>V=${fmt(p.data[0])}，M=${fmt(p.data[1])}<br>行人样本 n=${p.data[3]}`;c.setOption(o);missingScores('mismatch');return;}
 note('两个板块分别比较高活力低混合和双高点位。选择界面指标，横轴是不配得性，纵轴是所选评分；按不配得性顺序连接观测点，连线仅帮助阅读，不代表时间变化或因果。\n不配得性 U=ln[(1+V)/(1+M)]；V=M时为0，V>M为正，V<M为负。\nV、M均为0–1评分；加入1使零值可计算，双高或双低且相近时U接近0。\n遮荫评分=遮荫率(%)/20；其余界面指标使用总表评分。');const sub=el('div','subtabs'),host=el('div');const keys=['U','V','Y','Z','AE','AA'];tabs(sub,keys.map(k=>k==='AE'?'遮荫评分':D.headers[k]),idx=>{charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();const grid=el('div','chart-grid two',host);['高活力低混合','双高'].forEach(group=>{const panel=el('section','',grid);el('h2','section-heading',panel).textContent=group;const key=keys[idx],pts=D.points.filter(p=>p.quadrant===group&&finite(p.values[key])).sort((a,b)=>a.mismatch-b.mismatch);if(!pts.length){el('p','empty',panel).textContent='当前没有满足条件且该指标有效的点位。';return;}const c=chart(panel,490),o=base();o.xAxis=axis('不配得性 U');o.yAxis=axis(key==='AE'?'遮荫评分':D.headers[key]);o.series=[{type:'line',data:pts.map(p=>[p.mismatch,p.values[key]/(key==='AE'?20:1),p.address]),symbolSize:8,lineStyle:{color:'#4B4B4B',opacity:.4},itemStyle:{color:'#292929'},label:{show:true,position:'top',fontFamily:FONT,fontSize:13,formatter:p=>fmt(p.data[1],1)}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>U='+fmt(p.data[0])+'<br>评分='+fmt(p.data[1]);c.setOption(o);});});}

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
 const series=[{id:'regression',type:'line',silent:true,showSymbol:false,data:f.points.map(p=>p.slice(0,2)),lineStyle:{color:alwaysPink||f.r2>=.5?'#9c23ad':'#c90097',type:alwaysPink||f.r2>=.5?'solid':'dashed',width:2},z:3}];
 if(band>0)series.push({id:'regression-band',type:'custom',silent:true,data:[0],z:0,renderItem:(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+band*p[2]])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-band*p[2]]))]},style:{fill:'#c90097',opacity:.22}})});
 return series;
}
function linkedNodeCharts(){const active=charts.slice();active.forEach(c=>{c.setOption({series:[{id:'nodes',emphasis:{scale:1.6,itemStyle:{opacity:1},label:{show:true,position:'top',formatter:p=>p.data[2],fontFamily:FONT,color:'#292929',backgroundColor:'rgba(255,255,255,.9)',padding:3}}}]});
 c.on('mouseover',p=>{if(p.seriesId!=='nodes'&&p.seriesIndex!==0)return;const id=p.data[3];active.forEach(other=>{other.dispatchAction({type:'downplay'});const nodes=other.getOption().series.find(s=>s.id==='nodes');const index=nodes.data.findIndex(v=>v[3]===id);if(index>=0)other.dispatchAction({type:'highlight',seriesId:'nodes',dataIndex:index});});});
 c.on('globalout',()=>active.forEach(other=>other.dispatchAction({type:'downplay'})));});}
function vitalityInformation(){
 const nav=el('div','subtabs'),host=el('div'),c=informationScatter(host,'vitality'),original=c.getOption();host.querySelector('.caption').textContent='颜色区分指标；悬停显示原始数值及点位名称。校准展示以点大小编码该指标的相对大小，散点图以各自独立纵轴编码原始数值。';
 const keys=['sample','clusters','density','gather'],labels=[...keys.map(k=>quality?D.headers[k]:D.ys[k]),'综合评分'],values=keys.map(k=>D.points.map(p=>(quality?p.qualityNormalized:kind==='vitality'?p.vitalityNormalized:p.metrics)[k]));values.push(D.points.map(p=>p.vitality));let mode=0;
 c.off('mouseover');c.off('globalout');
 tabs(nav,['校准展示','散点图'],i=>{mode=i;const compact=window.innerWidth<700,step=compact?24:42;
 const axes=i?labels.map((name,j)=>({id:'metric-'+j,type:'value',min:'dataMin',max:'dataMax',position:j<4?'left':'right',offset:(j<4?j:j-4)*step,name:String(j+1),nameLocation:'end',nameTextStyle:{color:PALETTE[j%PALETTE.length],fontFamily:FONT},axisLine:{show:true,lineStyle:{color:PALETTE[j%PALETTE.length]}},axisLabel:{fontSize:compact?12:14,color:'#4B4B4B',formatter:v=>Number(v.toPrecision(3)).toString()},splitLine:{show:false}})):original.yAxis;
 const series=labels.map((name,j)=>({id:'info-'+j,type:'scatter',name,yAxisIndex:i?j:0,data:values[j].map((v,k)=>({id:String(D.points[k].id),value:[k,i?v:j,v]})),symbolSize:i?(v=>finite(v[2])?(j===6?10:7):0):original.series[j].symbolSize,itemStyle:{color:PALETTE[j%PALETTE.length],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}}}));
 series.push({id:'focus-ring',type:'scatter',yAxisIndex:i?6:0,data:[]});
 c.setOption({animation:true,animationDurationUpdate:850,animationEasingUpdate:'cubicInOut',grid:{left:i?step*3+40:150,right:i?step*2+40:25,top:40,bottom:50},yAxis:axes,series}, {replaceMerge:'yAxis'});
 note((i?'七组散点叠加，各指标使用独立纵轴，轴号1–7依次对应：'+labels.join('、')+'。每组纵轴均从小到大，不能直接比较不同指标的绝对高度。':'每列代表一个节点，每行代表一个指标，圆点大小显示该行相对大小。')+'\n悬停联动同点位，综合评分加外圈；切换视图时点位平滑移动。\n'+SFORM);
 });
 c.on('mouseover',p=>{if(p.seriesIndex>=7)return;const i=p.data.value?p.data.value[0]:p.data[0];c.dispatchAction({type:'downplay'});labels.forEach((_,j)=>c.dispatchAction({type:'highlight',seriesIndex:j,dataIndex:i}));c.setOption({series:[{id:'focus-ring',data:finite(values[6][i])?[[i,mode?values[6][i]:6]]:[]}]});});
 c.on('globalout',()=>{c.dispatchAction({type:'downplay'});c.setOption({series:[{id:'focus-ring',data:[]}]});});
 c.setOption({tooltip:{formatter:p=>{const i=(p.data.value||p.data)[0];return esc(D.points[i].address)+'<br>'+labels.map((name,j)=>esc(name)+'：'+fmt(values[j][i])).join('<br>')}}});
}
function informationScatter(parent,kind){
 const points=rankedInformationPoints(kind);
 const quality=kind==='quality',mix=kind==='mix',keys=quality?D.qualityFields:mix?['ageMix','activityMix','identityMix','postureMix','socialMix']:['sample','clusters','density','gather'],labels=[...keys.map(k=>quality?D.headers[k]:D.ys[k]),'综合评分'];
 const c=chart(parent,Math.max(440,Math.min(650,window.innerHeight*.68))),o=base();delete o.legend;
 o.grid={left:150,right:25,top:25,bottom:50};o.xAxis={type:'category',data:points.map(p=>p.name),axisLabel:{show:false},axisTick:{show:false},name:{quality:'所有点位（按界面品质从低到高）',mix:'所有点位（按综合混合度从低到高）',vitality:'所有点位（按空间活力度从低到高）'}[kind],nameLocation:'middle',nameGap:28};
 o.yAxis={type:'category',data:labels,inverse:true,axisLabel:{color:'#4B4B4B',fontFamily:FONT,fontSize:14,interval:0},axisTick:{show:false},splitLine:{show:true,lineStyle:{color:'#cd96be'}}};
 const values=keys.map(k=>points.map(p=>(quality?p.qualityNormalized:kind==='vitality'?p.vitalityNormalized:p.metrics)[k]));values.push(points.map(p=>p[quality?'quality':mix?'mixScore':'vitality']));
 const ranges=values.map(a=>{const v=a.filter(finite);return [Math.min(...v),Math.max(...v)]});
 o.series=labels.map((name,j)=>({id:'info-'+j,name,type:'scatter',data:values[j].map((v,i)=>[i,j,v]),symbolSize:v=>{if(!finite(v[2]))return 0;const [lo,hi]=ranges[j];return 5+9*Math.sqrt(hi>lo?(v[2]-lo)/(hi-lo):.5)},itemStyle:{color:PALETTE[j%PALETTE.length],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}},blur:{itemStyle:{opacity:.5}}}));
 o.series.push({id:'focus-ring',type:'scatter',silent:true,data:[],symbolSize:27,itemStyle:{color:'transparent',borderColor:PALETTE[6],borderWidth:2,opacity:1},z:10});
 o.tooltip.formatter=p=>{const i=p.data[0],node=points[i];return esc(node.address)+'<br>'+labels.map((name,j)=>esc(name)+'：'+fmt(values[j][i])).join('<br>')};c.setOption(o);
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
 note('颜色由深蓝到洋红表示负相关到正相关，近零为白色。悬停格子时显示指标名称、系数、显著性和有效样本数。\nρ=两变量平均秩的Pearson相关系数；逐对排除缺失，并列值取平均秩。\nB1编码：无退让a=0、局部c=1、区域b=2、整体d=3；B2可视度a/b/c/d=0/1/2/3。\nB3a、b、c分别为对应构件子类出现数量；C尺度层级按C1至C4编码1至4。\n附属设施加权指数采用当前源表已计算的加权指数；未记录保留缺失。\n* p<0.05，** p<0.01，*** p<0.001，双侧近似检验，未做多重校正。');
 const wrap=el('div','covariance'),ys=Object.keys(D.ys),rows=D.fields.length,cols=ys.length;wrap.style.setProperty('--cols',cols);wrap.style.setProperty('--rows',rows);
 const grid=el('div','covariance-grid',wrap),hover=el('div','covariance-focus',wrap),rowbar=el('div','cov-row',hover),colbar=el('div','cov-col',hover),rowlabel=el('span','cov-row-label',hover),collabel=el('span','cov-col-label',hover),detail=el('div','cov-detail',wrap);hover.hidden=true;detail.hidden=true;
 function color(value){return chartScale(value)}
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
function mismatch(i){document.body.classList.add('screen-analysis');if(!i){note('越右越活跃，越上越多样；0.5划分高低，悬停查看节点。\n'+SFORM+'\n'+MFORM+'\nU=ln[(1+V)/(1+M)]；V=M时为0，V>M为正，V<M为负。');const c=chart(W,500),o=base();delete o.legend;o.grid={left:60,right:25,top:28,bottom:55,containLabel:true};o.xAxis={...axis('活力度 V'),min:0,max:1};o.yAxis={...axis('混合度 M'),min:0,max:1};const pts=D.points.filter(p=>finite(p.vitality)&&finite(p.mixScore));o.series=[{type:'scatter',id:'nodes',data:pts.map(p=>[p.vitality,p.mixScore,p.address,p.id]),symbolSize:8,itemStyle:{color:PALETTE[0],opacity:.6},markArea:{silent:true,itemStyle:{color:'rgba(156,35,173,0.14)'},label:{show:false},data:[[{xAxis:0.5,yAxis:0},{xAxis:1,yAxis:0.5}]]},markLine:{symbol:'none',silent:true,lineStyle:{color:'#9094c1',type:'dashed'},label:{show:false},data:[{xAxis:.5},{yAxis:.5}]}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>V='+fmt(p.data[0])+' / M='+fmt(p.data[1]);c.setOption(o);linkedNodeCharts();return;}
 note('仅显示高活力低混合节点。每个点对应一个节点，悬停查看名称和指标数值。\nU=ln[(1+V)/(1+M)]，横轴越大说明活力度相对混合度越高。\n附属设施加权指数及其余纵轴指标直接采用当前总表。\nOLS线性回归：R²≥0.5为深粉色实线，其余为浅粉色虚线；横轴恒定或有效点少于3不拟合。');
 const groups=[['有效空间',['K','L','M','S']],['功能',['O','P']],['界面基本品质',['T','U','V','W']],['界面舒适度',['Y','Z','AE','AF']],['配套设施品质',['AA','facility']]],nav=el('div','subtabs'),host=el('div','mismatch-panels');tabs(nav,groups.map(v=>v[0]),j=>{charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();const grid=el('div','fixed-grid',host);groups[j][1].forEach(key=>{const c=chart(grid,300),o=base();delete o.legend;o.title={text:D.headers[key],left:'center',top:3,textStyle:{fontFamily:FONT,fontSize:14}};o.grid={left:60,right:20,top:45,bottom:50,containLabel:true};o.xAxis=axis('不配得性 U');o.xAxis.nameGap=25;o.yAxis=axis();const pts=D.points.filter(p=>p.quadrant==='高活力低混合'&&finite(p.values[key]));o.series=[{id:'nodes',type:'scatter',symbolSize:7,data:pts.map(p=>[p.mismatch,p.values[key],p.address,p.id]),itemStyle:{color:'#4d74a0',opacity:.65}}];o.tooltip.formatter=p=>esc(p.data[2])+'<br>U='+fmt(p.data[0])+'<br>'+esc(D.headers[key])+'：'+fmt(p.data[1]);const f=fittedRegression(o.series[0].data);o.series.push(...regressionSeries(f));o.graphic=[{type:'text',right:22,bottom:5,style:{text:f?'R²='+fmt(f.r2)+' · n='+f.n:'无法拟合（缺失或恒定）',font:'11px '+FONT,fill:'#4B4B4B'}}];c.setOption(o);});linkedNodeCharts();requestAnimationFrame(()=>charts.forEach(c=>c.resize()));});}





function vitalityInformation(){informationExplorer(W,'vitality');}
function informationExplorer(parent,kind){
 const points=rankedInformationPoints(kind);
 const quality=kind==='quality',mix=kind==='mix',keys=quality?D.qualityFields:mix?['ageMix','activityMix','identityMix','postureMix','socialMix']:['sample','clusters','density','gather'];
 const labels=[...keys.map(k=>quality?D.headers[k]:D.ys[k]),'综合评分'],count=labels.length,last=count-1;
 const nav=el('div','subtabs',parent),host=el('div','',parent),c=informationScatter(host,kind),original=c.getOption();
 original.xAxis.forEach(axis=>axis.name={quality:'所有点位（按界面品质从低到高）',mix:'所有点位（按综合混合度从低到高）',vitality:'所有点位（按空间活力度从低到高）'}[kind]);
 const controls=el('div','metric-controls axis-controls',host),caption=host.querySelector('.caption');
 const values=keys.map(k=>points.map(p=>(quality?p.qualityNormalized:kind==='vitality'?p.vitalityNormalized:p.metrics)[k]));values.push(points.map(p=>p[quality?'quality':mix?'mixScore':'vitality']));
 const fits=values.map(v=>fittedRegression(v.map((y,x)=>[x,y]))),state=labels.map(()=>({visible:true,line:false,band:false}));let mode=0,selected=-1,phase=0,timer=null,generation=0;
 function cancelReveal(){generation++;if(timer!==null)clearTimeout(timer);timer=null;}
 function reveal(j){const f=fits[j];if(!f)return;const token=generation;let frame=0;
  function tick(){if(token!==generation||c.isDisposed())return;frame++;const lineProgress=Math.min(1,frame/30),bandProgress=Math.max(0,Math.min(1,(frame-30)/20));
   const end=(f.points.length-1)*lineProgress,k=Math.floor(end),points=f.points.slice(0,k+1).map(p=>p.slice(0,2));if(k<f.points.length-1){const a=f.points[k],b=f.points[k+1],t=end-k;points.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}
   c.setOption({series:[{id:'info-line-'+j,animation:false,data:points},{id:'info-band-'+j,animation:false,data:bandProgress>0?[0]:[],renderItem:(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+1.96*p[2]*bandProgress])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-1.96*p[2]*bandProgress]))]},style:{fill:PALETTE[j%PALETTE.length],opacity:.14}})}]});
   if(frame<50)timer=setTimeout(tick,30);else timer=null;
  }timer=setTimeout(tick,30);
 }
 c.off('mouseover');c.off('globalout');
 labels.forEach((label,j)=>{const card=el('div','metric-control',controls);card.style.borderTopColor=PALETTE[j%PALETTE.length];
  const main=el('button','metric-toggle',card);main.textContent='';main.title=label;main.setAttribute('aria-label',label);main.dataset.phase='0';main.setAttribute('aria-pressed','false');main.onclick=()=>{cancelReveal();phase=selected===j?(phase+1)%3:1;selected=phase?j:-1;state.forEach((s,k)=>{s.visible=selected<0||k===selected;s.line=false;s.band=false;});controls.querySelectorAll('button').forEach((b,k)=>{b.setAttribute('aria-pressed',String(k===selected));b.dataset.phase=String(k===selected?phase:0);});render();if(phase===1)reveal(j);};
 });
 function render(){const compact=window.innerWidth<700,step=compact?23:42,leftCount=Math.ceil(count/2);
  const axes=mode?labels.map((label,j)=>{const valid=values[j].filter(finite);return {id:'metric-'+j,type:'value',min:valid.length?Math.min(...valid):0,max:valid.length?Math.max(...valid):1,show:state[j].visible,position:j<leftCount?'left':'right',offset:(j<leftCount?j:j-leftCount)*step,name:String(j+1),nameLocation:'end',nameTextStyle:{color:PALETTE[j%PALETTE.length],fontFamily:FONT},axisLine:{show:true,lineStyle:{color:PALETTE[j%PALETTE.length]}},axisLabel:{fontSize:compact?12:14,color:'#4B4B4B',formatter:v=>Number(v.toPrecision(3)).toString()},splitLine:{show:false}}}):original.yAxis;
  const series=labels.map((name,j)=>({id:'info-'+j,type:'scatter',name,yAxisIndex:mode?j:0,data:values[j].map((v,k)=>({id:String(points[k].id),value:[k,mode?v:j,v]})),symbolSize:v=>!finite(v[2])||mode&&!state[j].visible?0:mode?(j===last?10:7):original.series[j].symbolSize(v),itemStyle:{color:PALETTE[j%PALETTE.length],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}}}));
  labels.forEach((_,j)=>{const f=fits[j],enabled=mode&&state[j].visible,fit=regressionSeries(f,1.96,true);
   series.push({...fit[0],id:'info-line-'+j,type:'line',silent:true,yAxisIndex:mode?j:0,data:enabled&&state[j].line&&f?fit[0].data:[],lineStyle:{color:PALETTE[j%PALETTE.length],width:2,type:f&&f.r2>=.5?'solid':'dashed'}});
   series.push({...fit[1],id:'info-band-'+j,type:'custom',silent:true,clip:true,yAxisIndex:mode?j:0,data:enabled&&state[j].band&&f?[0]:[],renderItem:f?(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+1.96*p[2]])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-1.96*p[2]]))]},style:{fill:PALETTE[j%PALETTE.length],opacity:.14}}):()=>null});
  });
  series.push({id:'focus-ring',type:'scatter',silent:true,yAxisIndex:mode?last:0,data:[],symbolSize:27,itemStyle:{color:'transparent',borderColor:PALETTE[last%PALETTE.length],borderWidth:2,opacity:1},z:10});
  c.setOption({animation:true,animationDurationUpdate:850,animationEasingUpdate:'cubicInOut',grid:{left:mode?step*(leftCount-1)+42:150,right:mode?step*(count-leftCount-1)+42:25,top:40,bottom:82},xAxis:mode?{type:'value',min:0,max:points.length-1,data:[],axisLabel:{show:false},axisTick:{show:false},name:{quality:'所有点位（按界面品质从低到高）',mix:'所有点位（按综合混合度从低到高）',vitality:'所有点位（按空间活力度从低到高）'}[kind],nameLocation:'middle',nameGap:34}:original.xAxis,yAxis:axes,series},{replaceMerge:'yAxis'});
  controls.hidden=!mode;positionAxisControls(controls,c,count);c.reflow=()=>positionAxisControls(controls,c,count);
  const text=(mode?count+'组散点叠加，各自独立纵轴从小到大；轴号依次对应：'+labels.join('、')+'。同一指标按钮依次点击：单项散点与回归动画 → 仅单项散点 → 全部指标。换点其他指标从第一步开始。不同指标的绝对高度不可直接比较。':'每列为一个点位（按综合评分升序，缺失评分置后），每行代表一个指标，点大小表示该行相对大小。')+'\n悬停联动同一点位，综合评分加外圈；切换视图时点位平滑移动。\n'+(quality?'界面品质：11项指标按全域最小最大值标准化后，依系数表征权重求和。':mix?MFORM:SFORM);
  if(parent===W)note(text);else caption.textContent=text;
  if(parent===W)caption.textContent='回归横轴为综合评分排序，不代表时间或空间距离。OLS：ŷ=a+bx，b=Σ[(x−x̄)(y−ȳ)]/Σ(x−x̄)²，a=ȳ−bx̄。\n条带=ŷ±1.96×s√[1/n+(x−x̄)²/Σ(x−x̄)²]，s²=Σ(y−ŷ)²/(n−2)。R²≥0.5实线，其余虚线；不将顺序趋势解释为因果。';
 }
 tabs(nav,['校准展示','散点图'],i=>{cancelReveal();selected=-1;phase=0;state.forEach(s=>{s.visible=true;s.line=false;s.band=false;});controls.querySelectorAll('button').forEach(b=>{b.setAttribute('aria-pressed','false');b.dataset.phase='0';});mode=i;render();});
 if(parent!==W)el('p','caption',host).textContent='OLS以综合评分排序为横轴：ŷ=a+bx，b=Σ[(x−x̄)(y−ȳ)]/Σ(x−x̄)²，a=ȳ−bx̄。条带=ŷ±1.96×SE，SE=s√[1/n+(x−x̄)²/Σ(x−x̄)²]，s²=Σ(y−ŷ)²/(n−2)。顺序趋势不表示时间、距离或因果。';
 c.setOption({tooltip:{formatter:p=>{const i=(p.data.value||p.data)[0],node=points[i];return node?esc(node.address)+'<br>'+labels.filter((_,j)=>!mode||state[j].visible).map(name=>{const j=labels.indexOf(name);return esc(name)+'：'+fmt(values[j][i])}).join('<br>'):''}}});
 c.on('mouseover',p=>{if(p.seriesIndex>=count)return;const i=(p.data.value||p.data)[0];c.dispatchAction({type:'downplay'});labels.forEach((_,j)=>{if(!mode||state[j].visible)c.dispatchAction({type:'highlight',seriesId:'info-'+j,dataIndex:i});});c.setOption({series:[{id:'focus-ring',data:finite(values[last][i])&&(!mode||state[last].visible)?[[i,mode?values[last][i]:last]]:[]}]});});
 c.on('globalout',()=>{c.dispatchAction({type:'downplay'});c.setOption({series:[{id:'focus-ring',data:[]}]});});
}
function scatter(parent,xkey,ykey,title){
 const c=chart(parent),o=base(),series=[],all=[];delete o.legend;o.title={text:title,left:'center',textStyle:{fontFamily:FONT,fontSize:16,color:INK}};o.xAxis=axis(D.headers[xkey]);o.yAxis=axis(D.headers[ykey]);
 [...new Set(D.points.map(p=>p.road))].forEach((road,j)=>{const data=D.points.filter(p=>p.road===road&&finite(p.values[xkey])&&finite(p.values[ykey])).map(p=>[p.values[xkey],p.values[ykey],p.address]);all.push(...data);
  if(data.length)series.push({id:'road-points-'+j,name:road,type:'scatter',data,symbolSize:8,itemStyle:{color:'#72a9bc',opacity:.65},emphasis:{itemStyle:{color:'#4d74a0',opacity:1},scale:1.4}});
  const f=fittedRegression(data);if(f)series.push({id:'road-fit-'+j,name:road,type:'line',data:f.points.map(p=>p.slice(0,2)),showSymbol:false,silent:true,lineStyle:{color:'#929292',width:1,opacity:.4,type:f.r2>=.5?'solid':'dashed'},emphasis:{lineStyle:{color:'#666666',opacity:1,width:2.5}}});
 });
 const f=fittedRegression(all);if(f){series.push(...regressionSeries(f));o.graphic=[{type:'text',right:18,bottom:8,style:{text:`y=${fmt(f.slope)}x+${fmt(f.intercept)}\nR²=${fmt(f.r2)} · n=${f.n}`,fill:'#4B4B4B',font:'12px '+FONT,lineHeight:17,textAlign:'right'}}];}
 o.series=series;o.tooltip.formatter=p=>p.seriesType==='scatter'?`${esc(p.data[2])}<br>${esc(D.headers[xkey])}：${fmt(p.data[0])}<br>${esc(D.headers[ykey])}：${fmt(p.data[1])}`:'';c.setOption(o);c.on('mouseover',p=>{if(p.seriesType==='scatter')highlight(p.seriesName)});c.on('globalout',()=>highlight(null));
}

function correlationColor(value){return chartScale(value)}
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
   if(!o.series.some(s=>s.data.length))o.graphic=[{type:'text',left:'center',top:'middle',style:{text:'本组案例均缺少“'+xlabel+'”，无法绘制该横轴下的散点',font:'16px '+FONT,fill:'#686868'}}];
   o.tooltip.formatter=p=>{const value=p.data.value||p.data;return esc(value[2])+'<br>'+esc(xlabel)+'：'+fmt(value[0])+'<br>'+esc(p.seriesName)+'：'+fmt(value[1]);};
   c.setOption(o,{notMerge:true});
   const missing=dimensions.filter(([key])=>!analysis.points.some(p=>finite(getx(p))&&finite(gety(p,key)))).map(d=>d[1]);
   caption.textContent='本组 '+cases.length+' 个案例点位同时显示；当前地址的点加大并加深，其余点保留为淡色。每种颜色对应一个纵轴指标；点上不显示文字，悬停查看地址和数值。横轴按同组全部点位统一取值并留出边距，切换地址不改变范围。不同指标单位不同，不按纵坐标高低比较优劣。'+(missing.length?'\n当前选中案例无法绘制：'+missing.join('、')+'。缺失值不填零，也不使用其他点位补足。':'')+'\n节点样本不足时，不绘制回归线或显著差异圈。';
  });
  if(previousX)xnav.children[previousX].click();
 });
}

// Shared nested navigation keeps the outer selection while reusing existing charts.
function sectionTabs(labels,render){const nav=el('div','subtabs');tabs(nav,labels,i=>{charts.forEach(c=>c.dispose());charts=[];Array.from(W.children).forEach(n=>{if(n!==nav)n.remove();});document.body.classList.remove('screen-analysis');render(i);});}
function mixingSection(){sectionTabs(['信息散点图','全域与所有街道',...D.admins.map(g=>g.name)],i=>{if(i===0){informationExplorer(W,'mix');return;}diversity(i-1);});}
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
 el('details','critic-method',box).innerHTML="<summary>Critic权重算法</summary>\n<h3>1. 对比强度</h3><p class=\"formula\">S_j = √ [ (1/(n-1)) × Σ(x_ij - x̄_j)² ]</p>\n<p>x_ij 是第i个样本第j个指标的值，x̄_j 是第j个指标的均值。\nΣ是对i从1到n求和。</p>\n<p>标准差越大，说明这个指标越能区分不同样本，越重要。</p>\n<h3>2. 冲突性</h3><p class=\"formula\">R_j = Σ (1 - |r_jk|)</p>\n<p>其中 r_jk 是第j个指标和第k个指标的皮尔逊相关系数，|r_jk| 是取绝对值。\nΣ是对k从1到m求和。\n当k=j时，自己跟自己的相关系数是1，1减1等于0，所以自己那一项自动为0。</p>\n<p>R_j越大，说明这个指标跟别人越不相关，提供的信息越独特。</p>\n<h3>3. 综合信息量及权重</h3><p class=\"formula\">C_j = S_j × R_j</p><p class=\"formula\">w_j = C_j / ΣC_j</p>\n<p>其中ΣC_j是对所有指标的C_j求和。</p>";
 const lower=el('div','coefficient-tables',box),left=el('section','',lower),right=el('section','',lower);
 const table=el('table','coefficient-table',left);table.innerHTML='<thead><tr><th>指标</th><th>系数</th><th>权重</th></tr></thead><tbody>'+defs.map(d=>'<tr><td>'+d[1]+'</td><td>'+d[0]+'</td><td>'+d[2].toFixed(3)+'</td></tr>').join('')+'</tbody>';
 if(kind==='mix')el('p','coefficient-conclusion',left).textContent="进一步结合指标相关性与CRITIC权重分析可见，姿态丰富度与身份倾向混合度对街区综合混合度的贡献最为突出。\n其中活动丰富度与社交状态混合度呈现较强的相关性，说明行人的行为活动与社交行为存在明显的耦合关系。\n而年龄混合度权重相对较低，对整体混合度的解释力有限。\n由此可以推测，街道空间能否容纳多样化的身体姿态行为、能否吸引多元身份人群到访，是提升街区混合度的核心驱动要素。";
 const label={mix:'混合度',quality:'界面品质',vitality:'活力度'}[kind],key=kind==='mix'?'mixScore':kind;el('h2','section-heading',right).textContent=label+'总表';
 const wrap=el('div','score-table-wrap',right),scores=el('table','coefficient-table score-table',wrap);scores.innerHTML='<thead><tr><th>地址</th><th>'+label+'</th></tr></thead><tbody>'+D.points.map(p=>'<tr><td>'+esc(p.address)+'</td><td>'+fmt(p[key],6)+'</td></tr>').join('')+'</tbody>';
 note(kind==='mix'?"第d维混合度 H_d=−Σ(p_k×ln p_k)/ln K_d；p_k=类别频数/该维频数合计，0×ln0记0。\n零合计或缺失不评分。\n综合混合度 M=0.149H年龄+0.141H活动+0.250H身份倾向+0.228H姿态+0.233H社交状态。\n权重按给定公式顺序使用，不二次归一化。\n权重说明保留给定w1–w5名称；综合混合度（综合评分）按指定M公式的维度顺序代入。":SFORM+'\n'+D.scoreWeights[kind].map(d=>d[1]+' '+d[2].toFixed(3)).join('；'));
}
function dimensionBars(i){
 const d=D.mixDimensions[i],points=D.points,c=chart(W,Math.max(650,points.length*28+140)),o=base();
 o.animation=true;o.title={text:d.label,left:'center',textStyle:{fontFamily:FONT,fontSize:18}};o.legend={type:'scroll',top:35,textStyle:{fontFamily:FONT}};o.grid={left:220,right:125,top:90,bottom:50};
 o.xAxis={...axis('类别权重 pₖ'),min:0,max:1,axisLabel:{formatter:v=>Math.round(v*100)+'%'}};o.yAxis={type:'category',inverse:true,data:points.map(p=>p.address),axisLabel:{interval:0,fontFamily:FONT,fontSize:12},axisTick:{show:false}};
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
function shapAnalysis(){
 /*
  * 三个“不配得性分析”页面不再根据
  * “高XX低XX / 低XX高XX”切换图片。
  *
  * 根据当前 PAGE，直接选择固定的 SHAP 图片文件夹。
  *
  * qualityVitality → 不配得性Ⅰ
  * qualityMix      → 不配得性Ⅱ
  * mismatch        → 不配得性Ⅲ
  */

 const content=window.SHAP_CAPTIONS;

 // -------------------------------------------------
 // 1. 根据当前页面决定图片文件夹
 // -------------------------------------------------
 const folderMap={
  qualityVitality:'活力度界面品质',
  qualityMix:'混合度界面品质',
  mismatch:'活力度混合度'
 };

 // -------------------------------------------------
// 三个不配得性页面的文字内容
//
// 每个页面有三组文字，分别对应：
// 1.png
// 2.png
// 3.png
//
// description = 上方正文
// conclusion  = 下方结论
// -------------------------------------------------
const textMap={

 qualityVitality:[
  {
   description:'这里填写不配得性Ⅰ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅰ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅰ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第三张图片旁边的结论。'
  }
 ],

 qualityMix:[
  {
   description:'这里填写不配得性Ⅱ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅱ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅱ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第三张图片旁边的结论。'
  }
 ],

 mismatch:[
  {
   description:'这里填写不配得性Ⅲ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅲ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅲ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第三张图片旁边的结论。'
  }
 ]

};

 const folder=folderMap[PAGE];

 /*
  * 理论上本函数只会在三个不配得性页面中调用。
  * 如果以后代码结构改变，这里可以避免出现错误路径。
  */
 if(!folder){
  note('当前页面没有配置不配得性分析图片。');
  return;
 }

 // -------------------------------------------------
 // 2. 保留原来的标题位置(已经不要啦！)
 // -------------------------------------------------
 

 // -------------------------------------------------
 // 3. 保留原来的图片 + 右侧文字整体布局
 // -------------------------------------------------
 const gallery=el('section','shap-gallery');

 /*
  * 保留原来的文字换行规则。
  */
 const lines=s=>String(s||'')
  .replace(/([；;。])\s*/g,'$1\n')
  .trim();

 // -------------------------------------------------
 // 4. 固定加载 1.png / 2.png / 3.png
 // -------------------------------------------------
 [1,2,3].forEach((number,index)=>{

  // 每一行仍然使用：
  // 左侧图片 + 右侧文字
  const figure=el('figure','shap-figure',gallery);
  const row=el('div','shap-row',figure);

  // 图片
  const img=el('img','shap-image',row);

  /*
   * 最终浏览器路径：
   *
   * ../assets/data/shap/活力度界面品质/1.png
   * ../assets/data/shap/活力度界面品质/2.png
   * ../assets/data/shap/活力度界面品质/3.png
   *
   * 等。
   *
   * regression_revision.py 的 pages() 会自动把
   * result/shap 整个复制到 aerial/assets/data/shap，
   * 所以不需要手工复制图片。
   */
  img.src=
   '../assets/data/shap/'
   +folder
   +'/'
   +number
   +'.png?v='
   +content.assetVersion;

  img.alt=folder+' · '+number+'.png';

  // -------------------------------------------------
  // 5. 右侧文字区域
  // -------------------------------------------------
  const side=el('aside','shap-side',row);

  /*
   * 你目前还没有准备新的文字，
   * 所以这里暂时继续沿用原来的文字数据。
   *
   * 为了避免删除“高低类型切换”之后旧 label 不存在，
   * 这里按照当前页面寻找一组已有文字作为临时内容。
   */

  // 当前图片对应的文字
const text=textMap[PAGE][index];

// 第一段正文
el('p','shap-description',side).textContent=
 lines(text.description);

// 第二段结论
el('p','shap-conclusion',side).textContent=
 lines(text.conclusion);
 });

 note('');
}
function mismatchView(i){
 const config={qualityVitality:['quality','vitality','界面品质','活力度','界面品质的底层指标组合','活力度的底层指标'],qualityMix:['quality','mixScore','界面品质','混合度','界面品质的底层指标组合','混合度的底层指标'],mismatch:['vitality','mixScore','活力度','混合度','活力度的底层指标组合','混合度的底层指标']}[PAGE], [x,y,xlabel,ylabel,first,second]=config;
 const labels=PAGE==='mismatch'?['高混合度低活力度','高活力度低混合度']:['高'+xlabel+'低'+ylabel,'高'+ylabel+'低'+xlabel],mx=D.scoreMeans[x],my=D.scoreMeans[y];
 if(i){shapAnalysis();return;}
 const c=chart(W,610),o=base();delete o.legend;o.grid={left:75,right:55,top:45,bottom:65};
 o.xAxis={...axis(xlabel),scale:true,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};o.yAxis={...axis(ylabel),scale:true,axisLine:{show:false},axisTick:{show:false},splitLine:{show:false}};
 const pts=D.points.filter(p=>finite(p[x])&&finite(p[y]));o.series=[{type:'scatter',id:'nodes',data:pts.map(p=>({value:[p[x],p[y],p.address,p.id],itemStyle:{color:p.mismatchGroups[PAGE]===labels[0]?'#0071ee':p.mismatchGroups[PAGE]===labels[1]?'#c90097':'#9094c1',opacity:p.mismatchGroups[PAGE]?.85:.4}})),symbolSize:9,z:5,emphasis:{scale:1.6},markLine:{silent:true,symbol:'none',label:{show:true,position:'insideEndTop',formatter:p=>p.data.name,color:'#000',backgroundColor:'#fff',padding:3},lineStyle:{color:'#000',type:'solid',width:1.5},data:[{xAxis:mx,name:xlabel+'均值 '+fmt(mx,4)},{yAxis:my,name:ylabel+'均值 '+fmt(my,4)}]}}];
 o.tooltip.formatter=p=>{const a=p.value;return esc(a[2])+' · '+esc(a[3])+'<br>'+xlabel+'：'+fmt(a[0])+'<br>'+ylabel+'：'+fmt(a[1])};c.setOption(o);
 note('横轴：'+xlabel+'；纵轴：'+ylabel+'。按各指标全域有效评分的平均值划分四象限：'+xlabel+'均值='+fmt(mx,6)+'，'+ylabel+'均值='+fmt(my,6)+'。左上与右下两类点位纳入不配得性分析，等于均值归高组。\nQ、V、M与各总表综合评分完全一致，缺失评分不参与筛选。');el('p','caption').textContent=labels.map(label=>label+'：'+D.points.filter(p=>p.mismatchGroups[PAGE]===label).length+' 个点位').join('；');
 if(PAGE==='mismatch')el('p','mismatch-conclusion').textContent="活力度与人群身份混合度呈显著正相关，混合度整体随活力度上升。\n散点分布显示，多数点位混合度取值略高于活力度，仅少数样本呈高活力度—低混合度的背离特征。\n据此推断，人群构成的多元化或先于街道活力的提升而发生；通过增强街道空间包容性、适配多元人群需求，可有效促进街道活力。";
}
if(PAGE==='heat')mainTabs(['热力分布图','样本数'],i=>mapView(1-i));
if(PAGE==='weights')mainTabs(['空间分析','系数表征','界面品质总表'],i=>{if(i===2)informationExplorer(W,'quality');else if(i===1)coefficient('quality');else sectionTabs(['有效空间分析','舒适度分析','效果分析'],j=>j<2?space(j):effectAnalysis());});
if(PAGE==='mixRegression')mainTabs(['系数表征','混合度总表'],i=>i?mixedTotal():coefficient('mix'));
if(PAGE==='composition')mainTabs(D.mixDimensions.map(d=>d.label),dimensionBars);
if(PAGE==='memory')mainTabs(['系数表征','活力度总表'],i=>i?informationExplorer(W,'vitality'):coefficient('vitality'));
if(PAGE==='correlations')mainTabs(['空间行为相关性分析'],matrixWithAxes);
if(['qualityVitality','qualityMix','mismatch'].includes(PAGE))mainTabs(['筛选','不配得性分析'],mismatchView);

let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>charts.forEach(c=>{c.resize();c.reflow?.()}),120)});

function rankedInformationPoints(kind){const key=kind==='quality'?'quality':kind==='mix'?'mixScore':'vitality';return D.points.map((p,i)=>({p,i})).sort((a,b)=>{const x=a.p[key],y=b.p[key];return finite(x)&&finite(y)?x-y||a.i-b.i:finite(x)?-1:finite(y)?1:a.i-b.i;}).map(v=>v.p);}
function positionAxisControls(controls,c,count){
 const compact=window.innerWidth<700,step=compact?23:42,leftCount=Math.ceil(count/2),width=c.getWidth(),height=c.getHeight();
 const left=step*(leftCount-1)+42,right=step*(count-leftCount-1)+42;
 controls.style.top=(height-65)+'px';
 Array.from(controls.children).forEach((card,j)=>{card.style.left=(j<leftCount?left-j*step:width-right+(j-leftCount)*step)+'px';});
}
function enableChartDownload(c,node){
 const original=c.setOption.bind(c);
 c.setOption=(option,...args)=>original({...option,toolbox:{show:true,right:4,bottom:3,itemSize:15,showTitle:true,iconStyle:{borderColor:'#999',borderWidth:1},emphasis:{iconStyle:{borderColor:'#333'}},feature:{mySaveAsImage:{show:true,title:'下载 PNG',icon:'path://M4,16 L4,21 L20,21 L20,16 M12,2 L12,16 M6,10 L12,16 L18,10',onclick:()=>window.exportAnnotatedChart(c,node)}}}},...args);
}
function saveCanvasPNG(canvas,name){const link=document.createElement('a');link.download=name+'.png';link.href=canvas.toDataURL('image/png');link.click();}
async function exportDOMChart(node){
 await document.fonts.load('300 16px FZLanTingHei');
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
  node.querySelectorAll('.cov-row-label,.cov-col-label,.cov-detail').forEach(label=>{if(!label.getClientRects().length||label.closest('[hidden]'))return;const r=label.getBoundingClientRect(),css=getComputedStyle(label);ctx.fillStyle='rgba(255,255,255,.92)';ctx.fillRect(r.left-rect.left,r.top-rect.top,r.width,r.height);ctx.font='300 '+css.fontSize+' FZLanTingHei, SimHei, sans-serif';ctx.fillStyle=css.color;ctx.textBaseline='middle';ctx.fillText(label.textContent,r.left-rect.left+5,r.top-rect.top+r.height/2,r.width-10);});
 }
 saveCanvasPNG(canvas,(document.title||'图表').split('｜')[0]);
}
function attachDOMDownloads(){document.querySelectorAll('.map-stage,.covariance').forEach(node=>{if(node.querySelector('.dom-chart-download'))return;const button=document.createElement('button');button.className='dom-chart-download';button.title='下载 PNG';button.setAttribute('aria-label','下载图表 PNG');button.textContent='⇩';button.onclick=async event=>{event.stopPropagation();button.disabled=true;try{await exportDOMChart(node);}catch(error){button.title='下载失败，请重试';console.error(error);}finally{button.disabled=false;}};node.append(button);});}
if(typeof MutationObserver!=='undefined'){new MutationObserver(attachDOMDownloads).observe(W,{childList:true,subtree:true});attachDOMDownloads();}
if(document.fonts)document.fonts.load('16px SimSun').then(()=>charts.forEach(c=>{if(!c.isDisposed())c.resize();}));

/* interaction-revision */
