"""One point-ID based source for all Inclusive Vitality views and data_extract.csv."""
from pathlib import Path
from collections import defaultdict,Counter
import csv, json, math, re, shutil, zipfile
import xml.etree.ElementTree as ET
from build_data import ROOT, SOURCE, read_source, NS
from build_people import summarize, entropy, IDENTITIES, BEHAVIORS
from scipy.stats import spearmanr

def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
def avg(values):
    values=[v for v in values if finite(v)]
    return sum(values)/len(values) if values else None
def load_sheet(prefix,fallback):
    with zipfile.ZipFile(SOURCE) as z:
        names=[s.attrib['name'] for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS)]
    dated=[(int(m.group(1)),n) for n in names if (m:=re.fullmatch(re.escape(prefix)+r'[（(](\d{4})[）)]',n))]
    name=prefix if prefix in names else max(dated)[1] if dated else fallback
    return read_source(name)
def clean(v):
    if isinstance(v,float) and not math.isfinite(v): return None
    return v
def tokens(value):return [s.strip() for s in re.split('[；;、\n]',str(value or '')) if s.strip()]

def build():
    space_sheet,raw=read_source('全量总表（0907）')
    people_sheet,praw=read_source('行人信息总表（0907）')
    original_raw,original_praw=raw,praw
    from source_adapter import adapt
    raw,praw=adapt(raw,praw)
    headers=raw[2]
    source_rows=[r for r in raw[3:] if r.get('B') and r.get('C')]
    assert len({r['B'] for r in source_rows})==len(source_rows)
    records=[dict(r) for r in praw[1:] if r.get('B') and r.get('C') and r.get('D')]
    for r in records:
        m=re.search(r'区(.+?街道)',r['D']);r['admin']=m.group(1) if m else '未记录街道'
        m=re.search(r'([\u4e00-\u9fff]+?(?:路|街|巷|大道))',r['D'].split('街道')[-1]);r['road']=m.group(1) if m else '未记录道路'
        a,b=r.get('AD'),r.get('AE')
        r['identity']=IDENTITIES[0] if finite(a) and finite(b) and a>b else IDENTITIES[1] if finite(a) and finite(b) and b>a else '未定'
    grouped=defaultdict(list)
    for r in records:grouped[r['C']].append(r)
    location=json.loads((ROOT/'hengfu-map-point-locations-2026-09-07/points.json').read_text(encoding='utf-8'))
    positions={p['point_id']:p for p in location['points']}
    points=[]
    for row in source_rows:
        pid=row['B'];members=grouped[pid];pos=positions.get(pid);address=row['C']
        p=summarize(members,address.split('街道')[-1])
        p.update(id=pid,address=address,values={k:clean(v) for k,v in row.items()},position=pos,
                 admin=pos['subdistrict'] if pos else (members[0]['admin'] if members else '未定位街道'),
                 road=pos['road'] if pos else (members[0]['road'] if members else '未定位道路'))
        p['mixScore']=avg(p['mix']) if all(finite(v) for v in p['mix']) else None
        p['smallSample']=len(members)<5
        # Counts for map and vitality use the point table; absent observations are not fabricated.
        p['metrics']={'sample':row.get('AH'),'clusters':row.get('AI'),
          'density':row['AH']/row['M'] if finite(row.get('AH')) and finite(row.get('M')) and row['M']>0 else None,
          'gather':row['AK']/row['AH'] if finite(row.get('AK')) and finite(row.get('AH')) and row['AH']>0 else None,
          'ageMix':p['mix'][0], 'resident':avg([r.get('AD') for r in members]),'visitor':avg([r.get('AE') for r in members])}
        points.append(p)
    norms={}
    for key in ['sample','clusters','density','gather']:
        v=[p['metrics'][key] for p in points if finite(p['metrics'][key])]
        norms[key]={'min':min(v) if v else None,'max':max(v) if v else None}
    for p in points:
        parts=[]
        for key,bounds in norms.items():
            value=p['metrics'][key];lo,hi=bounds['min'],bounds['max']
            parts.append((value-lo)/(hi-lo) if finite(value) and hi>lo else 0 if finite(value) else None)
        p['vitality']=sum(parts)/4 if all(finite(v) for v in parts) else None
        v,m=p['vitality'],p['mixScore']
        p['mismatch']=math.log((1+v)/(1+m)) if finite(v) and finite(m) else None
        p['quadrant']=('高活力低混合' if m<.5 else '双高') if finite(v) and finite(m) and v>=.5 else None
    all_group=summarize(records,'全域')
    admins=[]
    for name in sorted({r['admin'] for r in records}):
        members=[r for r in records if r['admin']==name];g=summarize(members,name)
        g['roads']=[summarize([r for r in members if r['road']==road],road) for road in sorted({r['road'] for r in members})]
        admins.append(g)
    spatial=['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']
    fields=[{'key':key,'label':headers[key],'column':key} for key in spatial]
    for col in ['E','F','G','H','I','J']:
        for category in sorted({t for r in source_rows for t in tokens(r.get(col))}):
            fields.append({'key':col+':'+category,'label':category,'column':col,'category':category,'group':headers[col]})
    ys={'sample':'行人样本数','clusters':'行为集群数','density':'停留密度','gather':'集聚比例','ageMix':'年龄混合度','resident':'居民指数','visitor':'游客指数'}
    correlations=[]
    for field in fields:
        for key in ys:
            pairs=[]
            for p in points:
                raw_value=p['values'].get(field['column'])
                x=int(field['category'] in tokens(raw_value)) if 'category' in field and raw_value else raw_value if 'category' not in field else None
                y=p['metrics'][key]
                if finite(x) and finite(y):pairs.append((x,y))
            rho=pvalue=None
            if len(pairs)>=3 and len({x for x,y in pairs})>1 and len({y for x,y in pairs})>1:
                result=spearmanr(*zip(*pairs));rho=float(result.statistic);pvalue=float(result.pvalue)
            correlations.append({'x':field['key'],'y':key,'n':len(pairs),'rho':rho,'p':pvalue})
    weights=[]
    for road in sorted({p['road'] for p in points}):
        group=[p for p in points if p['road']==road]
        weights.append({'road':road,'values':[avg([p['values'].get(k) for p in group]) for k in ['U','V','Y','Z','AE','AA']]})
        if weights[-1]['values'][4] is not None:weights[-1]['values'][4]/=20
    memory=[];spaces={r['B']:r for r in source_rows}
    proxy=[('R','餐饮/饮品'),('M','零售'),('U','生产/办公'),('O','文化展示')]
    for cohort in ['老年','中年']:
        flows=Counter()
        for r in records:
            if r.get('H')!=cohort:continue
            origin=next((category for col,category in proxy if finite(r.get(col)) and r[col]>0),'生活服务')
            flows[(origin,str(spaces.get(r['C'],{}).get('N') or '功能未记录'))]+=1
        memory.append({'cohort':cohort,'n':sum(flows.values()),'links':[{'source':a,'target':b,'value':n} for (a,b),n in sorted(flows.items())]})
    assets=ROOT/'aerial/assets/data';assets.mkdir(exist_ok=True,parents=True)
    shutil.copy2(ROOT/'hengfu-map-point-locations-2026-09-07/hengfu-base-map.jpg',assets/'map.jpg')
    # Render document pages into the site shell; PDF reader UI cannot change the site theme.
    pdfs=list((ROOT/'spacemovement').glob('目录索引*.pdf')) or list((ROOT/'aerial/spacemovement').glob('目录索引*.pdf'))
    pdf_pages=[]
    if pdfs:
        import pypdfium2 as pdfium
        doc=pdfium.PdfDocument(str(pdfs[0]))
        for i in range(len(doc)):
            name=f'index-{i+1:02d}.png';path=assets/name
            if not path.exists() or path.stat().st_mtime<pdfs[0].stat().st_mtime:
                doc[i].render(scale=1.7).to_pil().convert('L').save(path)
            pdf_pages.append('assets/data/'+name)
    def table(rows):
        cols=sorted({k for r in rows for k in r},key=lambda c:(len(c),c))
        return {'columns':cols,'rows':[[clean(r.get(k)) for k in cols] for r in rows]}
    data={'rows':len(points),'recordCount':len(records),'spaceSheet':space_sheet,'peopleSheet':people_sheet,
          'headers':headers,'points':points,'all':all_group,'admins':admins,'behaviorLabels':BEHAVIORS,
          'norms':norms,'fields':fields,'ys':ys,'correlations':correlations,'weights':weights,
          'memory':memory,'pdfPages':pdf_pages,
          'tables':{'space':table(original_raw),'people':table(original_praw)},'mapMeta':location['metadata']['base_map']}
    from analysis_revision import revise
    _,mean_rows=read_source('点位均值')
    mean_lookup={r.get('A'):(r.get('B'),r.get('C')) for r in mean_rows[1:]}
    for p in points:
        p['metrics']['resident'],p['metrics']['visitor']=mean_lookup.get(p['address'],(None,None))
    data=revise(data)
    from september_update import enrich
    enrich(data)
    (assets/'inclusive-data.js').write_text('window.INCLUSIVE='+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8')
    extracted=[p for p in points if p['quadrant']]
    with (ROOT/'data_extract.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['point_id','完整地址','组别','活力度','混合度','不配得性','样本量'])
        for p in extracted:writer.writerow([p['id'],p['address'],p['quadrant'],p['vitality'],p['mixScore'],p['mismatch'],p['n']])
    (ROOT/'.site-build/inclusive-audit.json').write_text(json.dumps({'points':len(points),'mapMatched':sum(bool(p['position']) for p in points),'records':len(records),'scored':sum(p['mismatch'] is not None for p in points),'extracted':len(extracted),'pdfPages':len(pdf_pages),'categoryFields':len(fields)-16},ensure_ascii=False),encoding='utf-8')
    return data

if __name__=='__main__':print(json.dumps({k:v for k,v in build().items() if k in ['rows','recordCount']},ensure_ascii=False))
