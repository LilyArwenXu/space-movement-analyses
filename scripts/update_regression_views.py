from pathlib import Path
p=Path('aerial/assets/js/analysis-revision.js')
s=p.read_text(encoding='utf-8')
s=s.replace("informationScatter(W,'vitality');return;", "vitalityInformation();return;")
s=s.replace("el('p','caption',parent).textContent=", "el('p','caption',parent).textContent=")
s=s.replace("const nav=el('div','subtabs'),host=el('div'),c=informationScatter(host,'vitality'),original=c.getOption();", "const nav=el('div','subtabs'),host=el('div'),c=informationScatter(host,'vitality'),original=c.getOption();host.querySelector('.caption').textContent='颜色区分指标；悬停显示原始数值及点位名称。校准展示以点大小编码该指标的相对大小，散点图以各自独立纵轴编码原始数值。';")
s=s.replace("symbolSize:i?(j===6?10:7):original.series[j].symbolSize", "symbolSize:i?(v=>finite(v[2])?(j===6?10:7):0):original.series[j].symbolSize")
s=s.replace("c.setOption(o);\n}\nfunction mismatch", """const f=fittedRegression(o.series[0].data);
 const controls=el('label','band-controls'),slider=el('input','',controls),value=el('span','',controls);slider.type='range';slider.min='0';slider.max='4';slider.step='0.05';slider.value='1.96';slider.setAttribute('aria-label','回归条带宽度');
 function update(){const k=Number(slider.value);value.textContent='回归条带宽度：'+k.toFixed(2)+' × 标准误';c.setOption({series:[o.series[0],...regressionSeries(f,Math.max(.000001,k),true)]},{replaceMerge:['series']});}
 c.setOption(o);update();slider.oninput=update;slider.disabled=!f;
 el('p','caption').textContent=(f?'OLS：y='+fmt(f.slope)+'x + '+fmt(f.intercept)+'；R²='+fmt(f.r2)+'；n='+f.n:'有效点不足或横轴恒定，无法拟合回归。')+'\\n条带=拟合均值 ± k×SE，SE=s√[1/n+(x−x̄)²/Σ(xᵢ−x̄)²]，s=√[Σ(yᵢ−ŷᵢ)²/(n−2)]。滑条只调整k；这是可调标准误条带，不是固定置信水平。';
}
function mismatch""")
s=s.replace("data:pts.map(p=>[p.vitality,p.mixScore,p.address])", "id:'nodes',data:pts.map(p=>[p.vitality,p.mixScore,p.address,p.id])")
s=s.replace("c.setOption(o);return;}\n note('仅显示高活力", "c.setOption(o);linkedNodeCharts();return;}\n note('仅显示高活力")
s=s.replace("其余纵轴指标直接采用总表。');", "其余纵轴指标直接采用总表。\\nOLS线性回归：R²≥0.5为深粉色实线，其余为浅粉色虚线；横轴恒定或有效点少于3不拟合。');")
s=s.replace("{type:'scatter',symbolSize:7,data:pts.map(p=>[p.mismatch,p.values[key],p.address]),itemStyle:{color:PALETTE[j%7],opacity:.65}}", "{id:'nodes',type:'scatter',symbolSize:7,data:pts.map(p=>[p.mismatch,p.values[key],p.address,p.id]),itemStyle:{color:'#607E95',opacity:.65}}")
s=s.replace("c.setOption(o);});requestAnimationFrame", "const f=fittedRegression(o.series[0].data);o.series.push(...regressionSeries(f));o.graphic=[{type:'text',right:22,bottom:5,style:{text:f?'R²='+fmt(f.r2)+' · n='+f.n:'无法拟合（缺失或恒定）',font:'11px '+FONT,fill:'#4B4B4B'}}];c.setOption(o);});linkedNodeCharts();requestAnimationFrame")
p.write_text(s,encoding='utf-8')
