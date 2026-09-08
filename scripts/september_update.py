"""September 8 navigation, exact source tables, classification and case studies."""
import json, re, shutil, csv, math
from pathlib import Path
from build_data import ROOT, SOURCE, read_source

def enrich(data):
    import zipfile, xml.etree.ElementTree as ET
    from openpyxl.utils.cell import column_index_from_string, get_column_letter, range_boundaries
    from build_data import NS
    from scipy.stats import spearmanr
    for key,name,head in [('space',data['spaceSheet'],3),('people',data['peopleSheet'],1)]:
        _,raw=read_source(name)
        if key=='space':
            stop=next(column_index_from_string(k) for row in raw[:3] for k,v in row.items() if v=='进一步计算')
            cols=list(range(1,stop))
            cols=[c for c in cols if str(raw[2].get(get_column_letter(c),'')).strip()!='D附属设施加权指数']
        else:cols=[column_index_from_string(k) for k,v in raw[0].items() if v and str(v).strip() not in ['辅助计算1','辅助计算2','居民指数','游客指数']]
        rows=[[r.get(get_column_letter(c)) for c in cols] for r in raw]
        while rows and all(v is None for v in rows[-1]):rows.pop()
        merges=[]
        with zipfile.ZipFile(SOURCE) as z:
            sheet=next(s for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS) if s.attrib['name']==name)
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=next(r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if r.attrib['Id']==rid).lstrip('/')
            if not target.startswith('xl/'):target='xl/'+target
            for m in ET.fromstring(z.read(target)).findall('m:mergeCells/m:mergeCell',NS):
                c1,r1,c2,r2=range_boundaries(m.attrib['ref']);kept=[c for c in cols if c1<=c<=c2]
                if kept:merges.append([r1-1,cols.index(kept[0]),r2-r1+1,len(kept)])
        data['tables'][key]={'columns':[get_column_letter(c) for c in cols],'rows':rows,'merges':merges,'headerRows':head}
    _,means=read_source('点位均值')
    lookup={r.get('A'):(r.get('B'),r.get('C')) for r in means[1:]}
    for p in data['points']:
        p['metrics']['resident'],p['metrics']['visitor']=lookup.get(p['address'],(None,None))
    data['meanSheet']='点位均值'
    data['sourceWorkbook']=SOURCE.name
    # Recompute correlations after applying the explicitly supplied point means.
    for c in data['correlations']:
        pairs=[(p['values'].get(c['x']),p['metrics'].get(c['y'])) for p in data['points']]
        pairs=[(x,y) for x,y in pairs if isinstance(x,(float,int)) and isinstance(y,(float,int)) and math.isfinite(x) and math.isfinite(y)]
        c.update(n=len(pairs),rho=None,p=None)
        if len(pairs)>=3 and len({x for x,y in pairs})>1 and len({y for x,y in pairs})>1:
            result=spearmanr(*zip(*pairs));c.update(rho=float(result.statistic),p=float(result.pvalue))
    data['cases']={}
    groups={'qualityVitality':'不配得性Ⅰ','qualityMix':'不配得性Ⅱ','mismatch':'不配得性Ⅲ'}
    dims={'quality':[(k,data['headers'][k]) for k in data['qualityFields']], 'vitality':[(k,data['ys'][k]) for k in ['sample','clusters','density','gather','resident','visitor']], 'mix':[(k,data['ys'][k]) for k in ['ageMix','activityMix','identityMix','postureMix','socialMix']]}
    data['caseDimensions']=dims
    from case_analysis import analyze
    for kind,folder in groups.items():
        cases=[]
        for directory in sorted((ROOT/'examples'/folder).iterdir()):
            if not directory.is_dir():continue
            files=list(directory.glob('*.csv'));nodefile=next(f for f in files if '节点数据' in f.name);peoplefile=next(f for f in files if '行人数据' in f.name)
            with nodefile.open(encoding='utf-8-sig') as f:nodes=list(csv.DictReader(f))
            with peoplefile.open(encoding='utf-8-sig') as f:people=list(csv.DictReader(f))
            analysis=analyze(nodes,people,dims,kind)
            photos=[f for f in directory.iterdir() if f.suffix.lower() in ['.jpg','.jpeg','.png']]
            actions={k.replace('行为_',''):sum(float(r.get(k) or 0) for r in people) for k in people[0] if k.startswith('行为_')} if people else {}
            observed='、'.join(f'{k}{int(v)}人' for k,v in sorted(actions.items(),key=lambda kv:-kv[1])[:3] if v>0) or '无有效行为记录'
            cases.append({'address':directory.name,'id':nodes[0].get('点位ID'), 'analysis':analysis,'photos':['../examples/'+folder+'/'+directory.name+'/'+f.name for f in photos],
                'nodeRows':nodes,'peopleRows':people,'csv':['../examples/'+folder+'/'+directory.name+'/'+f.name for f in [nodefile,peoplefile]],
                'caption':f"{directory.name} · {nodes[0].get('功能类型','')}。案例记录：{observed}（行为可多选）。案例 CSV 共 {len(nodes)} 条节点记录、{len(people)} 条行人记录；以下统计仅使用这两个 CSV。"})
        data['cases'][kind]=cases

