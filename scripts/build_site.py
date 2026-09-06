from pathlib import Path
import shutil
from build_data import build, ROOT
build()
from build_people import build_people
build_people()
from catalog import CATALOG
for number,(renderer,route,title,kind) in enumerate(CATALOG,1):
    if kind=='weights': continue
    html=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜衡复风貌区</title><link rel="stylesheet" href="studies.css"><script src="echarts.min.js"></script><script src="survey-data.js"></script></head>
<body data-study="{renderer}" data-number="{number}" data-title="{title}"><header><a href="../visualizations.html" aria-label="返回图表目录">←</a><h1>{number:02d} {title}</h1><span class="meta"></span></header><nav role="tablist" aria-label="切换分析图表"></nav><p class="note"></p><main id="workspace" aria-label="数据图表"></main><script src="studies.js"></script></body></html>'''
    if kind=='people':
        html=html.replace('survey-data.js','people-data.js').replace('src="studies.js"','src="people-studies.js"')
    (ROOT/'spacemovement'/route).write_text(html.replace('https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js','echarts.min.js'),encoding='utf-8',newline='\n')
cards=''.join(f'''<a class="panel" href="spacemovement/{route}" aria-label="{i:02d} {title}">
  <span class="panel-spine" aria-hidden="true">{i:02d} / {title}</span>
  <div class="panel-detail"><span class="panel-number" aria-hidden="true">{i:02d}</span><h2>{title}</h2><span class="panel-link" aria-hidden="true">OPEN VISUALIZATION ⟶</span></div>
</a>''' for i,(_,route,title,_) in enumerate(CATALOG,1))
(ROOT/'aerial/visualizations.html').write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>数据可视化｜衡复风貌区</title><link rel="stylesheet" href="assets/css/visualizations.css"></head><body><header class="topbar"><a class="brand" href="index.html" aria-label="衡复风貌区，返回首页">HENG-FU DISTRICT</a><h1>DATA VISUALIZATION / {len(CATALOG):02d} STUDIES</h1></header><main class="accordion" aria-label="可视化图表目录">{cards}</main></body></html>''',encoding='utf-8',newline='\n')
(ROOT/'spacemovement/point_age_composition.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=people_composition.html#age"><title>点位年龄构成｜衡复风貌区</title></head><body><a href="people_composition.html#age">查看点位年龄构成</a></body></html>''',encoding='utf-8')
import sys
sys.path.insert(0,str(ROOT/'chart_python'))
from _export import apply_all
apply_all()
for path in (ROOT/'spacemovement').iterdir():
    if path.suffix in ['.js','.css','.html'] and path.name!='空间活力度分析报告(1).html':
        shutil.copy2(path,ROOT/'aerial/spacemovement'/path.name)
shutil.copytree(ROOT/'aerial',ROOT/'dist',dirs_exist_ok=True)
print('Built all study pages in aerial and dist.')
from prepare_pages import prepare
prepare()
