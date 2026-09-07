import csv,json,math,sys
from pathlib import Path
from build_data import ROOT
from build_inclusive_data import load_sheet,finite
from scipy.stats import spearmanr

data=json.loads((ROOT/'aerial/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
points=data['points'];assert len(points)==135 and len({p['id'] for p in points})==135
assert all(p['position'] and p['position']['point_id']==p['id'] for p in points)
assert sum(p['n'] for p in points)==data['recordCount']==594
assert len(data['pdfPages'])>0
for path in data['pdfPages']:assert (ROOT/'aerial'/path).is_file()
_,raw=load_sheet('全量总表','全量总表0906');byid={r['B']:r for r in raw[3:] if r.get('B')}
for p in points:
    assert p['values']['AH']==byid[p['id']].get('AH')
    for k in ['mixScore','vitality']:
        assert p[k] is None or 0<=p[k]<=1
    if p['mismatch'] is not None:
        expected=math.log((1+p['vitality'])/(1+p['mixScore']))
        assert abs(expected-p['mismatch'])<1e-12
        assert (p['mismatch']>0)==(p['vitality']>p['mixScore'])
    if p['mixScore'] is not None:assert abs(p['mixScore']-sum(p['mix'])/5)<1e-12
    if p['vitality'] is not None:
        parts=[]
        for key in ['sample','clusters','density','gather']:
            vals=[q['metrics'][key] for q in points if finite(q['metrics'][key])]
            lo,hi=min(vals),max(vals)
            parts.append((p['metrics'][key]-lo)/(hi-lo) if hi>lo else 0)
        assert abs(p['vitality']-sum(parts)/4)<1e-12
    for col in ['U','V','Y','Z','AE','AA']:assert p['values'].get(col)==byid[p['id']].get(col)
selected=list(csv.DictReader((ROOT/'data_extract.csv').open(encoding='utf-8-sig')))
assert {r['point_id'] for r in selected}=={p['id'] for p in points if p['quadrant']}
for r in selected:
    v,m=float(r['活力度']),float(r['混合度']);assert v>=.5
    assert r['组别']==('双高' if m>=.5 else '高活力低混合')
assert {f['column'] for f in data['fields'] if 'category' in f}==set('EFGHIJ')
for m in data['memory']:
    assert sum(v['value'] for v in m['links'])==m['n']
for r in data['correlations']:
    if not finite(r['rho']):continue
    assert -1<=r['rho']<=1 and 0<=r['p']<=1 and r['n']>=3
    field=next(f for f in data['fields'] if f['key']==r['x'])
    if 'category' not in field:
        pairs=[(p['values'].get(field['column']),p['metrics'][r['y']]) for p in points]
        pairs=[(a,b) for a,b in pairs if finite(a) and finite(b)]
        rho,pvalue=spearmanr(*zip(*pairs))
        assert abs(rho-r['rho'])<1e-12 and abs(pvalue-r['p'])<1e-12
print('Verified ID joins, 135 map positions, 594 pedestrians, source columns, score bounds, category encoding and data_extract membership.')
