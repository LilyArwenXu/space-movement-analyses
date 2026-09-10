"""Separate population/regression navigation and refresh the SHAP presentation."""
from pathlib import Path
import hashlib
import json
import re
import shutil
from html import escape
from catalog import CATALOG

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    'heat':(1,'人员热力图'), 'composition':(2,'人群构成分析'),
    'correlations':(3,'空间行为相关性分析'), 'mixRegression':(4,'混合度回归分析'),
    'weights':(5,'界面品质回归分析'), 'memory':(6,'空间活力度回归分析'),
    'qualityVitality':(7,'不配得性Ⅰ：高界面品质是否必然带来高空间活力度？'),
    'qualityMix':(8,'不配得性Ⅱ：高界面品质是否必然促进人群的高度混合？'),
    'mismatch':(9,'不配得性Ⅲ：混合度与活力度有何关联特征？'),
}
SHAP_RENDERER = r'''function shapAnalysis(label){
 const content=window.SHAP_CAPTIONS;
 el('h2','section-heading').textContent=label;
 const gallery=el('section','shap-gallery');
 const lines=s=>s.replace(/([；;。])\s*/g,'$1\n').trim();
 [1,2,3].forEach((number,index)=>{
  const figure=el('figure','shap-figure',gallery),row=el('div','shap-row',figure),img=el('img','shap-image',row);
  img.src='../assets/data/shap/'+label+'/'+number+'.png?v='+content.assetVersion;img.alt=label+' · '+number+'.png';
  const side=el('aside','shap-side',row);
  el('p','shap-description',side).textContent=lines(content.descriptionOverrides?.[label]?.[index]||content.descriptions[index]);
  el('p','shap-conclusion',side).textContent=lines(content.groups[label][index]);
 });
 note('');
}
'''
CSS = '''.macro-stage.expanded .mismatch-entry{transform:translateX(-200%)}
.mismatch-menu{left:33.333333%}
.critic-method>summary{cursor:pointer;font-size:23px;line-height:1.6;font-weight:400;list-style-position:inside}
.critic-method>summary:focus-visible{outline:2px solid #111;outline-offset:4px}
.critic-method[open]>summary{margin-bottom:24px}.critic-method:not([open]){padding:16px 0}
.shap-side{max-height:none;overflow:visible;padding-right:0}
.shap-side .shap-description{margin:0;white-space:pre-line;font:inherit}
.shap-side .shap-conclusion{margin:26px 0 0;padding-top:18px;border-top:1px solid #ddd;white-space:pre-line;font:inherit}
'''

def renderer(js):
    if 'function shapAnalysis(label){' not in js:
        return js
    js=re.sub(r"if\(PAGE==='composition'\)mainTabs\(\['构成分析','系数表征','混合度总表'\].*?;\n", "if(PAGE==='composition')mainTabs(D.mixDimensions.map(d=>d.label),dimensionBars);\n",js)
    if "if(PAGE==='mixRegression')" not in js:
        js=js.replace("if(PAGE==='composition')", "if(PAGE==='mixRegression')mainTabs(['系数表征','混合度总表'],i=>i?mixedTotal():coefficient('mix'));\nif(PAGE==='composition')")
    js=js.replace("el('section','critic-method',box)","el('details','critic-method',box)")
    js=js.replace("el('section','critic-method',NOTE)","el('details','critic-method',NOTE)")
    js=js.replace('<h2>Critic权重算法</h2>','<summary>Critic权重算法</summary>')
    start=js.index('function shapAnalysis(label){')
    end=js.index('function mismatchView(i){',start)
    js=js[:start]+SHAP_RENDERER+js[end:]
    start=js.index('function mismatchView(i){')
    if "if(i){if(PAGE==='mismatch')" in js[start:]:
        js=js[:start]+re.sub(r" if\(i\)\{.*?return;\}\n const c=chart\(W,610\)"," if(i){sectionTabs(labels,j=>shapAnalysis(labels[j]));return;}\n const c=chart(W,610)",js[start:],count=1,flags=re.S)
    return js

def card(route,kind):
    number,title=TITLES[kind]
    group=' regression' if kind in ['mixRegression','weights','memory'] else ''
    return f'<a class="panel{group}" href="spacemovement/{route}" aria-label="{number:02d} {escape(title)}"><span class="panel-spine">{number:02d} / {escape(title)}</span><div class="panel-detail"><span class="panel-number">{number:02d}</span><h2>{escape(title)}</h2><span class="panel-link">OPEN VISUALIZATION ⟶</span></div></a>'

