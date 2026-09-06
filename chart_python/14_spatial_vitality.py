"""可编辑图表：修改 HTML / JAVASCRIPT 后运行。"""
from _export import export_chart
ROUTE = 'spatial_vitality.html'
SOURCE_SCRIPT = 'studies.js'
HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>空间活力度分析概述｜衡复风貌区</title><link rel="stylesheet" href="studies.css"><script src="echarts.min.js"></script><script src="survey-data.js"></script></head>
<body data-study="4" data-number="14" data-title="空间活力度分析概述"><header><a href="../visualizations.html" aria-label="返回图表目录">←</a><h1>14 空间活力度分析概述</h1><span class="meta"></span></header><nav role="tablist" aria-label="切换分析图表"></nav><p class="note"></p><main id="workspace" aria-label="数据图表"></main><script src="studies.js"></script></body></html>'''
JAVASCRIPT = r'''/* All study inputs come from the 0906 worksheet. Missing observations stay missing. */
const D=window.SURVEY, WHITE='#f5f5f2', POINT='#858583', ALPHA=1, LINE_ALPHA=.2;
const titles=['人员热力图','街道空间评分因素权重分析','节点功能混合度','空间活力度分析概述','有效空间分析','舒适度分析','不配得性Ⅰ：界面评价/行人选择','不配得性Ⅰ：区位资源/行人选择'];
const page=Number(document.body.dataset.study), workspace=document.querySelector('#workspace'), tabs=document.querySelector('nav'), note=document.querySelector('.note');
const displayTitle=document.body.dataset.title||titles[page-1];
document.querySelector('h1').textContent=String(document.body.dataset.number||page).padStart(2,'0')+' '+displayTitle;
document.title=displayTitle+'｜衡复风貌区';
document.querySelector('.meta').textContent='2026人因空间·'+D.rows.length+'RECORDS';
let charts=[];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n==null?'—':Number(n).toFixed(3);
function reset(){charts.forEach(c=>c.dispose());charts=[];workspace.replaceChildren();}
function chart(height){const el=document.createElement('div');el.className='plot';if(height)el.style.height=height+'px';workspace.append(el);const c=echarts.init(el);charts.push(c);return c;}
function base(){return {animation:false,backgroundColor:'#090909',textStyle:{color:WHITE,fontFamily:'Times New Roman, SimSun, Songti SC, serif'},tooltip:{confine:true,backgroundColor:'#181818',borderColor:'#777',textStyle:{color:WHITE}},grid:{left:85,right:35,top:70,bottom:100},xAxis:axis(),yAxis:axis()};}
function axis(name=''){return {type:'value',name,nameLocation:'middle',nameGap:40,axisLabel:{color:'#bbb'},nameTextStyle:{color:'#ddd'},axisLine:{show:true,lineStyle:{color:'#666'}},splitLine:{lineStyle:{color:'#262626'}}};}
function select(labels,render){tabs.replaceChildren();labels.forEach((label,i)=>{const b=document.createElement('button');b.textContent=label;b.setAttribute('role','tab');b.onclick=()=>{tabs.querySelectorAll('button').forEach(x=>x.setAttribute('aria-selected',String(x===b)));reset();render(i);};tabs.append(b);if(i===0)b.click();});}
function regression(points){const n=points.length;if(n<2)return null;let mx=points.reduce((s,p)=>s+p[0],0)/n,my=points.reduce((s,p)=>s+p[1],0)/n;let xx=0,xy=0,yy=0;points.forEach(([x,y])=>{xx+=(x-mx)**2;xy+=(x-mx)*(y-my);yy+=(y-my)**2;});if(xx===0)return null;const slope=xy/xx,intercept=my-slope*mx,r2=yy>0?xy*xy/(xx*yy):null;return {n,slope,intercept,r2,min:Math.min(...points.map(p=>p[0])),max:Math.max(...points.map(p=>p[0]))};}
function line(f,street){return {name:street,type:'line',data:[[f.min,f.slope*f.min+f.intercept],[f.max,f.slope*f.max+f.intercept]],symbol:'none',lineStyle:{color:WHITE,opacity:LINE_ALPHA,width:1,type:f.r2!==null&&f.r2>=.5?'solid':'dashed'},emphasis:{lineStyle:{color:'#fff',opacity:1,width:3}},silent:true};}
function scatter(x,y,title){const c=chart(),o=base();o.title={text:title,left:'center',top:12,textStyle:{color:WHITE,fontSize:16,fontWeight:400}};o.xAxis=axis(D.headers[x]||x);o.yAxis=axis(D.headers[y]||y);o.series=[];const all=[];D.streets.forEach(street=>{const pts=D.rows.filter(r=>r.street===street&&Number.isFinite(r[x])&&Number.isFinite(r[y])).map(r=>[r[x],r[y],r.address,street]);all.push(...pts);if(!pts.length)return;o.series.push({name:street,type:'scatter',data:pts,symbolSize:9,itemStyle:{color:POINT,opacity:ALPHA},emphasis:{itemStyle:{color:'#fff',opacity:1,borderWidth:1,borderColor:'#fff'},scale:1.3}});const f=regression(pts);if(f)o.series.push(line(f,street));});const f=regression(all);if(f){o.series.push({...line(f,'全体回归'),lineStyle:{color:WHITE,opacity:LINE_ALPHA,width:2,type:f.r2!==null&&f.r2>=.5?'solid':'dashed'}});o.graphic=[{type:'text',right:30,bottom:12,style:{text:`全体 OLS · n=${f.n}\ny = ${fmt(f.slope)}x ${f.intercept<0?'−':'+'} ${fmt(Math.abs(f.intercept))}\nR² = ${fmt(f.r2)}`,fill:'#ccc',font:'12px SimSun',lineHeight:17,textAlign:'right'}}];}o.tooltip.formatter=p=>p.seriesType==='scatter'?`${esc(p.data[2])}<br>${esc(o.xAxis.name)}：${fmt(p.data[0])}<br>${esc(o.yAxis.name)}：${fmt(p.data[1])}`:'';c.setOption(o);c.on('mouseover',p=>{if(p.seriesType==='scatter')highlight(p.seriesName);});c.on('globalout',()=>highlight(null));c.on('mouseout',()=>highlight(null));return c;}
function highlight(street){charts.forEach(c=>{const s=c.getOption().series||[];s.forEach((v,i)=>{c.dispatchAction({type:street&&v.name===street?'highlight':'downplay',seriesIndex:i});});});}
function scatterNote(){note.textContent='同街道点与回归线悬停联动；白点为完整有效观测。实线 R²≥0.5，虚线 R²<0.5 或无法定义；粗线为全体回归，细线为街道回归。缺失值不补零。';}
// Fixed, densely packed address slots. Filtering never changes coordinates.
let peopleRange=null;
function heat(i){
  const keys=['AU','AV','AX','AY','BA','BB'],key=keys[i];
  const max=Math.max(1,...D.nodes.flatMap(r=>keys.map(k=>r[k]||0)));
  const c=chart(),o=base(),columns=Array.from({length:D.nodes.length},(_,j)=>j+1).filter(n=>D.nodes.length%n===0).sort((a,b)=>Math.abs(a-Math.sqrt(D.nodes.length)*1.6)-Math.abs(b-Math.sqrt(D.nodes.length)*1.6))[0],rowCount=D.nodes.length/columns;
  const size=Math.max(1,Math.min(30,(c.getWidth()-40)/columns,(c.getHeight()-100)/rowCount));
  o.grid={left:(c.getWidth()-columns*size)/2,top:80,width:columns*size,height:rowCount*size};
  o.xAxis={type:'category',data:Array.from({length:columns},(_,j)=>j),show:false};
  o.yAxis={type:'category',data:Array.from({length:rowCount},(_,j)=>j),inverse:true,show:false};
  o.visualMap={type:'continuous',dimension:2,seriesIndex:1,min:0,max,
    range:peopleRange||[0,max],calculable:true,realtime:true,precision:0,
    orient:'horizontal',left:'center',top:8,itemWidth:16,itemHeight:260,
    text:['人数上限','人数下限'],textStyle:{color:'#ccc'},
    inRange:{color:['#444','#f5f5f2'],opacity:1},
    outOfRange:{color:['#444','#f5f5f2'],opacity:0}};
  const slots=D.nodes.map((n,j)=>[j%columns,Math.floor(j/columns),0,n.address,n.short,n.street]);
  const cells=D.nodes.map((n,j)=>[j%columns,Math.floor(j/columns),n[key]??0,n.address,n.short,n.street]);
  o.series=[
    {name:'地址位置',type:'heatmap',silent:true,data:slots,
      itemStyle:{color:'#151515',borderColor:'#333',borderWidth:1},
      label:{show:false},emphasis:{disabled:true}},
    {name:D.headers[key],type:'heatmap',data:cells,
      itemStyle:{opacity:1,borderColor:'#090909',borderWidth:2},
      emphasis:{itemStyle:{borderColor:'#fff',borderWidth:2}},
      label:{show:false}}
  ];
  o.tooltip.formatter=p=>`${esc(p.data[3])}<br>${esc(D.headers[key])}：${p.data[2]} 人`;
  c.setOption(o);
  c.reflowCells=()=>{const size=Math.max(1,Math.min(30,(c.getWidth()-40)/columns,(c.getHeight()-100)/rowCount));c.setOption({grid:{left:(c.getWidth()-columns*size)/2,top:80,width:columns*size,height:rowCount*size}});};
  c.on('datarangeselected',()=>{peopleRange=c.getOption().visualMap[0].range.slice();});
  note.textContent='拖动滑块筛选人数，观测缺失按0人处理。';
}
function correlationMatrix(){
  const el=document.createElement('section');el.className='report reference-matrix';workspace.append(el);
  el.innerHTML=referenceTable(REFERENCE[0])+'<p class="matrix-legend">正负号表示相关方向　　* p &lt; 0.05　 ** p &lt; 0.01　 *** p &lt; 0.001</p>';
}