def renderer(js):
    # Preserve independently editable renderers, applying this migration at build time.
    js=js.replace('function reset(){',"function reset(){document.body.classList.remove('case-analysis');")
    js=js.replace("D.points.filter(p=>p.n).slice()","D.points.filter(p=>p.n>=4).slice()")
    for a,b in [('fontSize:8','fontSize:12'),('fontSize:10','fontSize:13'),('fontSize:11','fontSize:14'),('fontSize:12','fontSize:14')]:js=js.replace(a,b)
    js=js.replace('fontSize:compact?8:10','fontSize:compact?12:14')
    js=js.replace("textStyle:{color:INK,fontFamily:FONT},title", "textStyle:{color:INK,fontFamily:FONT,fontSize:15},title")
    js=js.replace("name:'所有点位（按总表顺序）'}:original.xAxis", "name:'所有点位（按总表顺序）',nameLocation:'middle',nameGap:34}:original.xAxis")
    js=js.replace("const mix=kind==='mix',keys=mix?", "const quality=kind==='quality',mix=kind==='mix',keys=quality?D.qualityFields:mix?")
    js=js.replace('keys.map(k=>D.ys[k])','keys.map(k=>quality?D.headers[k]:D.ys[k])')
    js=js.replace('D.points.map(p=>p.metrics[k])',"D.points.map(p=>(quality?p.values:p.metrics)[k])")
    js=js.replace("p[mix?'mixScore':'vitality']","p[quality?'quality':mix?'mixScore':'vitality']")
    js=js.replace('(mix?MFORM:SFORM)',"(quality?'界面品质：沿用不配得性Ⅰ的正向显著指标，各指标全域最小最大标准化后等权平均。':mix?MFORM:SFORM)")
    js=re.sub(r'PALETTE\[j\]', 'PALETTE[j%PALETTE.length]',js)
    js=js.replace('PALETTE[last]','PALETTE[last%PALETTE.length]')
    start=js.index("if(PAGE==='heat')")
    end=js.index('let resizeTimer',start)
    color=next(line.strip() for line in js.splitlines() if line.strip().startswith('function color(value)')).replace('function color(value)','function correlationColor(value)')
    js=js[:start]+color+'\n'+(ROOT/'aerial/assets/js/case-study.js').read_text(encoding='utf-8')+'\n'+(ROOT/'aerial/assets/js/september.js').read_text(encoding='utf-8')+'\n'+js[end:]
    from interface_update import update_renderer
    return update_renderer(js)

