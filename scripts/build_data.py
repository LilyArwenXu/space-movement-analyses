from pathlib import Path
import zipfile, xml.etree.ElementTree as ET, re, json, math
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.build-deps'))
SOURCE = ROOT / 'spacemovement/工作表-衡复风貌区调研全量总表-2026.xlsx'
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_source(sheet_name='全量总表0906'):
    with zipfile.ZipFile(SOURCE) as z:
        strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        sheets=wb.find('m:sheets',NS)
        sheet=next(s for s in sheets if re.sub(r'[（）()]','',s.attrib['name'])==re.sub(r'[（）()]','',sheet_name))
        rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rel=next(r for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if r.attrib['Id']==rid)
        target=rel.attrib['Target'].lstrip('/')
        if not target.startswith('xl/'): target='xl/'+target
        rows=[]
        for row in ET.fromstring(z.read(target)).findall('.//m:sheetData/m:row',NS):
            out={}
            for c in row:
                col=re.sub(r'\d','',c.attrib['r']); v=c.find('m:v',NS)
                value=v.text if v is not None else None
                if c.attrib.get('t')=='s' and value is not None: value=strings[int(value)]
                elif c.attrib.get('t')=='inlineStr': value=''.join(c.find('m:is',NS).itertext())
                elif value is not None:
                    try: value=float(value)
                    except ValueError: pass
                out[col]=value
            rows.append(out)
        return sheet.attrib['name'],rows
def build():
    from scipy.stats import spearmanr
    name,raw=read_source(); headers=raw[2]
    rows=[]
    for i,r in enumerate(raw[3:],4):
        if not isinstance(r.get('C'),str) or not r['C'].strip(): continue
        address=r['C'].strip(); short=address.split('街道')[-1]
        match=re.search(r'([\u4e00-\u9fff]+?(?:路|街|巷|大道))',short)
        row={'address':address,'short':short,'street':match.group(1) if match else '其他道路','sourceRow':i}
        for k,v in r.items():
            if isinstance(v,(int,float)) and math.isfinite(v): row[k]=v
        # Cached formula zeros on rows without observations are not observed behavior.
        if 'AH' not in row:
            for k in ['BI','BJ','BK','BQ']: row.pop(k,None)
        rows.append(row)
    rows.sort(key=lambda r:(r['street'],int(re.search(r'\d+',r['short']).group()) if re.search(r'\d+',r['short']) else 0,r['sourceRow']))
    streets=sorted(set(r['street'] for r in rows))
    for street in streets:
        group=[r for r in rows if r['street']==street]
        for i,r in enumerate(group):
            r['position']=i/(len(group)-1) if len(group)>1 else .5
            if r.get('T',0)>0 and 'AH' in r: r['choice']=r['AH']/r['T']
    xs=['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']; ys=['AH','AI','BJ','BK','BQ','BR','BS']
    correlations=[]
    for x in xs:
        for y in ys:
            pairs=[(r[x],r[y]) for r in rows if x in r and y in r]
            rho=p=None
            if len(pairs)>2 and len(set(a for a,b in pairs))>1 and len(set(b for a,b in pairs))>1:
                result=spearmanr(*zip(*pairs)); rho=float(result.statistic); p=float(result.pvalue)
            correlations.append({'x':x,'y':y,'n':len(pairs),'rho':rho,'p':p})
    # Reference-style triangular matrix across all usable space/behavior fields.
    matrix_fields=[k for k in xs+ys if len({r[k] for r in rows if k in r})>1]
    matrix_correlations=[]
    for i,x in enumerate(matrix_fields):
        for y in matrix_fields[:i+1]:
            pairs=[(r[x],r[y]) for r in rows if x in r and y in r]
            rho=p=None
            if len(pairs)>2 and len({a for a,b in pairs})>1 and len({b for a,b in pairs})>1:
                result=spearmanr(*zip(*pairs));rho=float(result.statistic);p=float(result.pvalue)
            matrix_correlations.append({'x':x,'y':y,'n':len(pairs),'rho':rho,'p':p})
    nodes=[]
    for address in dict.fromkeys(r['address'] for r in rows):
        group=[r for r in rows if r['address']==address]; node={k:group[0][k] for k in ['address','short','street']}
        node['records']=len(group)
        for k in ['O','AU','AV','AX','AY','BA','BB']:
            values=[r[k] for r in group if k in r]
            node[k]=(sum(values)/len(values) if k=='O' else sum(values)) if values else None
        nodes.append(node)
    data={'source':SOURCE.name,'sheet':name,'headers':headers,'rows':rows,'nodes':nodes,'streets':streets,'xs':xs,'ys':ys,'correlations':correlations,'matrixFields':matrix_fields,'matrixCorrelations':matrix_correlations}
    (ROOT/'spacemovement/survey-data.js').write_text('window.SURVEY = '+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8',newline='\n')
    # Preserve the existing weights chart and its grey levels, refreshing only its data.
    path=ROOT/'spacemovement/street_interface_weights.html'; html=path.read_text(encoding='utf-8')
    fields={'界面开放度':'U','临界互动性':'V','视觉丰富度':'Y','历史感知度':'Z','遮阴率':'AE','路面状态':'AA'}
    series={}
    for label,key in fields.items():
        series[label]=[]
        for street in streets:
            values=[r[key] for r in rows if r['street']==street and key in r]
            series[label].append(round(sum(values)/len(values)/(20 if key=='AE' else 1),4) if values else None)
    html=re.sub(r'const resData = .*?;', 'const resData = '+json.dumps({'roads':streets,'series':series},ensure_ascii=False)+';',html,count=1)
    html=html.replace('临界互动性','临街互动性').replace('界面整体状态由六项维度加权决定（各项满分5分，遮阴率已等比换算为5分制，悬浮可查看具体权重占比）','全量总表(0906) · 各街道有效评分均值；遮荫率÷20换算为5分制；占比为六项均值的构成比例').replace('综合评估加权总分','六项评分均值合计').replace('加权综合得分','六项评分均值合计')
    html=re.sub(r'\$\{\(p.value == null[^}]+\}', "${p.value == null ? '缺失' : p.value.toFixed(2)}",html)
    html=html.replace('${p.value.toFixed(2)}',"${p.value == null ? '缺失' : p.value.toFixed(2)}")
    path.write_text('\n'.join(line.rstrip() for line in html.strip().splitlines())+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'records':len(rows),'nodes':len(nodes),'streets':len(streets),'observations':sum('AH' in r for r in rows),'correlations':len(correlations)},ensure_ascii=False))
if __name__=='__main__': build()