function bars(){const c=chart(),o=base();o.grid={left:70,right:25,top:30,bottom:115};o.xAxis={...axis('完整地址节点'),type:'category',data:D.nodes.map(n=>n.short),axisLabel:{color:'#aaa',rotate:50,fontSize:10,interval:'auto'}};o.yAxis=axis('功能混合度');o.dataZoom=[{type:'inside'},{type:'slider',bottom:8,height:18,borderColor:'#555',fillerColor:'#ffffff22',textStyle:{color:'#aaa'}}];o.series=[{type:'bar',data:D.nodes.map(n=>n.O),itemStyle:{color:POINT,opacity:ALPHA},emphasis:{itemStyle:{color:'#fff',opacity:1}}}];o.tooltip.formatter=p=>`${esc(D.nodes[p.dataIndex].address)}<br>功能混合度：${fmt(p.value)}<br>记录数：${D.nodes[p.dataIndex].records}`;c.setOption(o);note.textContent=`${D.nodes.length} 个唯一完整地址，同一街道相邻；重复地址的功能混合度取有效值均值。拖动底部滑块可放大节点。`;}
function single(){const c=chart(80+D.streets.length*110),o=base();delete o.xAxis;delete o.yAxis;delete o.grid;o.singleAxis=[];o.series=[];o.graphic=[];const max=Math.max(...D.streets.map(s=>D.rows.filter(r=>r.street===s).length));D.streets.forEach((s,i)=>{const rows=D.rows.filter(r=>r.street===s),top=70+i*110;o.singleAxis.push({type:'value',min:-max/2,max:max/2,left:'20%',right:'13%',top,height:0,axisLabel:{show:false},axisTick:{show:false},splitLine:{show:false},axisLine:{lineStyle:{color:'#444'}}});o.graphic.push({type:'text',left:'7%',top:top-6,style:{text:s,fill:'#ddd',font:'12px SimSun'}});['AH','T'].forEach(key=>o.series.push({name:s,type:'scatter',coordinateSystem:'singleAxis',singleAxisIndex:i,data:rows.flatMap((r,j)=>Number.isFinite(r[key])?[[j-(rows.length-1)/2,r[key],r.address,key]]:[]),symbolSize:v=>key==='AH'?Math.max(Math.sqrt(v[1])*12,8):Math.max(v[1]*4,2),itemStyle:{color:key==='AH'?POINT:'transparent',opacity:ALPHA,borderColor:POINT,borderWidth:key==='AH'?0:1},emphasis:{itemStyle:{opacity:1}}}));});o.tooltip.formatter=p=>`${esc(p.data[2])}<br>${esc(D.headers[p.data[3]])}：${p.data[1]}`;c.setOption(o);note.textContent='实心圆大小表示行人样本数，空心圆大小表示界面整体状态评分；各街道颜色与透明度一致。上下滚动查看各街道，缺失指标不绘制。';}
const star=p=>p==null?'':p<.001?'***':p<.01?'**':p<.05?'*':'';
const REFERENCE=[[["自变量 X \\ 因变量 Y", "行人样本数", "行为集群数", "停留密度", "集聚比例", "年龄混合度", "居民指数", "游客指数"], ["节点空间长度(m)", "0.150", "0.083", "-0.345***", "-0.050", "0.061", "-0.064", "0.058"], ["界面退让距离(m)", "-0.023", "0.010", "-0.202*", "-0.043", "0.009", "0.008", "0.021"], ["有效停留空间面积(㎡)", "0.177", "0.157", "-0.380***", "-0.012", "0.128", "0.072", "0.050"], ["功能混合度", "0.096", "0.001", "0.016", "-0.065", "0.087", "0.002", "-0.216*"], ["人均消费水平(元/人)", "0.061", "0.050", "-0.048", "0.067", "-0.026", "-0.022", "-0.012"], ["消费型停留空间占比(%)", "0.173", "0.067", "0.083", "-0.191", "0.186*", "0.259**", "-0.121"], ["可承载停留人数(人)", "0.186", "0.163", "-0.130", "-0.137", "0.098", "0.054", "-0.078"], ["界面整体状态", "-0.070", "-0.114", "0.019", "0.062", "-0.123", "-0.369***", "0.072"], ["界面开放度", "0.015", "-0.029", "-0.092", "-0.014", "0.150", "0.078", "0.168"], ["临街互动性", "-0.008", "-0.145", "0.033", "-0.243*", "0.149", "0.073", "0.155"], ["视觉丰富度", "0.022", "-0.020", "0.071", "0.048", "-0.027", "-0.107", "0.087"], ["历史感知度", "-0.013", "-0.066", "0.107", "-0.089", "0.031", "0.025", "-0.082"], ["路面状态", "-0.181", "-0.173", "0.008", "-0.028", "-0.124", "-0.149", "-0.067"], ["遮荫率(%)", "-0.125", "-0.101", "-0.033", "-0.140", "0.057", "0.132", "-0.089"], ["声环境舒适度", "-0.020", "0.050", "-0.070", "0.018", "-0.110", "-0.087", "0.061"], ["气味环境", "0.022", "0.042", "-0.019", "0.038", "-0.088", "-0.036", "-0.021"]], [["自变量 X \\ 因变量 Y", "行人样本数", "行为集群数", "停留密度", "集聚比例", "年龄混合度", "居民指数", "游客指数"], ["节点空间长度(m)", "0.1222", "0.3914", "0.0001", "0.6108", "0.4910", "0.5098", "0.5512"], ["界面退让距离(m)", "0.8102", "0.9213", "0.0238", "0.6613", "0.9228", "0.9376", "0.8316"], ["有效停留空间面积(㎡)", "0.0679", "0.1065", "0.0000", "0.8990", "0.1452", "0.4612", "0.6104"], ["功能混合度", "0.3162", "0.9888", "0.8605", "0.4990", "0.3204", "0.9801", "0.0233"], ["人均消费水平(元/人)", "0.5383", "0.6158", "0.6036", "0.4987", "0.7685", "0.8216", "0.9033"], ["消费型停留空间占比(%)", "0.0769", "0.4999", "0.3656", "0.0506", "0.0362", "0.0077", "0.2197"], ["可承载停留人数(人)", "0.0564", "0.0944", "0.1521", "0.1601", "0.2702", "0.5846", "0.4241"], ["界面整体状态", "0.4676", "0.2367", "0.8333", "0.5220", "0.1555", "0.0001", "0.4578"], ["界面开放度", "0.8760", "0.7644", "0.3097", "0.8820", "0.0846", "0.4151", "0.0791"], ["临街互动性", "0.9325", "0.1320", "0.7168", "0.0106", "0.0852", "0.4512", "0.1067"], ["视觉丰富度", "0.8185", "0.8380", "0.4343", "0.6210", "0.7565", "0.2658", "0.3644"], ["历史感知度", "0.8911", "0.4908", "0.2354", "0.3579", "0.7247", "0.7918", "0.3957"], ["路面状态", "0.0586", "0.0702", "0.9319", "0.7707", "0.1559", "0.1198", "0.4878"], ["遮荫率(%)", "0.1942", "0.2968", "0.7130", "0.1472", "0.5188", "0.1705", "0.3560"], ["声环境舒适度", "0.8327", "0.6070", "0.4396", "0.8506", "0.2098", "0.3690", "0.5276"], ["气味环境", "0.8195", "0.6683", "0.8349", "0.6916", "0.3169", "0.7093", "0.8249"]], [["自变量X", "因变量Y", "Spearman_ρ", "p值", "显著性", "n"], ["有效停留空间面积(㎡)", "停留密度", "-0.38", "0.0", "***", "125"], ["节点空间长度(m)", "停留密度", "-0.345", "0.0001", "***", "125"], ["界面整体状态", "居民指数", "-0.369", "0.0001", "***", "110"], ["消费型停留空间占比(%)", "居民指数", "0.259", "0.0077", "**", "105"], ["临街互动性", "集聚比例", "-0.243", "0.0106", "*", "110"], ["功能混合度", "游客指数", "-0.216", "0.0233", "*", "110"], ["界面退让距离(m)", "停留密度", "-0.202", "0.0238", "*", "125"], ["消费型停留空间占比(%)", "年龄混合度", "0.186", "0.0362", "*", "127"]]];
function referenceTable(rows){return '<table><thead><tr>'+rows[0].map(t=>'<th scope="col">'+esc(t)+'</th>').join('')+'</tr></thead><tbody>'+rows.slice(1).map(row=>'<tr>'+row.map((v,j)=>j===0?'<th scope="row">'+esc(v)+'</th>':'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';}
function report(i){
 note.textContent='* p<0.05，** p<0.01，*** p<0.001；相关性不表示因果。';
 if(i===5){correlationMatrix();return;}
 const el=document.createElement('section');el.className='report';workspace.append(el);
 if(i>=1&&i<=3){el.innerHTML=referenceTable(REFERENCE[i-1]);return;}
 if(i===0){el.innerHTML='<h2>空间属性与行人行为</h2><p>16项空间属性 × 7项行人行为指标，共112对关联。</p><p>显著相关对：'+(REFERENCE[2].length-1)+' 对。</p><p>'+REFERENCE[0][0].slice(1).map(esc).join('、')+'</p>';return;}
 el.innerHTML='<h2>显著关联概述</h2>'+REFERENCE[2].slice(1).map(r=>'<p>'+esc(r[0])+'与'+esc(r[1])+'呈'+(parseFloat(r[2])>0?'正':'负')+'相关：ρ='+esc(r[2])+'，p='+esc(r[3])+'，n='+esc(r[5])+'。</p>').join('')+'<p>关联结果不用于推断因果关系。</p>';
}

if(page===1)select(['观察人数','光顾人数','打卡人数','社交人数','饮食人数','休憩人数'],heat);
if(page===3)bars();
if(page===4)select(['数据概况','Spearman相关系数','p值矩阵','显著相关对','分析结论','Spearman图表'],report);
if(page===5)select(['空间有效性分析','空间承载力分析','消费空间占比分析'],i=>{scatterNote();scatter('K',['M','S','R'][i],['空间有效性分析','空间承载力分析','消费空间占比分析'][i]);});
if(page===6){scatterNote();['AE','AF','AG'].forEach((key,i)=>scatter('T',key,['遮荫率','声环境舒适度','气味环境'][i]));}
if(page===7)single();
if(page===8){D.headers.position='街道内节点区位比例';D.headers.choice='行人样本数 / 界面整体状态';scatterNote();note.textContent+=' 区位比例沿用原图门牌顺序归一化定义；评分为0的比值不绘制。';scatter('T','AH','界面整体状态 / 行人样本数');scatter('position','choice','区位比例 / 行人选择比值');}
new ResizeObserver(()=>charts.forEach(c=>{c.resize();if(c.reflowCells)c.reflowCells();})).observe(workspace);
'''

if __name__ == '__main__':
    export_chart(ROUTE, HTML, JAVASCRIPT, SOURCE_SCRIPT)
