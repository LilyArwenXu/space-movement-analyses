"""Aggregate pedestrian observations; keep source identifiers out of public payload."""
from build_data import ROOT, SOURCE, read_source
from collections import Counter, defaultdict
import json, math, re
import numpy as np
from scipy.stats import rankdata, false_discovery_control

AGES=['幼年','青年','中年','老年']
SEXES=['男','女']
IDENTITIES=['居民倾向','游客倾向']
BEHAVIORS=['观察','光顾','等待','打卡','社交','争吵/纠纷','饮食','休憩','避雨/遮阳','工作','娱乐','运动','照看','整理']
BEHAVIOR_COLS=[chr(i) for i in range(76,90)]
BOOTSTRAPS=2000
PERMUTATIONS=4999
SEED=20260906

def entropy(counts):
    counts=np.asarray(counts,dtype=float)
    total=counts.sum()
    if total<=0:return None
    p=counts[counts>0]/total
    return float(-(p*np.log(p)).sum()/math.log(len(counts)))

def summarize(records,name):
    ages=[sum(r.get('H')==c for r in records) for c in AGES]
    sexes=[sum(r.get('I')==c for r in records) for c in SEXES]
    identities=[sum(r['identity']==c for r in records) for c in IDENTITIES]
    actions=[sum(r.get(k,0) or 0 for r in records) for k in BEHAVIOR_COLS]
    values=sorted(actions); total=sum(values); m=len(values)
    lorenz=[0]+(np.cumsum(values)/total).tolist() if total else None
    gini=float(sum((2*i-m-1)*v for i,v in enumerate(values,1))/(m*total)) if total else None
    top4=sum(sorted(values,reverse=True)[:4])/total if total else None
    return {'name':name,'n':len(records),'ages':ages,'sexes':sexes,'unknownSex':len(records)-sum(sexes),
            'identities':identities,'unknownIdentity':len(records)-sum(identities),'actions':actions,
            'mix':[entropy(ages),entropy(sexes),entropy(actions),entropy(identities)],
            'lorenz':lorenz,'gini':gini,'top4':top4,'actionTotal':total}

def permutation_spearman(x,y,rng):
    x=np.asarray(x);y=np.asarray(y);n=len(x)
    if n<4 or len(set(x))<2 or len(set(y))<2:return None,None
    a=rankdata(x);b=rankdata(y);a-=a.mean();b-=b.mean()
    a/=np.linalg.norm(a);b/=np.linalg.norm(b)
    rho=float(np.clip(a@b,-1,1));extreme=0
    for start in range(0,PERMUTATIONS,500):
        batch=min(500,PERMUTATIONS-start)
        perm=rng.permuted(np.broadcast_to(b,(batch,n)),axis=1)
        extreme+=int(np.count_nonzero(np.abs(perm@a)>=abs(rho)-1e-12))
    return rho,(extreme+1)/(PERMUTATIONS+1)

