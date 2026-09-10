"""September 10: authoritative source frequencies, explicit weights and UI migration."""
import csv,json,math,re,shutil
from build_data import ROOT,read_source
from scipy.stats import spearmanr

def revise(data):
    _,rows=read_source(data['spaceSheet'])
    raw={int(r['A']):r for r in rows[3:] if isinstance(r.get('A'),(int,float)) and r.get('B')}
    finite=lambda v:isinstance(v,(int,float)) and math.isfinite(v)
    dimensions=[('ageMix','年龄混合度',['AM','AN','AO','AP']),('activityMix','活动丰富度',['AV','AW','AX','AY','AZ','BA','BB','BC','BD','BE','BF','BG','BH','BI']),('socialMix','社交状态混合度',['AK','AL']),('postureMix','姿态丰富度',['AT','AU']),('identityMix','身份倾向混合度',['BS','BT'])]
    data['mixDimensions']=[{'key':k,'label':label,'columns':cols,'labels':[rows[2][c] for c in cols]} for k,label,cols in dimensions]
    quality=[('M','有效停留面积',.068),('S','可承载停留人数',.078),('R','消费型停留空间占比',.167),('AE','遮荫率',.112),('AF','声环境舒适度',.069),('AG','气味环境',.058),('Y','视觉丰富度',.095),('Z','历史感知度',.099),('AA','路面状态',.077),('U','界面开放度',.094),('V','临界互动性',.084)]
    vitality=[('sample','人数',.194),('clusters','行人集群数',.144),('density','停留密度',.205),('gather','聚集比例',.456)]
    data['ys'].update(clusters='行人集群数',gather='聚集比例')
    data['scoreWeights']={'quality':quality,'vitality':vitality,'mix':[('ageMix','年龄混合度',.149),('activityMix','活动丰富度',.141),('identityMix','身份倾向混合度',.250),('postureMix','姿态丰富度',.228),('socialMix','社交状态混合度',.233)]}
    for p in data['points']:
        r=raw[int(p['values']['A'])];p['mixCounts']={}
        for key,label,cols in dimensions:
            counts=[r.get(c) for c in cols];p['mixCounts'][key]=counts
            h=None
            if all(finite(v) and v>=0 for v in counts) and sum(counts)>0:
                total=sum(counts);h=-sum(v/total*math.log(v/total) for v in counts if v)/math.log(len(cols))
            p['metrics'][key]=h
        p['mix']=[p['metrics'][k] for k in ['ageMix','activityMix','identityMix','postureMix','socialMix']]
        p['mixScore']=sum(p['metrics'][k]*w for k,_,w in data['scoreWeights']['mix']) if all(finite(v) for v in p['mix']) else None
    for kind,defs in [('quality',quality),('vitality',vitality)]:
        source='values' if kind=='quality' else 'metrics';bounds={}
        for k,label,w in defs:
            a=[p[source].get(k) for p in data['points'] if finite(p[source].get(k))];bounds[k]=[min(a),max(a)] if a else [None,None]
            if kind=='quality':data['headers'][k]=label
        for p in data['points']:
            z={}
            for k,_,w in defs:
                v=p[source].get(k);lo,hi=bounds[k];z[k]=(v-lo)/(hi-lo) if finite(v) and hi>lo else 0 if finite(v) else None
            p[kind+'Normalized']=z;p[kind]=sum(z[k]*w for k,_,w in defs) if all(finite(v) for v in z.values()) else None
        data[kind+'Bounds']=bounds
    data['qualityFields']=[k for k,_,_ in quality];data['vitalityCoefficient']=1
    data['qualityRule']='指定11项指标全域最小最大标准化后按给定权重求和'
    for c in data['correlations']:
        a=[(p['values'].get(c['x']),p['metrics'].get(c['y'])) for p in data['points']];a=[(x,y) for x,y in a if finite(x) and finite(y)]
        c.update(n=len(a),rho=None,p=None)
        if len(a)>=3 and len({x for x,y in a})>1 and len({y for x,y in a})>1:
            stat=spearmanr(*zip(*a));c.update(rho=float(stat.statistic),p=float(stat.pvalue))
    from shap_revision import load_scores
    load_scores(data)
    data['scoreMeans']={k:s['mean'] for k,s in data['scoreSources'].items()}
    extracted=[]
    for p in data['points']:
        p['mismatchGroups']={}
        for kind,x,y,xlabel,ylabel in [('qualityVitality','quality','vitality','界面品质','活力度'),('qualityMix','quality','mixScore','界面品质','混合度'),('mismatch','vitality','mixScore','活力度','混合度')]:
            a,b=p[x],p[y];group=None
            if finite(a) and finite(b):
                mx,my=data['scoreMeans'][x],data['scoreMeans'][y]
                group='高'+ylabel+'低'+xlabel if a<mx and b>=my else '高'+xlabel+'低'+ylabel if a>=mx and b<my else None
            p['mismatchGroups'][kind]=group
            if group:extracted.append([p['id'],p['address'],kind,group,p['quality'],p['vitality'],p['mixScore'],p['metrics']['sample'],xlabel,ylabel,a,b,data['scoreMeans'][x],data['scoreMeans'][y],'左上' if a<data['scoreMeans'][x] else '右下'])
        p['quadrant']=p['mismatchGroups']['mismatch'];p['mismatch']=math.log((1+p['vitality'])/(1+p['mixScore'])) if finite(p['vitality']) and finite(p['mixScore']) else None
    for filename in ['data-extract.csv','data_extract.csv']:
        with (ROOT/filename).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['point_id','完整地址','分析','组别','界面品质Q','活力度V','混合度M','行人样本数','横轴指标','纵轴指标','横轴值','纵轴值','横轴全域有效评分均值','纵轴全域有效评分均值','象限']);w.writerows(extracted)
    with (ROOT/'result/score-fields.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f)
        w.writerow(['point_id','完整地址','CSV数据行','界面品质','活力度','混合度','界面品质均值','活力度均值','混合度均值','不配得性Ⅰ组别','不配得性Ⅱ组别','不配得性Ⅲ组别'])
        for p in data['points']:
            w.writerow([p['id'],p['address'],p['scoreSourceRows']['vitality'],p['quality'],p['vitality'],p['mixScore'],data['scoreMeans']['quality'],data['scoreMeans']['vitality'],data['scoreMeans']['mixScore'],p['mismatchGroups']['qualityVitality'],p['mismatchGroups']['qualityMix'],p['mismatchGroups']['mismatch']])
    (ROOT/'.site-build/final-audit.json').write_text(json.dumps({'source':data['spaceSheet'],'fields':data['mixDimensions'],'weights':data['scoreWeights'],'points':len(data['points']),'missing':{k:sum(p[k] is None for p in data['points']) for k in ['quality','vitality','mixScore']},'extracted':len(extracted)},ensure_ascii=False,indent=2),encoding='utf-8')

def renderer(js):
    js=re.sub(r'const SFORM=.*?;\nconst MFORM=.*?;\n',"const SFORM='各底层指标 z=(x−全域最小值)/(全域最大值−全域最小值)，常量记0；缺失则综合评分缺失。综合评分=Σ(w×z)，采用系数表征的指定权重，不额外缩放。';\nconst MFORM='H_d=−Σ(p_k×ln p_k)/ln K_d；p_k=类别频数/该维频数合计，0×ln0记0。零合计或缺失不评分。M=0.149H年龄+0.141H活动+0.250H身份倾向+0.228H姿态+0.233H社交状态。权重按给定公式顺序使用，不二次归一化。';\n",js,flags=re.S)
    js=js.replace("['sample','clusters','density','gather','resident','visitor']","['sample','clusters','density','gather']")
    js=js.replace('(quality?p.values:p.metrics)[k]',"(quality?p.qualityNormalized:kind==='vitality'?p.vitalityNormalized:p.metrics)[k]")
    js=js.replace("界面品质：沿用不配得性Ⅰ的正向显著指标，各指标全域最小最大标准化后等权平均。","界面品质：11项指标按全域最小最大值标准化后，依系数表征权重求和。")
    js=js.replace("scatter(grid,'T',y,t)","scatter(grid,'AH',y,t)")
    js=js.replace("mode?'#292929':'#A45668'","mode?'#292929':(['#607E95','#A45668','#8C793E','#497F73','#806A96','#BD7546'][['AU','AV','AX','BA','AY','BB'].indexOf(selected)]||'#607E95')")
    start=js.index("if(PAGE==='heat')");end=js.index('let resizeTimer',start)
    js=js[:start]+(ROOT/'aerial/assets/js/final-revision.js').read_text(encoding='utf-8')+'\n'+js[end:]
    from palette_revision import renderer as palette_renderer
    js=palette_renderer(js)
    from presentation_revision import renderer as presentation_renderer
    js=presentation_renderer(js)
    return js

from regression_revision import TITLES
def pages():
    from catalog import CATALOG
    cards=[]
    for _,route,_,kind in sorted(CATALOG,key=lambda r:TITLES[r[3]][0]):
        n,title=TITLES[kind]
        cards.append(f'<a class="panel {"regression" if n in [4,5] else ""}" href="spacemovement/{route}" aria-label="{n:02} {title}"><span class="panel-spine">{n:02} / {title}</span><div class="panel-detail"><span class="panel-number">{n:02}</span><h2>{title}</h2><span class="panel-link">OPEN VISUALIZATION ⟶</span></div></a>')
        for folder in ['spacemovement','aerial/spacemovement']:
            p=ROOT/folder/route;s=p.read_text(encoding='utf-8');s=re.sub(r'<h1>.*?</h1>',f'<h1>{n:02} {title}</h1>',s);s=re.sub(r'<title>.*?</title>',f'<title>{title}｜Inclusive Vitality</title>',s)
            s=s.replace('</head>','<link rel="stylesheet" href="../assets/css/final-revision.css"></head>');p.write_text(s,encoding='utf-8')
    p=ROOT/'aerial/visualizations.html';s=p.read_text(encoding='utf-8');s=re.sub(r'<main class="accordion">.*?</main>','<main class="macro-stage"><div class="accordion">'+''.join(cards[:5])+'<button class="panel mismatch-entry" aria-expanded="false" aria-controls="mismatch-menu"><span class="panel-spine">06–08 / 不配得性分析</span><div class="panel-detail"><span class="panel-number">06–08</span><h2>不配得性分析</h2><span class="panel-link">展开分析 ⟶</span></div></button></div><section id="mismatch-menu" class="mismatch-menu" inert><button class="menu-back">← 返回全部分析</button>'+''.join(cards[5:])+'</section></main>',s)
    s=s.replace('</head>','<link rel="stylesheet" href="assets/css/final-revision.css"></head>').replace('</body>','<script>const stage=document.querySelector(".macro-stage"),entry=document.querySelector(".mismatch-entry"),menu=document.querySelector(".mismatch-menu");function toggle(open){stage.classList.toggle("expanded",open);entry.setAttribute("aria-expanded",open);menu.inert=!open;document.querySelectorAll(".accordion>a").forEach(a=>a.inert=open);if(open)setTimeout(()=>menu.querySelector("button").focus(),550);else entry.focus()}entry.onclick=()=>toggle(entry.getAttribute("aria-expanded")!=="true");document.querySelector(".menu-back").onclick=()=>toggle(false);document.addEventListener("keydown",e=>{if(e.key==="Escape")toggle(false)});</script></body>');p.write_text(s,encoding='utf-8')
    p=ROOT/'aerial/index.html';s=p.read_text(encoding='utf-8').replace('调研网页','总览')
    if 'team.html' not in s:s=s.replace('</ul>','<li><a href="team.html" class="portal"><span class="number">06</span><span>课程与团队信息</span></a></li></ul>',1)
    if 'final-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/css/final-revision.css"></head>')
    p.write_text(s,encoding='utf-8')
    (ROOT/'aerial/team.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>课程与团队信息</title><link rel="stylesheet" href="assets/css/inclusive.css"><link rel="stylesheet" href="assets/css/interface.css"></head><body><header class="topbar unified-topbar"><a class="brand" href="index.html">← INCLUSIVE VITALITY</a><h1>课程与团队信息</h1></header><main style="max-width:1000px;margin:8vh auto;padding:32px;line-height:2.4"><h2>指导老师：闫超</h2><p>孙靖琪、王霏杨、常思语、丁文颖、王一一、黄子童、苏嘉欣、黄希龄、徐韵晨、王倪潇、李严宇、蔡淙旭</p></main></body></html>',encoding='utf-8')
    dest=ROOT/'aerial/assets/data/coefficients';dest.mkdir(exist_ok=True)
    for name in ['M','Q','V']:shutil.copy2(ROOT/f'result/权重/{name}.png',dest/f'{name}.png')
    from palette_revision import pages as palette_pages
    palette_pages()
    from shap_revision import pages as shap_pages
    shap_pages()
