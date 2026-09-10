"""Build the micro analysis page and extend existing correlation explanations."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCALE = '空间面积扩大并不等同于停留人数同比例增长，大尺度开放空间容易出现空间闲置，紧凑适度的空间尺度更利于形成高密度停留。\n三个因素中以有效停留空间面积负相关最显著，节点空间长度其次，界面退让距离影响稍弱。'
EXPLANATIONS = {
    'typeB3c:resident': '人行道围栏对人群流向有一定的引导作用。',
    'facility:density': '道路附属设施的增加一定程度上降低停留密度。',
    'K:density': SCALE, 'L:density': SCALE, 'M:density': SCALE,
    'S:density': '紧凑适度的空间尺度更利于形成高密度停留。',
    'typeB3b:visitor': '一定数量的外摆构件能有效吸引游客到访。',
    'R:identityMix': '消费型停留空间占比越高，到访人群的身份倾向混合度越高，居民到访意愿较强。',
}

def renderer(js):
    marker = " const tooltip=el('aside','correlation-explanation',wrap);"
    addition = ' Object.assign(texts,' + json.dumps(EXPLANATIONS, ensure_ascii=False) + ');\n'
    if addition not in js and marker in js:
        js = js.replace(marker, addition + marker)
    return js

CSS = '''body.micro-page{min-height:100vh;height:auto;overflow:auto}.micro-page [hidden]{display:none!important}.micro-page .micro-content{padding:10px 3vw 48px}.micro-page .principle{padding:16px 0 24px;border-bottom:1px solid var(--line,#ccc)}.micro-page h2{font-size:24px;margin:12px 0 20px}.micro-page p{font-size:16px;line-height:1.95;white-space:pre-line;overflow-wrap:anywhere}.micro-page .case-meta{color:var(--muted,#555);line-height:1.8;margin-bottom:24px}.micro-page .case-tabs{padding:0 0 20px;display:flex;gap:10px;flex-wrap:wrap}.micro-page figure{margin:32px 0;width:100%}.micro-page figure img{display:block;width:100%;height:auto}.micro-page figcaption{font-size:14px;margin-bottom:10px;color:var(--muted,#555)}.micro-page button:focus-visible{outline:2px solid #292929;outline-offset:3px}@media(max-width:650px){.micro-page .micro-content{padding:6px 16px 32px}.micro-page p{font-size:15px}.micro-page .case-tabs{gap:6px}.micro-page .case-tabs button{font-size:13px;padding:8px}}
'''
JS = '''document.querySelectorAll('[role="tablist"]').forEach(list=>{
 const tabs=Array.from(list.querySelectorAll('[role="tab"]'));
 const select=tab=>tabs.forEach(button=>{const active=button===tab;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;document.getElementById(button.getAttribute('aria-controls')).hidden=!active;});
 tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>select(tab));tab.addEventListener('keydown',event=>{let index;if(event.key==='ArrowRight')index=(i+1)%tabs.length;else if(event.key==='ArrowLeft')index=(i+tabs.length-1)%tabs.length;else if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else return;event.preventDefault();select(tabs[index]);tabs[index].focus();});});
 select(tabs[0]);
});
'''

def tab(key, label, active=False):
    return f'<button type="button" role="tab" id="tab-{key}" aria-controls="{key}" aria-selected="{str(active).lower()}" tabindex="{0 if active else -1}">{escape(label)}</button>'

def panel(key, content, active=False):
    return f'<section id="{key}" role="tabpanel" aria-labelledby="tab-{key}"{ "" if active else " hidden"}>{content}</section>'

def pages():
    data=json.loads((ROOT/'scripts/micro_content.json').read_text(encoding='utf-8'))
    site=ROOT/'aerial'
    principles=''.join(f'<article class="principle"><h2>{escape(title)}</h2><p>{escape(text)}</p></article>' for title,text in data['principles'])
    cases='<nav class="case-tabs" role="tablist" aria-label="案例点位">'+''.join(tab(f'case-{i}',c['name'],i==0) for i,c in enumerate(data['cases']))+'</nav>'
    names=['姿态图.png','平面轨迹.png','平面散点.png','社交强度.png','骨骼.png','视线朝向.png']
    for i,c in enumerate(data['cases']):
        content=f'<h2>{escape(c["name"])}</h2><p class="case-meta">地址：{escape(c["address"])}\n节点功能类别：{escape(c["category"])}\n界面分类信息：\nA：A2\nB：{escape(c["B"])}\nC：{c["C"]}\nD：{c["D"]}</p><p>{escape(c["description"])}</p>'
        for name in names:
            source=ROOT/'result/骨骼组总图'/c['folder']/name
            if not source.exists():
                source=source.with_name('骨骼.jpg' if name=='骨骼.png' else '视觉朝向.png')
            target=site/'assets/data/micro'/c['folder']/source.name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
            with Image.open(source) as image:
                width,height=image.size
            url=quote(target.relative_to(site).as_posix())
            content+=f'<figure><figcaption>{escape(name[:-4])}</figcaption><img src="{url}" alt="{escape(c["name"])} · {escape(name[:-4])}" width="{width}" height="{height}" loading="lazy" decoding="async"></figure>'
        cases+=panel(f'case-{i}',content,i==0)
    html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>微观数据分析｜Inclusive Vitality</title>'
    html+=''.join(f'<link rel="stylesheet" href="assets/css/{name}.css">' for name in ['inclusive','interface','final-revision','palette-revision','micro'])
    html+='</head><body class="micro-page"><header class="topbar unified-topbar"><a class="brand" href="index.html" aria-label="返回首页">← INCLUSIVE VITALITY</a><h1>微观数据分析</h1></header><nav class="tabs" role="tablist" aria-label="微观分析">'+tab('principles','可视化原理',True)+tab('cases','案例剖析')+'</nav><main class="micro-content">'+panel('principles',principles,True)+panel('cases',cases)+'</main><script src="assets/js/micro.js"></script></body></html>'
    (site/'behavior-analysis.html').write_text(html,encoding='utf-8')
    (site/'assets/css/micro.css').write_text(CSS,encoding='utf-8')
    (site/'assets/js/micro.js').write_text(JS,encoding='utf-8')
    path=site/'index.html'
    path.write_text(path.read_text(encoding='utf-8').replace('微观行为分析','微观数据分析'),encoding='utf-8')
    path=site/'assets/js/chart-06.js'
    path.write_text(renderer(path.read_text(encoding='utf-8')),encoding='utf-8')

if __name__=='__main__':
    pages()
    for folder in ['dist','docs']:
        target=ROOT/folder
        for name in ['behavior-analysis.html','assets/css/micro.css','assets/js/micro.js','assets/js/chart-06.js']:
            shutil.copy2(ROOT/'aerial'/name,target/name)
        index=target/'index.html'
        index.write_text(index.read_text(encoding='utf-8').replace('微观行为分析','微观数据分析'),encoding='utf-8')
        shutil.copytree(ROOT/'aerial/assets/data/micro',target/'assets/data/micro',dirs_exist_ok=True)
    print('Updated micro analysis, 36 images, and eight correlation explanations.')
