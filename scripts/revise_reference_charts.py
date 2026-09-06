"""Apply the requested reference-report revision to editable chart snapshots."""
from pathlib import Path
import re, json, runpy, sys
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'chart_python'))
source=(ROOT/'spacemovement/空间活力度分析报告(1).html').read_text(encoding='utf-8')
tables=re.findall(r'<table\b[^>]*>(.*?)</table>',source,re.S)
def cells(table):
 return [[unescape(re.sub('<[^>]+>','',c)).strip() for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.S)] for row in re.findall(r'<tr[^>]*>(.*?)</tr>',table,re.S)]
report=[cells(t) for t in tables[:3]]
assert len(report[0])==17 and len(report[1])==17 and all(len(r)==8 for r in report[0])
for number in ['01','05','11','14']:
 path=next((ROOT/'chart_python').glob(number+'_*.py'))
 cfg=runpy.run_path(str(path));s=cfg['JAVASCRIPT']
 if number=='01':
  s=s.replace("inRange:{color:['#444','#f5f5f2'],opacity:1}","inRange:{color:['#171717','#f5f5f2'],opacity:1}")
  s=s.replace("itemStyle:{color:'#151515',borderColor:'#333',borderWidth:1}","itemStyle:{color:'#101010',borderColor:'#151515',borderWidth:1}")
 if number=='05':
  s=s.replace("color:key==='AH'?POINT:'transparent',opacity:ALPHA,borderColor:POINT,borderWidth:key==='AH'?0:1", "color:key==='AH'?WHITE:'transparent',opacity:key==='AH'?.4:1,borderColor:'#f5f5f2',borderType:'solid',borderWidth:key==='AH'?0:1.5")
  s=s.replace("emphasis:{itemStyle:{opacity:1}}}));", "emphasis:{disabled:true}}));")
 if number=='11':
  s=s.replace('itemStyle:{color:shades[k],opacity:1}',"itemStyle:{color:shades[k],opacity:key==='identities'&&labels[j]==='游客倾向'?.3:1}")
 if number=='14':
  start=s.index('function correlationMatrix(){');end=s.index('\nfunction bars()',start)
  s=s[:start]+'''function correlationMatrix(){
  const el=document.createElement('section');el.className='report reference-matrix';workspace.append(el);
  el.innerHTML=referenceTable(REFERENCE[0],true)+'<p class="matrix-legend">■ 正相关　<span>■ 负相关</span>　* p &lt; 0.05　 ** p &lt; 0.01　 *** p &lt; 0.001</p>';
}
'''+s[end:]
  start=s.index('function report(i){');end=s.index('\nif(page===1)',start)
  s=s[:start]+'''const REFERENCE='''+json.dumps(report,ensure_ascii=False)+''';
function referenceTable(rows,color=false){return '<table><thead><tr>'+rows[0].map(t=>'<th>'+esc(t)+'</th>').join('')+'</tr></thead><tbody>'+rows.slice(1).map(row=>'<tr>'+row.map((v,j)=>{let style='';if(color&&j){const n=parseFloat(v),alpha=.15+Math.abs(n)*.55;style=` style="background:rgba(${n>=0?'220,53,69':'13,110,253'},${alpha})"`;}return '<td'+style+'>'+esc(v)+'</td>';}).join('')+'</tr>').join('')+'</tbody></table>';}
function report(i){
 note.textContent='* p<0.05，** p<0.01，*** p<0.001；相关性不表示因果。';
 if(i===5){correlationMatrix();return;}
 const el=document.createElement('section');el.className='report';workspace.append(el);
 if(i>=1&&i<=3){el.innerHTML=referenceTable(REFERENCE[i-1]);return;}
 if(i===0){el.innerHTML='<h2>空间属性与行人行为</h2><p>16项空间属性 × 7项行人行为指标，共112对关联。</p><p>显著相关对：'+(REFERENCE[2].length-1)+' 对。</p><p>'+REFERENCE[0][0].slice(1).map(esc).join('、')+'</p>';return;}
 el.innerHTML='<h2>显著关联概述</h2>'+REFERENCE[2].slice(1).map(r=>'<p>'+esc(r[0])+'与'+esc(r[1])+'呈'+(parseFloat(r[2])>0?'正':'负')+'相关：ρ='+esc(r[2])+'，p='+esc(r[3])+'，n='+esc(r[5])+'。</p>').join('')+'<p>关联结果不用于推断因果关系。</p>';
}
'''+s[end:]
 cfg['JAVASCRIPT']=s
 text='"""可编辑图表：修改 HTML / JAVASCRIPT 后运行。"""\nfrom _export import export_chart\n'
 for key in ['ROUTE','SOURCE_SCRIPT']:text+=key+' = '+repr(cfg[key])+'\n'
 for key in ['HTML','JAVASCRIPT']:text+=key+" = r'''"+cfg[key]+"'''\n"
 text+="\nif __name__ == '__main__':\n    export_chart(ROUTE, HTML, JAVASCRIPT, SOURCE_SCRIPT)\n"
 path.write_text(text,encoding='utf-8')
css=ROOT/'spacemovement/studies.css'
css.write_text(css.read_text(encoding='utf-8')+'''\n.reference-matrix{background:#f4f6f9;color:#2c3e50}.reference-matrix table{font-size:15px;height:calc(100% - 40px)}.reference-matrix th{background:#2c5f8a;color:white}.reference-matrix th,.reference-matrix td{border:1px solid #dde3ec;padding:10px;text-align:center}.reference-matrix td:first-child{background:#f0f5fa;text-align:left;font-weight:bold}.matrix-legend{color:#dc3545;margin:12px 0}.matrix-legend span{color:#0d6efd}\n''',encoding='utf-8')
print('Reference imported:',len(report[0])-1,'x',len(report[0][0])-1,'; significant pairs:',len(report[2])-1)
