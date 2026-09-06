from pathlib import Path
import shutil
from build_data import build, ROOT
build()
from build_people import build_people
build_people()
routes={1:'address_people_heatmaps.html',2:'street_interface_weights.html',3:'node_function_mix.html',4:'spatial_vitality.html',5:'effective_space.html',6:'comfort.html',7:'scatter_single_axis.html',8:'scatter_location.html'}
titles=['人员热力图','街道空间评分因素权重分析','节点功能混合度','空间活力度分析概述','有效空间分析','舒适度分析','不配得性Ⅰ：界面评价/行人选择','不配得性Ⅰ：区位资源/行人选择']
routes.update({9:'people_composition.html',10:'people_diversity_radar.html',11:'behavior_lorenz.html',12:'point_age_composition.html',13:'point_diversity_ci.html',14:'people_space_correlations.html'})
titles.extend(['街道人群构成','四维混合度对比','行为集中度：洛伦兹曲线','点位年龄构成','点位混合度与置信区间','人群、行为与空间关联'])
for number,route in routes.items():
    if number==2: continue
    html=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{titles[number-1]}</title><link rel="stylesheet" href="studies.css"><script src="https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script><script src="survey-data.js"></script></head>
<body data-study="{number}"><header><a href="../visualizations.html" aria-label="返回图表目录">←</a><h1>{number:02d} {titles[number-1]}</h1><span class="meta"></span></header><nav role="tablist" aria-label="切换分析图表"></nav><p class="note"></p><main id="workspace" aria-label="数据图表"></main><script src="studies.js"></script></body></html>'''
    if number>=9:
        html=html.replace('survey-data.js','people-data.js').replace('src="studies.js"','src="people-studies.js"')
    (ROOT/'spacemovement'/route).write_text(html.replace('https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js','echarts.min.js'),encoding='utf-8',newline='\n')
cards=''.join(f'''<a class="panel" href="spacemovement/{routes[i]}" aria-label="{i:02d} {titles[i-1]}">
  <span class="panel-spine" aria-hidden="true">{i:02d} / {titles[i-1]}</span>
  <div class="panel-detail"><span class="panel-number" aria-hidden="true">{i:02d}</span><h2>{titles[i-1]}</h2><span class="panel-link" aria-hidden="true">OPEN VISUALIZATION ⟶</span></div>
</a>''' for i in sorted(routes))
(ROOT/'aerial/visualizations.html').write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>数据可视化｜巨富长街区</title><link rel="stylesheet" href="assets/css/visualizations.css"></head><body><header class="topbar"><a class="brand" href="index.html" aria-label="巨富长街区，返回首页">JUFU–CHANGLE</a><h1>DATA VISUALIZATION / {len(routes):02d} STUDIES</h1></header><main class="accordion" aria-label="可视化图表目录">{cards}</main></body></html>''',encoding='utf-8',newline='\n')
for path in (ROOT/'spacemovement').iterdir():
    if path.suffix in ['.js','.css','.html'] and path.name!='空间活力度分析报告(1).html':
        shutil.copy2(path,ROOT/'aerial/spacemovement'/path.name)
shutil.copytree(ROOT/'aerial',ROOT/'dist',dirs_exist_ok=True)
print('Built all study pages in aerial and dist.')
from prepare_pages import prepare
prepare()