def pages():
    site=ROOT/'aerial'
    inputs=json.loads((ROOT/'scripts/mismatch_captions.json').read_text(encoding='utf-8'))
    marker='/* Updated mismatch III captions */'
    caption=site/'assets/data/shap-captions.js'
    base=caption.read_text(encoding='utf-8').split(marker)[0]
    desc=inputs['descriptions']
    overrides={'高混合度低活力度':[desc['summary'],desc['interaction'],desc['summary']], '高活力度低混合度':[desc['summary'],desc['interaction'],desc['trend']]}
    files=sorted((ROOT/'result/shap').glob('*/*.png'))
    version=hashlib.sha256(b''.join(hashlib.sha256(f.read_bytes()).digest() for f in files)).hexdigest()[:12]
    base+='\n'+marker+'\nObject.assign(window.SHAP_CAPTIONS.groups,'+json.dumps(inputs['groups'],ensure_ascii=False)+');\nwindow.SHAP_CAPTIONS.descriptionOverrides='+json.dumps(overrides,ensure_ascii=False)+';\nwindow.SHAP_CAPTIONS.assetVersion='+json.dumps(version)+';\n'
    caption.write_text(base,encoding='utf-8')
    shutil.copytree(ROOT/'result/shap',site/'assets/data/shap',dirs_exist_ok=True)
    # All chart snapshots share the same functions and branch on data-page.
    for file in (site/'assets/js').glob('chart-*.js'):
        file.write_text(renderer(file.read_text(encoding='utf-8')),encoding='utf-8')
    shutil.copy2(site/'assets/js/chart-03.js',site/'assets/js/chart-10.js')
    template=(site/'spacemovement/people_composition.html').read_text(encoding='utf-8')
    (site/'spacemovement/mixing_regression.html').write_text(template.replace('data-page="composition"','data-page="mixRegression"').replace('chart-03.js','chart-10.js'),encoding='utf-8')
    (site/'assets/css/regression-revision.css').write_text(CSS,encoding='utf-8')
    for _,route,_,kind in CATALOG:
        path=site/'spacemovement'/route;s=path.read_text(encoding='utf-8');number,title=TITLES[kind]
        s=re.sub(r'<title>.*?</title>',f'<title>{escape(title)}｜Inclusive Vitality</title>',s)
        s=re.sub(r'<h1>.*?</h1>',f'<h1>{number:02d} {escape(title)}</h1>',s)
        if 'regression-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="../assets/css/regression-revision.css"></head>')
        path.write_text(s,encoding='utf-8')
        shutil.copy2(path,ROOT/'spacemovement'/route)
    path=site/'visualizations.html';s=path.read_text(encoding='utf-8')
    ordered=sorted(CATALOG,key=lambda entry:TITLES[entry[3]][0]);cards=[card(route,kind) for _,route,_,kind in ordered]
    main='<main class="macro-stage"><div class="accordion">'+''.join(cards[:6])+'<button class="panel mismatch-entry" aria-expanded="false" aria-controls="mismatch-menu"><span class="panel-spine">07–09 / 不配得性分析</span><div class="panel-detail"><span class="panel-number">07–09</span><h2>不配得性分析</h2><span class="panel-link">展开分析 ⟶</span></div></button></div><section id="mismatch-menu" class="mismatch-menu" inert><button class="menu-back">← 返回全部分析</button>'+''.join(cards[6:])+'</section></main>'
    s=re.sub(r'<main\b.*?</main>',lambda _:main,s,flags=re.S).replace('08 STUDIES','09 STUDIES')
    if 'regression-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/css/regression-revision.css"></head>')
    path.write_text(s,encoding='utf-8')
    for name in ['data-extract.csv','data_extract.csv']:
        shutil.copy2(ROOT/name,site/'assets/data'/name)

def refresh():
    from final_revision import revise
    path=ROOT/'aerial/assets/data/inclusive-data.js'
    data=json.loads(path.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    revise(data)
    path.write_text('window.INCLUSIVE='+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8')
    pages()
    from sync_static import copy_static
    shutil.copytree(ROOT/'aerial',ROOT/'dist',dirs_exist_ok=True,copy_function=copy_static)
    from prepare_pages import prepare
    prepare()
    print(json.dumps({'scoreMeans':data['scoreMeans'],'groupCounts':{kind:{label:sum(p['mismatchGroups'][kind]==label for p in data['points']) for label in sorted({p['mismatchGroups'][kind] for p in data['points'] if p['mismatchGroups'][kind]})} for kind in ['qualityVitality','qualityMix','mismatch']}},ensure_ascii=False))

if __name__=='__main__':refresh()