def pages():
    for folder in ['category-photos','examples']:shutil.copytree(ROOT/folder,ROOT/'aerial'/folder,dirs_exist_ok=True)
    home=ROOT/'aerial/index.html';s=home.read_text(encoding='utf-8')
    s=s.replace('<span class="portal unavailable" aria-disabled="true"><span class="number">03</span><span>类型划分</span></span>','<a class="portal" href="categories.html"><span class="number">03</span><span>类型划分</span></a>')
    home.write_text(s,encoding='utf-8')
    groups=[('A 空间功能','A1a 居住界面|A2a 商业界面|A3 公共界面|A4a 基础设施界面'),('B1 界面退让','B1a 无后退|B1b 区域后退|B1c 局部后退|B1d 整体后退'),('B2 可视度','B2a 仅墙面|B2b 橱窗|B2c 墙面开洞|B2d 完全开放'),('B3 构件延伸','B3a-i 椅子内侧|B3a-ii 椅子外侧|B3b-i 雨棚|B3b-ii 招牌|B3b-iii 大雨棚|B3cc 围栏'),('C 作用尺度','C1 构件尺度|C2 开间尺度|C3 建筑尺度|C4 组团尺度'),('D 街道环境','D1 公共座椅|D2 行道树|D3 花坛|D4 电线杆|D5 路灯|D6 共享单车|D7 垃圾桶|D8 配电箱')]
    photos=list((ROOT/'category-photos').glob('*.png'));rows=''
    for title,entries in groups:
        for i,entry in enumerate(entries.split('|')):
            code,label=entry.split(' ',1);photo=next((p for p in photos if p.stem==code or p.stem.endswith('_'+code)),None)
            content=f'<img loading="lazy" src="category-photos/{photo.name}" alt="{entry}">' if photo else '<p>该分类未提供图片</p>'
            rows+='<tr>'+ (f'<th rowspan="{len(entries.split("|"))}">{title}</th>' if i==0 else '')+f'<td class="category-cell"><details><summary>{code}</summary><div class="category-image">{content}</div></details></td><td>{label}</td></tr>'
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>类型划分</title><link rel="stylesheet" href="assets/css/inclusive.css"><header class="topbar"><a href="index.html">←</a><h1>类型划分</h1></header><main class="category-layout"><details><summary>街道空间要素分类表 · 原始 SVG 总览</summary><img class="category-overview" src="category-photos/街道空间要素分类表_最新.svg" alt="街道空间要素分类表原始总览"></details><p>悬停分类编号查看图片，点击可固定展开。</p><table class="category-table">'''+rows+'''</table></main><script>document.querySelectorAll('.category-cell details').forEach(d=>{let pinned=false;d.querySelector('summary').onclick=e=>{e.preventDefault();pinned=!pinned;d.open=pinned};d.addEventListener('pointerenter',()=>d.open=true);d.addEventListener('pointerleave',()=>d.open=pinned);d.addEventListener('focusin',()=>d.open=true);});</script></html>'''
    # SVG lettering is outlined paths. Place keyboard-accessible targets over the
    # original cells; the drawing itself is preserved byte-for-byte.
    spots=[]
    codes=['A1a','A2a','A3','A4a','B1a','B1b','B1c','B1d','B2a','B2b','B2c','B2d','B3a-i','B3a-ii','B3b-i','B3b-ii','B3b-iii','B3cc','C1','C2','C3','C4','D1','D2','D3','D4','D5','D6','D7','D8']
    for i,code in enumerate(codes):
        photo=next((p for p in photos if p.stem==code or p.stem.endswith('_'+code)),None)
        x,w=(20.4,8.5) if i<4 or i>=18 else (67,10.5) if 12<=i<=16 else (44.8,9)
        content=f'<img src="category-photos/{photo.name}" alt="{code}" loading="lazy">' if photo else '<p>该分类未提供 PNG</p>'
        spots.append(f'<div class="svg-hotspot" tabindex="0" aria-label="{code} 分类图片" style="left:{x}%;top:{(173+i*35.5)/1419*100}%;width:{w}%;height:2.5%"><span class="hotspot-label">{code}</span><div class="hotspot-preview">{content}</div></div>')
    overview='<section class="svg-overview"><img src="category-photos/街道空间要素分类表_最新.svg" alt="街道空间要素分类表原始总览">'+''.join(spots)+'</section>'
    html=html.replace('<main class="category-layout">','<main class="category-layout">'+overview)
    html=html.replace('<table class="category-table">','<h2>分类图片索引</h2><table class="category-table">')
    from interface_update import category_page
    (ROOT/'aerial/categories.html').write_text(category_page(),encoding='utf-8')
    p=ROOT/'aerial/data-collection.html';p.write_text(p.read_text(encoding='utf-8').replace('街道节点总表','街道信息总表').replace('js/collection.js','js/collection-september.js'),encoding='utf-8')
    for path in [ROOT/'aerial/index.html',ROOT/'aerial/visualizations.html']:
        s=path.read_text(encoding='utf-8')
        if 'september.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/css/september.css"></head>')
        path.write_text(s,encoding='utf-8')
    p=ROOT/'aerial/assets/css/inclusive.css';s=p.read_text(encoding='utf-8')
    marker='/* September overrides */'
    s=s.split(marker)[0]
    s=s.split('\nbody{font-size:17px}')[0]
    if '@import url("september.css");' not in s:s='@import url("september.css");\n'+s
    p.write_text(s+'\n'+marker+'\n'+(ROOT/'aerial/assets/css/september.css').read_text(encoding='utf-8'),encoding='utf-8')
    from interface_update import update_pages
    update_pages()
