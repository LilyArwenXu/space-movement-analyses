from pathlib import Path
import shutil
from build_data import build, ROOT
build()
from build_people import build_people
build_people()
from catalog import CATALOG
for number,(renderer,route,title,kind) in enumerate(CATALOG,1):
    if kind in ('weights','summary'): continue
    html=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜衡复风貌区</title><link rel="stylesheet" href="studies.css"><script src="echarts.min.js"></script><script src="survey-data.js"></script></head>
<body data-study="{renderer}" data-number="{number}" data-title="{title}"><header><a href="../visualizations.html" aria-label="返回图表目录">←</a><h1>{number:02d} {title}</h1><span class="meta"></span></header><nav role="tablist" aria-label="切换分析图表"></nav><p class="note"></p><main id="workspace" aria-label="数据图表"></main><script src="studies.js"></script></body></html>'''
    if kind=='people':
        html=html.replace('survey-data.js','people-data.js').replace('src="studies.js"','src="people-studies.js"')
    (ROOT/'spacemovement'/route).write_text(html.replace('https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js','echarts.min.js'),encoding='utf-8',newline='\n')
def summary_text(title):
    return {'人员热力图':'不同人数指标展示点位人群分布，颜色可以帮助快速找到聚集较多的位置。滑块适合用来筛选观察范围。','街道空间评分因素权重分析':'六项界面评分合在一起呈现街道差异，可以看出哪些街道在开放度、互动性和风貌感知上更突出。','空间活力度分析概述':'空间属性与行人行为之间存在一些明显联系，停留密度尤其值得关注。整体结果适合用来理解空间条件与活动表现的关系。','五维混合度对比':'年龄、活动、身份倾向、姿态和社交状态共同反映点位的人群多样性。不同街道及道路之间的轮廓差异，显示出使用方式并不相同。','行为集中度：洛伦兹曲线':'曲线越偏离均等线，说明少数行为占据的比重越高。按道路查看可以发现行为集中程度的空间差异。','有效空间分析':'空间长度与有效停留空间、承载能力及消费空间占比的关系，帮助判断空间是否真正支持停留。回归线可作为方向性的参考。','舒适度分析':'界面状态与遮荫、声音和气味环境放在一起比较，可以看到舒适体验的不同侧面。散点分布也反映了各点位之间的差异。','不配得性Ⅰ：界面评价/行为选择':'将界面评价与行人选择放在一起，可以观察空间感受是否与实际选择相互呼应。不同街道的点位分布提供了直观比较。','不配得性Ⅰ：区位资源/行人选择':'点位区位和行人选择之间的关系，帮助判断位置优势是否转化为更多关注。悬停时可沿街查看同一道路的点位。','人群、行为与空间关联':'人群特征、行为表现和空间条件的关联表，适合用来寻找值得进一步观察的组合。相关系数只表示一起变化的程度。','不配得性Ⅰ：点位混合度与置信区间':'样本较多的点位才进入混合度和置信区间比较。误差线越短，说明这批样本的结果越稳定。','不配得性Ⅱ：街道人群构成':'街道和点位的人群构成呈现了年龄与身份倾向的差别。按排序查看，可以更快找到构成较特殊的位置。','不配得性Ⅱ：经济门槛与阶层排他':'不同功能类型的消费水平、消费空间和承载人数放在一起比较。三项指标的差异可以提示空间使用的门槛。','不配得性Ⅱ：在地记忆的悬置':'图中把人群偏好推演为原初功能，再与当前功能相连，用来观察记忆与现状之间的距离。它是分析性的假设关系。'}[title]
summary='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>分析总结｜衡复风貌区</title><link rel="stylesheet" href="studies.css"></head><body data-study="summary"><header><a href="../visualizations.html">←</a><h1>01 分析总结</h1><span class="meta">2026人因空间·135RECORDS</span></header><main id="workspace" class="summary-page"><section class="report"><p class="note">各图表的简要阅读提示，点击标题可返回对应图表。</p>'''+''.join(f'<article class="summary-item"><h2><a href="{route}">{i:02d} {title} ↗</a></h2><p>{summary_text(title)}</p></article>' for i,(_,route,title,_) in enumerate(CATALOG,1) if title!='分析总结')+'''</section></main></body></html>'''
summary_number=next(i for i,(_,route,_,_) in enumerate(CATALOG,1) if route=='analysis_summary.html')
summary=summary.replace('<h1>01 分析总结</h1>',f'<h1>{summary_number:02d} 分析总结</h1>')
(ROOT/'spacemovement/analysis_summary.html').write_text(summary,encoding='utf-8',newline='\n')
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
