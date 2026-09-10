"""Recompute requested scores independently from workbook cells and check export classes."""
import csv,json,math
from pathlib import Path
from build_data import read_source,ROOT
d=json.loads((ROOT/'aerial/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
_,rows=read_source(d['spaceSheet']);raw={r['A']:r for r in rows[3:] if isinstance(r.get('A'),(float,int)) and r.get('B')}
assert len(raw)==len(d['points'])==135
for index,p in enumerate(d['points']):
    r=raw[p['values']['A']]
    assert p['address']==r['B']
    for dim in d['mixDimensions']:
        a=[r.get(k) for k in dim['columns']];assert a==p['mixCounts'][dim['key']]
        if all(isinstance(x,(int,float)) and x>=0 for x in a) and sum(a)>0:
            expected=-sum(x/sum(a)*math.log(x/sum(a)) for x in a if x)/math.log(len(a))
            assert math.isclose(expected,p['metrics'][dim['key']],abs_tol=1e-12)
        else:assert p['metrics'][dim['key']] is None
    for key,filename,column in [('quality','gua.csv','界面品质'),('vitality','four.csv','活力度'),('mixScore','mixing_scores.csv','混合度')]:
        source=list(csv.DictReader((ROOT/'result/shap'/filename).open(encoding='utf-8-sig')))
        expected=float(source[index][column])
        assert math.isclose(p[key],expected,abs_tol=1e-12),(p['id'],key,p[key],expected)
rows=list(csv.DictReader((ROOT/'data-extract.csv').open(encoding='utf-8-sig')))
means={key:math.fsum(p[key] for p in d['points'] if p[key] is not None)/sum(p[key] is not None for p in d['points']) for key in ['quality','vitality','mixScore']}
assert all(math.isclose(means[k],d['scoreMeans'][k],abs_tol=1e-12) for k in means)
expected=set()
for p in d['points']:
    for kind,x,y,xlabel,ylabel in [('qualityVitality','quality','vitality','界面品质','活力度'),('qualityMix','quality','mixScore','界面品质','混合度'),('mismatch','vitality','mixScore','活力度','混合度')]:
        a,b=p[x],p[y];group=None
        if a is not None and b is not None:
            if a<means[x] and b>=means[y]:group='高'+ylabel+'低'+xlabel
            elif a>=means[x] and b<means[y]:group='高'+xlabel+'低'+ylabel
        assert p['mismatchGroups'][kind]==group
        if group:expected.add((p['id'],kind,group))
assert {(r['point_id'],r['分析'],r['组别']) for r in rows}==expected
for r in rows:
    a,b,mx,my=[float(r[k]) for k in ['横轴值','纵轴值','横轴全域有效评分均值','纵轴全域有效评分均值']]
    assert (a<mx and b>=my) if r['象限']=='左上' else (a>=mx and b<my)
print('Verified 135 source points, five entropy dimensions, Q/V/M scores, and',len(rows),'mismatch memberships.')
print('Mean thresholds:',means)
