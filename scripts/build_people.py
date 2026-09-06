"""Aggregate pedestrian observations; keep source identifiers out of public payload."""
from build_data import ROOT, SOURCE, read_source
from collections import Counter, defaultdict
import json, math, re
import numpy as np
from scipy.stats import rankdata

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
    postures=[sum(r.get('J')==c for r in records) for c in ['落座','站立/倚靠']]
    social=[sum(r.get('G')==c for r in records) for c in ['独立','集聚']]
    values=sorted(actions); total=sum(values); m=len(values)
    lorenz=[0]+(np.cumsum(values)/total).tolist() if total else None
    gini=float(sum((2*i-m-1)*v for i,v in enumerate(values,1))/(m*total)) if total else None
    top4=sum(sorted(values,reverse=True)[:4])/total if total else None
    return {'name':name,'n':len(records),'ages':ages,'sexes':sexes,'unknownSex':len(records)-sum(sexes),
            'identities':identities,'unknownIdentity':len(records)-sum(identities),'actions':actions,
            'postures':postures,'social':social,
            'mix':[entropy(ages),entropy(actions),entropy(identities),entropy(postures),entropy(social)],
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
    for r in records:
        m=re.search(r'([\u4e00-\u9fff]+?(?:路|街|巷|大道))',r['D'].split('街道')[-1])
        r['road']=m.group(1) if m else '其他道路'
    admins=[summarize([r for r in records if r['admin']==name],name) for name in sorted({r['admin'] for r in records})]
    roads=[summarize([r for r in records if r['road']==name],name) for name in sorted({r['road'] for r in records})]
    admin_roads={g['name']:[summarize([r for r in records if r['admin']==g['name'] and r['road']==road],road)
                 for road in sorted({r['road'] for r in records if r['admin']==g['name']})] for g in admins}
    whole=summarize(records,'全域')
    _,space_raw=read_source()
    space_headers=space_raw[2]
    space={r['B']:r for r in space_raw[3:] if r.get('B')}
    points=[];rng=np.random.default_rng(SEED)
    for pid,group in grouped.items():
        address=group[0]['D'];point=summarize(group,address.split('街道')[-1])
        point.update(address=address,admin=group[0]['admin'],road=group[0]['road'],node=len(points)+1)
        point['ci']=None
        # Age diversity uses a fixed four-category denominator. Small nodes are not ranked.
        if point['n']>=5:
            counts=np.asarray(point['ages']);n=int(counts.sum())
            draws=rng.multinomial(n,counts/n,size=BOOTSTRAPS)
            estimates=[entropy(c) for c in draws]
            point['ci']=[float(v) for v in np.quantile(estimates,[.025,.975])]
        else:
            point['mix']=[None]*5
        attrs={}
        for i,k in enumerate(AGES):attrs['age'+str(i)]=point['ages'][i]/sum(point['ages'])
        for i,k in enumerate(SEXES):attrs['sex'+str(i)]=point['sexes'][i]/sum(point['sexes']) if sum(point['sexes']) else None
        for i,k in enumerate(IDENTITIES):attrs['identity'+str(i)]=point['identities'][i]/sum(point['identities']) if sum(point['identities']) else None
        for i,k in enumerate(BEHAVIORS):attrs['act'+str(i)]=point['actions'][i]/point['n']
        for k in ['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']:
            v=space.get(pid,{}).get(k)
            if isinstance(v,(float,int)) and math.isfinite(v):attrs['space'+k]=v
        attrs['sampleCount']=point['n']
        attrs['clusterCount']=len({r['F'] for r in group if r.get('F') is not None and str(r['F']).strip() and r['F']!=0})
        area=attrs.get('spaceM')
        attrs['stayDensity']=point['n']/area if area is not None and area>0 else None
        attrs['clusterRatio']=point['social'][1]/sum(point['social']) if sum(point['social']) else None
        attrs['ageMix']=entropy(point['ages'])
        for key,col in [('residentIndex','AD'),('visitorIndex','AE')]:
            values=[r[col] for r in group if isinstance(r.get(col),(int,float)) and math.isfinite(r[col])]
            attrs[key]=sum(values)/len(values) if values else None
        point['attributes']=attrs
        point['matchedSpace']=pid in space
        points.append(point)
    labels={**{'age'+str(i):v+'占比' for i,v in enumerate(AGES)},**{'sex'+str(i):v+'性占比' for i,v in enumerate(SEXES)},
            **{'identity'+str(i):v+'占比' for i,v in enumerate(IDENTITIES)},**{'act'+str(i):v+'人数占比' for i,v in enumerate(BEHAVIORS)},
            **{'space'+k:space_headers[k] for k in ['K','L','M','O','Q','R','S','T','U','V','Y','Z','AA','AE','AF','AG']}}
    labels.update({'sampleCount':'行人样本数','clusterCount':'行为集群数','stayDensity':'停留密度','clusterRatio':'集聚比例','ageMix':'年龄混合度','residentIndex':'居民指数','visitorIndex':'游客指数'})
    crowd=['age1','age2','age3','identity0','identity1']
    behavior=[k for k in labels if k.startswith('act')]
    spatial=[k for k in labels if k.startswith('space')]
    configs=[('行为x空间',['sampleCount','clusterCount','stayDensity','clusterRatio','ageMix','residentIndex','visitorIndex'],[k for k in spatial if k!='spaceAG']),('人群x行为',crowd,behavior),('人群x空间',crowd,spatial)]
    correlations=[];matrices=[];rng=np.random.default_rng(SEED+1)
    for title,xkeys,ykeys in configs:
        matrices.append({'title':title,'xs':xkeys,'ys':ykeys})
        for x in xkeys:
            for y in ykeys:
                pairs=[(p['attributes'].get(x),p['attributes'].get(y)) for p in points]
                pairs=[(a,b) for a,b in pairs if a is not None and b is not None]
                rho,pval=permutation_spearman(*zip(*pairs),rng) if pairs else (None,None)
                correlations.append({'x':x,'y':y,'n':len(pairs),'rho':rho,'p':pval})
    tested=[r for r in correlations if r['p'] is not None]
    # Three economic metrics are averaged over all valid surveyed point records,
    # including points without pedestrian observations. Mixed functions remain distinct.
    by_function=defaultdict(list)
    for row in space_raw[3:]:
        if row.get('B') and row.get('C'):by_function[str(row.get('N') or '功能未记录')].append(row)
    economy=[]
    for function,group in sorted(by_function.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        item={'function':function,'n':len(group)}
        for label,col in [('cost','Q'),('consumerShare','R'),('capacity','S')]:
            values=[r[col] for r in group if isinstance(r.get(col),(int,float)) and math.isfinite(r[col])]
            item[label]=sum(values)/len(values) if values else None
            item[label+'N']=len(values)
        economy.append(item)
    # A deliberately explicit scenario, not reconstructed historical land use.
    # Each observation contributes once; first matching behavior determines the proxy.
    proxy_rules=[('R','餐饮/饮品'),('M','零售'),('U','生产/办公'),('O','文化展示')]
    memory=[]
    for cohort in ['老年','中年']:
        flows=Counter()
        for r in records:
            if r.get('H')!=cohort:continue
            original=next((category for col,category in proxy_rules if r.get(col,0)>0),'生活服务')
            current=str(space.get(r['C'],{}).get('N') or '功能未记录')
            flows[(original,current)]+=1
        memory.append({'cohort':cohort,'n':sum(flows.values()),'links':[{'source':a,'target':b,'value':n} for (a,b),n in sorted(flows.items())]})
    data={'source':SOURCE.name,'sheet':sheet,'spaceSheet':'全量总表(0906)','recordCount':len(records),'pointCount':len(points),
          'ageLabels':AGES,'sexLabels':SEXES,'identityLabels':IDENTITIES,'behaviorLabels':BEHAVIORS,'all':whole,'admins':admins,'roads':roads,'adminRoads':admin_roads,'points':points,'economy':economy,'memory':memory,
          'memoryMethod':'代际偏好推演，非历史实测。当前年长群体的活动作为过去同一群体偏好的代理，不换算具体年份。功能假设按饮食→餐饮/饮品、光顾→零售、工作→生产/办公、打卡→文化展示的顺序优先匹配，其余活动归入生活服务；这是一项建模假设，不等于点位曾有该用途。每条行人记录只计一次。',
          'labels':labels,'matrices':matrices,'correlations':correlations,'testCount':len(tested),
          'bootstrap':BOOTSTRAPS,'permutations':PERMUTATIONS,'seed':SEED,'minimumSample':5,
          'identityMethod':'居民指数大于游客指数为居民倾向，反之为游客倾向，相等或缺失记未定；不是实测居住身份。'}
    (ROOT/'spacemovement/people-data.js').write_text('window.PEOPLE = '+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8',newline='\n')
    print(json.dumps({'pedestrians':len(records),'points':len(points),'eligible':sum(p['n']>=5 for p in points),'gini':whole['gini'],'top4':whole['top4'],'tests':len(tested)},ensure_ascii=False))

if __name__=='__main__':build_people()
