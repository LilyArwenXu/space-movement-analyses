"""Recompute requested scores independently from workbook cells and check export classes."""
import csv,json,math
from pathlib import Path
from build_data import read_source,ROOT
d=json.loads((ROOT/'aerial/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
_,rows=read_source(d['spaceSheet']);raw={r['A']:r for r in rows[3:] if isinstance(r.get('A'),(float,int)) and r.get('B')}
assert len(raw)==len(d['points'])==135
for p in d['points']:
    r=raw[p['values']['A']]
    assert p['address']==r['B']
    for dim in d['mixDimensions']:
        a=[r.get(k) for k in dim['columns']];assert a==p['mixCounts'][dim['key']]
        if all(isinstance(x,(int,float)) and x>=0 for x in a) and sum(a)>0:
            expected=-sum(x/sum(a)*math.log(x/sum(a)) for x in a if x)/math.log(len(a))
            assert math.isclose(expected,p['metrics'][dim['key']],abs_tol=1e-12)
        else:assert p['metrics'][dim['key']] is None
    if all(x is not None for x in p['mix']):assert math.isclose(p['mixScore'],sum(x*w for x,w in zip(p['mix'],[.149,.141,.250,.228,.233])),abs_tol=1e-12)
    # Explicit original workbook mapping, independent of the adapted column keys.
    for kind,columns,weights in [('quality',['N','T','S','AF','AG','AH','Z','AA','AB','V','W'],[.068,.078,.167,.112,.069,.058,.095,.099,.077,.094,.084])]:
        if p[kind] is not None:
            score=0
            for col,w in zip(columns,weights):
                a=[row[col] for row in raw.values() if isinstance(row.get(col),(int,float))];lo,hi=min(a),max(a);score+=w*((r[col]-lo)/(hi-lo) if hi>lo else 0)
            assert math.isclose(score,p[kind],abs_tol=1e-12),(p['id'],score,p[kind])
    if p['vitality'] is not None:
        total=0
        for key,w in zip(['sample','clusters','density','gather'],[.194,.144,.205,.456]):
            a=[n['metrics'][key] for n in d['points'] if n['metrics'][key] is not None];lo,hi=min(a),max(a);total+=w*((p['metrics'][key]-lo)/(hi-lo) if hi>lo else 0)
        assert math.isclose(total,p['vitality'],abs_tol=1e-12)
rows=list(csv.DictReader((ROOT/'data-extract.csv').open(encoding='utf-8-sig')))
expected={(p['id'],k,g) for p in d['points'] for k,g in p['mismatchGroups'].items() if g}
assert {(r['point_id'],r['分析'],r['组别']) for r in rows}==expected
print('Verified 135 source points, five entropy dimensions, Q/V/M scores, and',len(rows),'mismatch memberships.')
