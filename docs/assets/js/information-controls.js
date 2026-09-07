function vitalityInformation(){informationExplorer(W,'vitality');}
function informationExplorer(parent,kind){
 const mix=kind==='mix',keys=mix?['ageMix','activityMix','identityMix','postureMix','socialMix']:['sample','clusters','density','gather','resident','visitor'];
 const labels=[...keys.map(k=>D.ys[k]),'综合评分'],count=labels.length,last=count-1;
 const nav=el('div','subtabs',parent),host=el('div','',parent),c=informationScatter(host,kind),original=c.getOption();
 const controls=el('div','metric-controls',host),caption=host.querySelector('.caption');
 const values=keys.map(k=>D.points.map(p=>p.metrics[k]));values.push(D.points.map(p=>p[mix?'mixScore':'vitality']));
 const fits=values.map(v=>fittedRegression(v.map((y,x)=>[x,y]))),state=labels.map(()=>({visible:true,line:false,band:false}));let mode=0,selected=-1,phase=0,timer=null,generation=0;
 function cancelReveal(){generation++;if(timer!==null)clearTimeout(timer);timer=null;}
 function reveal(j){const f=fits[j];if(!f)return;const token=generation;let frame=0;
  function tick(){if(token!==generation||c.isDisposed())return;frame++;const lineProgress=Math.min(1,frame/30),bandProgress=Math.max(0,Math.min(1,(frame-30)/20));
   const end=(f.points.length-1)*lineProgress,k=Math.floor(end),points=f.points.slice(0,k+1).map(p=>p.slice(0,2));if(k<f.points.length-1){const a=f.points[k],b=f.points[k+1],t=end-k;points.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}
   c.setOption({series:[{id:'info-line-'+j,animation:false,data:points},{id:'info-band-'+j,animation:false,data:bandProgress>0?[0]:[],renderItem:(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+1.96*p[2]*bandProgress])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-1.96*p[2]*bandProgress]))]},style:{fill:PALETTE[j],opacity:.14}})}]});
   if(frame<50)timer=setTimeout(tick,30);else timer=null;
  }timer=setTimeout(tick,30);
 }
 c.off('mouseover');c.off('globalout');
 labels.forEach((label,j)=>{const card=el('div','metric-control',controls);card.style.borderTopColor=PALETTE[j];
  const main=el('button','metric-toggle',card);main.textContent=label;main.setAttribute('aria-pressed','false');main.onclick=()=>{cancelReveal();phase=selected===j?(phase+1)%3:1;selected=phase?j:-1;state.forEach((s,k)=>{s.visible=selected<0||k===selected;s.line=false;s.band=false;});controls.querySelectorAll('button').forEach((b,k)=>b.setAttribute('aria-pressed',String(k===selected)));render();if(phase===1)reveal(j);};
 });
 function render(){const compact=window.innerWidth<700,step=compact?23:42,leftCount=Math.ceil(count/2);
  const axes=mode?labels.map((label,j)=>{const valid=values[j].filter(finite);return {id:'metric-'+j,type:'value',min:valid.length?Math.min(...valid):0,max:valid.length?Math.max(...valid):1,show:state[j].visible,position:j<leftCount?'left':'right',offset:(j<leftCount?j:j-leftCount)*step,name:String(j+1),nameLocation:'end',nameTextStyle:{color:PALETTE[j],fontFamily:FONT},axisLine:{show:true,lineStyle:{color:PALETTE[j]}},axisLabel:{fontSize:compact?8:10,color:'#4B4B4B',formatter:v=>Number(v.toPrecision(3)).toString()},splitLine:{show:false}}}):original.yAxis;
  const series=labels.map((name,j)=>({id:'info-'+j,type:'scatter',name,yAxisIndex:mode?j:0,data:values[j].map((v,k)=>({id:String(D.points[k].id),value:[k,mode?v:j,v]})),symbolSize:v=>!finite(v[2])||mode&&!state[j].visible?0:mode?(j===last?10:7):original.series[j].symbolSize(v),itemStyle:{color:PALETTE[j],opacity:.5},emphasis:{scale:1.5,itemStyle:{opacity:1}}}));
  labels.forEach((_,j)=>{const f=fits[j],enabled=mode&&state[j].visible,fit=regressionSeries(f,1.96,true);
   series.push({...fit[0],id:'info-line-'+j,type:'line',silent:true,yAxisIndex:mode?j:0,data:enabled&&state[j].line&&f?fit[0].data:[],lineStyle:{color:PALETTE[j],width:2,type:f&&f.r2>=.5?'solid':'dashed'}});
   series.push({...fit[1],id:'info-band-'+j,type:'custom',silent:true,clip:true,yAxisIndex:mode?j:0,data:enabled&&state[j].band&&f?[0]:[],renderItem:f?(params,api)=>({type:'polygon',shape:{points:[...f.points.map(p=>api.coord([p[0],p[1]+1.96*p[2]])),...f.points.slice().reverse().map(p=>api.coord([p[0],p[1]-1.96*p[2]]))]},style:{fill:PALETTE[j],opacity:.14}}):()=>null});
  });
  series.push({id:'focus-ring',type:'scatter',silent:true,yAxisIndex:mode?last:0,data:[],symbolSize:27,itemStyle:{color:'transparent',borderColor:PALETTE[last],borderWidth:2,opacity:1},z:10});
  c.setOption({animation:true,animationDurationUpdate:850,animationEasingUpdate:'cubicInOut',grid:{left:mode?step*(leftCount-1)+42:150,right:mode?step*(count-leftCount-1)+42:25,top:40,bottom:50},xAxis:mode?{type:'value',min:0,max:D.points.length-1,data:[],axisLabel:{show:false},axisTick:{show:false},name:'所有点位（按总表顺序）'}:original.xAxis,yAxis:axes,series},{replaceMerge:'yAxis'});
  controls.hidden=!mode;
  const text=(mode?count+'组散点叠加，各自独立纵轴从小到大；轴号依次对应：'+labels.join('、')+'。同一指标按钮依次点击：单项散点与回归动画 → 仅单项散点 → 全部指标。换点其他指标从第一步开始。不同指标的绝对高度不可直接比较。':'每列为一个点位，每行代表一个指标，点大小表示该行相对大小。')+'\n悬停联动同一点位，综合评分加外圈；切换视图时点位平滑移动。\n'+(mix?MFORM:SFORM);
  if(parent===W)note(text);else caption.textContent=text;
  if(parent===W)caption.textContent='回归横轴为总表点位顺序，不代表时间或空间距离。OLS：ŷ=a+bx，b=Σ[(x−x̄)(y−ȳ)]/Σ(x−x̄)²，a=ȳ−bx̄。\n条带=ŷ±1.96×s√[1/n+(x−x̄)²/Σ(x−x̄)²]，s²=Σ(y−ŷ)²/(n−2)。R²≥0.5实线，其余虚线；不将顺序趋势解释为因果。';
 }
 tabs(nav,['校准展示','散点图'],i=>{cancelReveal();selected=-1;phase=0;state.forEach(s=>{s.visible=true;s.line=false;s.band=false;});controls.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed','false'));mode=i;render();});
 if(parent!==W)el('p','caption',host).textContent='OLS以总表点位顺序为横轴：ŷ=a+bx，b=Σ[(x−x̄)(y−ȳ)]/Σ(x−x̄)²，a=ȳ−bx̄。条带=ŷ±1.96×SE，SE=s√[1/n+(x−x̄)²/Σ(x−x̄)²]，s²=Σ(y−ŷ)²/(n−2)。顺序趋势不表示时间、距离或因果。';
 c.setOption({tooltip:{formatter:p=>{const i=(p.data.value||p.data)[0],node=D.points[i];return node?esc(node.address)+'<br>'+labels.filter((_,j)=>!mode||state[j].visible).map(name=>{const j=labels.indexOf(name);return esc(name)+'：'+fmt(values[j][i])}).join('<br>'):''}}});
 c.on('mouseover',p=>{if(p.seriesIndex>=count)return;const i=(p.data.value||p.data)[0];c.dispatchAction({type:'downplay'});labels.forEach((_,j)=>{if(!mode||state[j].visible)c.dispatchAction({type:'highlight',seriesId:'info-'+j,dataIndex:i});});c.setOption({series:[{id:'focus-ring',data:finite(values[last][i])&&(!mode||state[last].visible)?[[i,mode?values[last][i]:last]]:[]}]});});
 c.on('globalout',()=>{c.dispatchAction({type:'downplay'});c.setOption({series:[{id:'focus-ring',data:[]}]});});
}
function scatter(parent,xkey,ykey,title){
 const c=chart(parent),o=base(),series=[],all=[];delete o.legend;o.title={text:title,left:'center',textStyle:{fontFamily:FONT,fontSize:16,color:INK}};o.xAxis=axis(D.headers[xkey]);o.yAxis=axis(D.headers[ykey]);
 [...new Set(D.points.map(p=>p.road))].forEach((road,j)=>{const data=D.points.filter(p=>p.road===road&&finite(p.values[xkey])&&finite(p.values[ykey])).map(p=>[p.values[xkey],p.values[ykey],p.address]);all.push(...data);
  if(data.length)series.push({id:'road-points-'+j,name:road,type:'scatter',data,symbolSize:8,itemStyle:{color:'#A8C3D6',opacity:.65},emphasis:{itemStyle:{color:'#607E95',opacity:1},scale:1.4}});
  const f=fittedRegression(data);if(f)series.push({id:'road-fit-'+j,name:road,type:'line',data:f.points.map(p=>p.slice(0,2)),showSymbol:false,silent:true,lineStyle:{color:'#929292',width:1,opacity:.4,type:f.r2>=.5?'solid':'dashed'},emphasis:{lineStyle:{color:'#666666',opacity:1,width:2.5}}});
 });
 const f=fittedRegression(all);if(f){series.push(...regressionSeries(f));o.graphic=[{type:'text',right:18,bottom:8,style:{text:`y=${fmt(f.slope)}x+${fmt(f.intercept)}\nR²=${fmt(f.r2)} · n=${f.n}`,fill:'#4B4B4B',font:'12px SimSun',lineHeight:17,textAlign:'right'}}];}
 o.series=series;o.tooltip.formatter=p=>p.seriesType==='scatter'?`${esc(p.data[2])}<br>${esc(D.headers[xkey])}：${fmt(p.data[0])}<br>${esc(D.headers[ykey])}：${fmt(p.data[1])}`:'';c.setOption(o);c.on('mouseover',p=>{if(p.seriesType==='scatter')highlight(p.seriesName)});c.on('globalout',()=>highlight(null));
}
