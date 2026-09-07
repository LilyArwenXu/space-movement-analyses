// Mechanical update of the shared renderer and independent editable snapshots.
const fs=require('fs'),path=require('path');
const files=['aerial/assets/js/inclusive.js',...fs.readdirSync('chart_python/current').filter(n=>/^\d\d_.*\.py$/.test(n)).map(n=>'chart_python/current/'+n)];
for(const file of files){
 let s=fs.readFileSync(file,'utf8');
 const colors={'#181818':'#292929','#111':'#292929','#222':'#292929','#000':'#292929','#333':'#4B4B4B','#555':'#4B4B4B','#666':'#4B4B4B','#777':'#A4A6A7','#888':'#A4A6A7','#aaa':'#A4A6A7','#bbb':'#C6B8A7','#ccc':'#C6B8A7','#ddd':'#C6B8A7','#eee':'#A4A6A7','#e2e2e2':'#FCB45E','#e8e8e8':'#C6B8A7','#999':'#A4A6A7'};
 s=s.replace(/#[0-9a-fA-F]{3,8}\b/g,c=>colors[c]||c);
 s=s.replace("INK='#292929';","INK='#292929', PALETTE=['#A4A6A7','#C6B8A7','#FCB45E','#292929','#4B4B4B'];");
 s=s.replace("backgroundColor:'#fff',textStyle", "backgroundColor:'#fff',color:PALETTE,textStyle");
 s=s.replace("legend:{top:8,type:'scroll'", "legend:{top:38,left:20,right:20,type:'scroll'");
 s=s.replace('colors=[[33,102,172],[103,169,207],[247,247,247],[244,165,130],[178,24,43]]','colors=[[164,166,167],[182,175,167],[198,184,167],[225,182,130],[252,180,94]]');
 s=s.replace("mode?'#292929':'#292929'","mode?'#292929':'#FCB45E'");
 s=s.replace("冷色表示人数少，暖色表示人数多", "灰色表示人数少，橙色表示人数多");
 s=s.replace("color:['#292929','#4B4B4B','#A4A6A7','#A4A6A7','#C6B8A7','#A4A6A7'][j]", "color:['#292929','#4B4B4B','#A4A6A7','#C6B8A7','#FCB45E','#A4A6A7'][j],opacity:j===5?.55:1");
 s=s.replace("color:j<3?'#fff':'#292929'", "color:j<2?'#fff':'#292929'");
 s=s.replace("lineStyle:{color:'#292929',opacity:j?.35:1", "lineStyle:{color:PALETTE[j%5],opacity:j?.7:1");
 s=s.replace("itemStyle:{color:'#4B4B4B'},data:[{name:g.name,value:g.mix}]", "itemStyle:{color:PALETTE[j%5]},data:[{name:g.name,value:g.mix}]");
 s=s.replace("const c=chart(parent),o=base(),series=[],all=[];", "const c=chart(parent),o=base(),series=[],all=[];delete o.legend;");
 s=s.replace("text:title,left:'center',top:12", "text:title,left:'center',top:8");
 s=s.replace("function scorePlot(parent,points,key,title){const valid=points.filter(p=>finite(p[key])),container=el('div','score-wrap',parent),c=chart(container,480),o=base();", "function scorePlot(parent,points,key,title){const compact=key==='mixScore',valid=points.filter(p=>finite(p[key])),container=el('div',compact?'score-wrap score-fit':'score-wrap',parent),c=chart(container,480),o=base();delete o.legend;");
 s=s.replace("o.grid={left:60,right:30,top:80,bottom:120};o.xAxis={...axis(),type:'category',data:valid.map(p=>p.name),axisLabel:{rotate:45,interval:0,fontSize:10,fontFamily:FONT}};", "o.grid={left:60,right:24,top:80,bottom:compact?45:120,containLabel:true};o.xAxis={...axis(),type:'category',data:valid.map(p=>p.name),axisTick:{show:!compact},axisLabel:{show:!compact,rotate:45,interval:0,fontSize:10,fontFamily:FONT}};");
 s=s.replace("text:'行为集中度：洛伦兹曲线',left:'center',textStyle", "text:'行为集中度：洛伦兹曲线',left:'center',top:5,textStyle");
 s=s.replace("o.grid={left:55,right:20,top:60,bottom:115};", "o.legend={...o.legend,top:40,left:10,right:10};o.grid={left:55,right:20,top:92,bottom:115,containLabel:true};");
 const before="const grid=el('div','chart-grid');if(i===0)[['M','空间有效性分析'],['S','空间承载力分析'],['R','消费空间占比分析']].forEach(([y,t])=>scatter(grid,'K',y,t));else[['AE','遮荫率'],['AF','声环境舒适度'],['AG','气味环境']].forEach(([y,t])=>scatter(grid,'T',y,t));";
 const after="if(i===0){const sub=el('div','subtabs'),host=el('div','single-space-chart');const options=[['M','空间有效性分析'],['S','空间承载力分析'],['R','消费空间占比分析']];tabs(sub,options.map(v=>v[1]),j=>{charts.forEach(c=>c.dispose());charts=[];host.replaceChildren();scatter(host,'K',options[j][0],options[j][1]);});}else{const grid=el('div','chart-grid');[['AE','遮荫率'],['AF','声环境舒适度'],['AG','气味环境']].forEach(([y,t])=>scatter(grid,'T',y,t));}";
 s=s.replace(before,after);
 fs.writeFileSync(file,s);
}
console.log('Updated shared chart renderer and eight editable Python snapshots.');
