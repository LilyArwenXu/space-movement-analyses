from build_data import ROOT,read_source
from build_people import entropy,BEHAVIOR_COLS
import json,math
import numpy as np
from scipy.stats import false_discovery_control,spearmanr

data=json.loads((ROOT/'spacemovement/people-data.js').read_text(encoding='utf-8').removeprefix('window.PEOPLE = ').strip().rstrip(';'))
_,raw=read_source('行人信息总表0905')
records=[r for r in raw[1:] if r.get('B') and r.get('C') and r.get('D')]
assert len(records)==data['recordCount']==594
assert sum(g['n'] for g in data['admins'])==sum(p['n'] for p in data['points'])==594
assert data['pointCount']==len(data['points'])==111
assert all(p['matchedSpace'] for p in data['points'])
assert sum(p['n']>=10 for p in data['points'])==19
for p in data['points']:
    assert sum(p['ages'])==p['n']
    if p['n']<10:assert p['ci'] is None and p['mix']==[None]*4
    else:assert 0<=p['ci'][0]<=p['ci'][1]<=1
for i,k in enumerate(BEHAVIOR_COLS):assert data['all']['actions'][i]==sum(r.get(k,0) or 0 for r in records)
assert abs(entropy([1,1,1,1])-1)<1e-12 and entropy([10,0,0,0])==0
counts=np.asarray(data['all']['actions']);gini=float(np.abs(counts[:,None]-counts).sum()/(2*len(counts)*counts.sum()))
assert abs(gini-data['all']['gini'])<1e-12
assert data['all']['lorenz'][0]==0 and data['all']['lorenz'][-1]==1
tested=[r for r in data['correlations'] if r['p'] is not None]
assert len(tested)==data['testCount']
adjusted=false_discovery_control([r['p'] for r in tested],method='bh')
for r,q in zip(tested,adjusted):assert abs(r['q']-q)<1e-12
for r in tested[::50]:
    pairs=[(p['attributes'].get(r['x']),p['attributes'].get(r['y'])) for p in data['points']]
    pairs=[(a,b) for a,b in pairs if a is not None and b is not None]
    assert len(pairs)==r['n']
    assert abs(float(spearmanr(*zip(*pairs)).statistic)-r['rho'])<1e-12
    assert 0<r['p']<=1 and r['q']>=r['p']-1e-12
print('Verified pedestrian totals, point matching, bootstrap bounds, Lorenz/Gini, sampled Spearman coefficients and global BH-FDR correction.')
