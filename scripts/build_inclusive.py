"""Build the complete light-theme static website and its reproducible analyses."""
from pathlib import Path
import json,re,shutil,sys
from catalog import CATALOG
from build_data import ROOT
from build_inclusive_data import build as build_dataset
from sync_static import copy_static

def page(number,route,title,kind):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{title}｜Inclusive Vitality</title><link rel="stylesheet" href="../assets/css/inclusive.css"><script src="echarts.min.js"></script><script src="../assets/data/inclusive-data.js"></script></head><body data-page="{kind}" data-number="{number}"><header class="topbar"><a class="back" href="../visualizations.html" aria-label="返回宏观行为分析目录">←</a><h1>{number:02d} {title}</h1><span class="meta"></span></header><nav class="tabs" role="tablist" aria-label="切换图表"></nav><p class="readme"></p><main class="workspace"></main><script src="../assets/js/inclusive.js"></script></body></html>'''

def build(refresh=True):
    data=build_dataset() if refresh else json.loads((ROOT/'aerial/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    (ROOT/'aerial/assets/css/legacy-light.css').write_text('html{filter:invert(1) grayscale(1);background:#000;color-scheme:dark}body{min-height:100vh}iframe,embed,object{filter:grayscale(1)}',encoding='utf-8')
    active={r for _,r,_,_ in CATALOG}
    for number,route,title,kind in CATALOG:
        # Each editable snapshot is independent; subsequent builds preserve manual edits.
        import runpy
        editor=ROOT/'chart_python/current'/f'{number:02d}_{Path(route).stem}.py'
        if not editor.exists():
            js=(ROOT/'aerial/assets/js/inclusive.js').read_text(encoding='utf-8')
            editor.write_text('"""'+title+'：修改 JAVASCRIPT 后运行，即更新网站和发布包。"""\n'
               +'JAVASCRIPT = r\'\'\''+js+'\'\'\'\n\n'
               +"if __name__=='__main__':\n    from _export import export_chart\n    export_chart()\n",encoding='utf-8')
        js=runpy.run_path(str(editor))['JAVASCRIPT']
        script_name=f'chart-{number:02d}.js'
        (ROOT/'aerial/assets/js'/script_name).write_text(js,encoding='utf-8')
        html=page(number,route,title,kind).replace('src="../assets/js/inclusive.js"',f'src="../assets/js/{script_name}"')
        (ROOT/'spacemovement'/route).write_text(html,encoding='utf-8')
    for path in (ROOT/'spacemovement').glob('*.html'):
        if path.name=='空间活力度分析报告(1).html':continue
        text=path.read_text(encoding='utf-8')
        if path.name not in active and 'data-page=' in text:
            text=text.replace('<link rel="stylesheet" href="../assets/css/legacy-light.css">','')
            path.write_text(text,encoding='utf-8')
        elif path.name not in active and 'legacy-light.css' not in text:
            text=text.replace('</head>','<link rel="stylesheet" href="../assets/css/legacy-light.css"></head>')
            path.write_text(text,encoding='utf-8')
    cards=''.join(f'<a class="panel" href="spacemovement/{route}" aria-label="{i:02d} {title}"><span class="panel-spine">{i:02d} / {title}</span><div class="panel-detail"><span class="panel-number">{i:02d}</span><h2>{title}</h2><span class="panel-link">OPEN VISUALIZATION ⟶</span></div></a>' for i,route,title,_ in CATALOG)
    (ROOT/'aerial/visualizations.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>宏观行为分析｜Inclusive Vitality</title><link rel="stylesheet" href="assets/css/visualizations.css"></head><body><header class="topbar"><a class="brand" href="index.html">← INCLUSIVE VITALITY</a><h1>MACRO BEHAVIOR / '+str(len(CATALOG)).zfill(2)+' STUDIES</h1></header><main class="accordion">'+cards+'</main></body></html>',encoding='utf-8')
    (ROOT/'aerial/data-collection.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>数据采集｜Inclusive Vitality</title><link rel="stylesheet" href="assets/css/inclusive.css"><script src="assets/data/inclusive-data.js"></script></head><body><header class="topbar"><a class="back" href="index.html" aria-label="返回首页">←</a><h1>数据采集</h1><span class="meta">INCLUSIVE VITALITY / DATA COLLECTION</span></header><main class="collection"><nav class="sidebar" role="tablist" aria-label="数据目录"><button>目录索引</button><button>街道节点总表</button><button>行人信息总表</button></nav><section class="document-view" aria-label="文件内容"></section></main><script src="assets/js/collection.js"></script></body></html>''',encoding='utf-8')
    (ROOT/'aerial/behavior-analysis.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>微观行为分析｜Inclusive Vitality</title><link rel="stylesheet" href="assets/css/inclusive.css"></head><body><header class="topbar"><a class="back" href="index.html" aria-label="返回首页">←</a><h1>微观行为分析</h1></header><main class="frame-page"><h1>微观行为分析</h1><p>内容正在规划中</p></main></body></html>''',encoding='utf-8')
    for path in (ROOT/'spacemovement').iterdir():
        if path.suffix in ['.js','.css','.html'] and path.name!='空间活力度分析报告(1).html':
            shutil.copy2(path,ROOT/'aerial/spacemovement'/path.name)
    for path in (ROOT/'aerial/spacemovement').glob('*.html'):
        if path.name in active:continue
        text=path.read_text(encoding='utf-8')
        if 'legacy-light.css' not in text and 'data-page=' not in text:path.write_text(text.replace('</head>','<link rel="stylesheet" href="../assets/css/legacy-light.css"></head>'),encoding='utf-8')
    shutil.copytree(ROOT/'aerial',ROOT/'dist',dirs_exist_ok=True,copy_function=copy_static)
    from prepare_pages import prepare
    prepare()
    print(f'Inclusive Vitality: {len(CATALOG)} study pages, collection viewer and data_extract.csv updated.')

if __name__=='__main__':build()
