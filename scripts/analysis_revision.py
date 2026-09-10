"""Transparent classification coding and score calibration for the revised analyses."""
import math,re
from scipy.stats import spearmanr

def revise(data):
    pts=data['points'];finite=lambda v:isinstance(v,(int,float)) and math.isfinite(v)
    spatial=['K','L','M','O','P','Q','R','S','T','U','V','W','Y','Z','AA','AE','AF']
    defs=[('typeB1','B1 界面退让'),('typeB2','B2 可视度'),('typeB3a','B3 构件延伸a'),('typeB3b','B3 构件延伸b'),('typeB3c','B3 构件延伸c'),('typeC','C 尺度层级'),('facility','D 附属设施加权指数')]
    for p in pts:
        v=p['values']
        for key,col,pattern,mapping in [('typeB1','F',r'B1([abcd])',{'a':0,'b':2,'c':1,'d':3}),('typeB2','G',r'B2([abcd])',{'a':0,'b':1,'c':2,'d':3}),('typeC','I',r'C([1-4])',{'1':1,'2':2,'3':3,'4':4})]:
            m=re.search(pattern,str(v.get(col) or ''));v[key]=mapping[m[1]] if m else None
        for letter in 'abc':
            s=v.get('H');v['typeB3'+letter]=len(set(re.findall(r'B3'+letter+r'(?:-[iv]+)?',str(s)))) if s else None
        s=v.get('J');v['facility']=v['facilitySource'] if 'facilitySource' in v else len(set(re.findall(r'D([1-7])',str(s))))/7 if s else None
        for i,key in enumerate(['ageMix','activityMix','identityMix','postureMix','socialMix']):p['metrics'][key]=p['mix'][i]
        p['vitalityRaw']=p['vitality']
    # No display calibration: final authoritative scores are loaded from SHAP CSVs.
    coefficient=1
    for p in pts:
        p['mismatch']=None
        p['quadrant']=None
    ys={'sample':'行人样本数','clusters':'行为集群数','density':'停留密度','gather':'集聚比例','resident':'居民指数','visitor':'游客指数','ageMix':'年龄混合度','activityMix':'活动丰富度','identityMix':'身份倾向混合度','postureMix':'姿态丰富度','socialMix':'社交状态混合度'}
    fields=[{'key':k,'column':k,'label':name,'group':'界面类型'} for k,name in defs]+[{'key':k,'column':k,'label':data['headers'][k],'group':'空间指标'} for k in spatial]
    corrs=[]
    for f in fields:
        for y in ys:
            pairs=[(p['values'].get(f['key']),p['metrics'].get(y)) for p in pts]
            pairs=[(a,b) for a,b in pairs if finite(a) and finite(b)]
            rho=pval=None
            if len(pairs)>=3 and len({a for a,b in pairs})>1 and len({b for a,b in pairs})>1:
                result=spearmanr(*zip(*pairs));rho=float(result.statistic);pval=float(result.pvalue)
            corrs.append({'x':f['key'],'y':y,'n':len(pairs),'rho':rho,'p':pval})
    selected=sorted({r['x'] for r in corrs if r['x'] in spatial and finite(r['rho']) and r['rho']>0 and r['p']<.05},key=spatial.index)
    ranges={k:(min(p['values'][k] for p in pts if finite(p['values'].get(k))),max(p['values'][k] for p in pts if finite(p['values'].get(k)))) for k in selected}
    for p in pts:
        values=[(p['values'][k]-ranges[k][0])/(ranges[k][1]-ranges[k][0]) for k in selected if finite(p['values'].get(k)) and ranges[k][1]>ranges[k][0]]
        p['quality']=sum(values)/len(values) if selected and len(values)==len(selected) else None
    data.update(fields=fields,ys=ys,correlations=corrs,qualityFields=selected,qualityRule='ρ>0 且 p<0.05（正相关且显著，不属于强相关）',vitalityCoefficient=coefficient,dualHigh=sum(p['quadrant']=='双高' for p in pts))
    data['headers'].update(dict(defs))
    return data