def build_people():
    sheet,raw=read_source('行人信息总表0905')
    records=[dict(r) for r in raw[1:] if r.get('B') and r.get('C') and r.get('D')]
    assert len(records)==len({r['B'] for r in records}),'Repeated pedestrian IDs'
    for r in records:
        match=re.search(r'区(.+?街道)',r['D'])
        r['admin']=match.group(1) if match else '街道未记录'
        a,b=r.get('AD'),r.get('AE')
        r['identity']=IDENTITIES[0] if isinstance(a,(int,float)) and isinstance(b,(int,float)) and a>b else IDENTITIES[1] if isinstance(a,(int,float)) and isinstance(b,(int,float)) and b>a else '未定'
    grouped=defaultdict(list)
    for r in records:grouped[r['C']].append(r)
    admins=[summarize([r for r in records if r['admin']==name],name) for name in sorted({r['admin'] for r in records})]
    whole=summarize(records,'全域')
    _,space_raw=read_source()
    space_headers=space_raw[2]
    space={r['B']:r for r in space_raw[3:] if r.get('B')}
    points=[];rng=np.random.default_rng(SEED)
    for pid,group in grouped.items():
        address=group[0]['D'];point=summarize(group,address.split('街道')[-1])
        point.update(address=address,admin=group[0]['admin'],node=len(points)+1)
        point['ci']=None
        # Age diversity uses a fixed four-category denominator. Small nodes are not ranked.
        if point['n']>=10:
            counts=np.asarray(point['ages']);n=int(counts.sum())
            draws=rng.multinomial(n,counts/n,size=BOOTSTRAPS)
            estimates=[entropy(c) for c in draws]
            point['ci']=[float(v) for v in np.quantile(estimates,[.025,.975])]
        else:
            point['mix']=[None]*4
        attrs={}
        for i,k in enumerate(AGES):attrs['age'+str(i)]=point['ages'][i]/sum(point['ages'])
        for i,k in enumerate(SEXES):attrs['sex'+str(i)]=point['sexes'][i]/sum(point['sexes']) if sum(point['sexes']) else None
        for i,k in enumerate(IDENTITIES):attrs['identity'+str(i)]=point['identities'][i]/sum(point['identities']) if sum(point['identities']) else None
        for i,k in enumerate(BEHAVIORS):attrs['act'+str(i)]=point['actions'][i]/point['n']
        for k in ['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']:
            v=space.get(pid,{}).get(k)
            if isinstance(v,(float,int)) and math.isfinite(v):attrs['space'+k]=v
        point['attributes']=attrs
        point['matchedSpace']=pid in space
        points.append(point)
    labels={**{'age'+str(i):v+'占比' for i,v in enumerate(AGES)},**{'sex'+str(i):v+'性占比' for i,v in enumerate(SEXES)},
            **{'identity'+str(i):v+'占比' for i,v in enumerate(IDENTITIES)},**{'act'+str(i):v+'人数占比' for i,v in enumerate(BEHAVIORS)},
            **{'space'+k:space_headers[k] for k in ['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']}}
    crowd=[k for k in labels if k.startswith(('age','sex','identity'))]
    behavior=[k for k in labels if k.startswith('act')]
    spatial=[k for k in labels if k.startswith('space')]
    configs=[('人群 × 行为',crowd,behavior),('人群 × 空间',crowd,spatial),('行为 × 空间',behavior,spatial)]
    correlations=[];matrices=[];rng=np.random.default_rng(SEED+1)
    for title,xkeys,ykeys in configs:
        matrices.append({'title':title,'xs':xkeys,'ys':ykeys})
        for x in xkeys:
            for y in ykeys:
                pairs=[(p['attributes'].get(x),p['attributes'].get(y)) for p in points]
                pairs=[(a,b) for a,b in pairs if a is not None and b is not None]
                rho,pval=permutation_spearman(*zip(*pairs),rng) if pairs else (None,None)
                correlations.append({'x':x,'y':y,'n':len(pairs),'rho':rho,'p':pval,'q':None})
    tested=[r for r in correlations if r['p'] is not None]
    if tested:
        for r,q in zip(tested,false_discovery_control([r['p'] for r in tested],method='bh')):r['q']=float(q)
    data={'source':SOURCE.name,'sheet':sheet,'spaceSheet':'全量总表(0906)','recordCount':len(records),'pointCount':len(points),
          'ageLabels':AGES,'sexLabels':SEXES,'identityLabels':IDENTITIES,'behaviorLabels':BEHAVIORS,'all':whole,'admins':admins,'points':points,
          'labels':labels,'matrices':matrices,'correlations':correlations,'testCount':len(tested),
          'bootstrap':BOOTSTRAPS,'permutations':PERMUTATIONS,'seed':SEED,
          'identityMethod':'居民指数大于游客指数为居民倾向，反之为游客倾向，相等或缺失记未定；不是实测居住身份。'}
    (ROOT/'spacemovement/people-data.js').write_text('window.PEOPLE = '+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8',newline='\n')
    print(json.dumps({'pedestrians':len(records),'points':len(points),'eligible':sum(p['n']>=10 for p in points),'gini':whole['gini'],'top4':whole['top4'],'tests':len(tested),'FDR_significant':sum(r['q']<.05 for r in tested)},ensure_ascii=False))

if __name__=='__main__':build_people()
