"""Case-only statistics. Never import or consult the full workbook dataset."""
import math
from collections import Counter
from scipy.stats import spearmanr


def number(value):
    try:
        value=float(value)
        return value if math.isfinite(value) else None
    except (TypeError,ValueError):return None


def entropy(counts):
    total=sum(counts)
    return -sum((n/total)*math.log(n/total) for n in counts if n)/math.log(len(counts)) if total else None


def analyze(nodes,people,dimensions,kind):
    """One sample is one node record, not a duplicated node per pedestrian."""
    result=[]
    for index,node in enumerate(nodes):
        members=[r for r in people if r.get('点位ID')==node.get('点位ID')] if node.get('点位ID') else [r for r in people if r.get('完整地址')==node.get('完整地址')]
        values={key:number(node.get(label)) for key,label in dimensions['quality']}
        sample=number(node.get('行人样本数'));area=number(node.get('有效停留空间面积(㎡)'));gather=number(node.get('集聚人数'))
        metrics={'sample':sample,'clusters':number(node.get('行为集群数')),
                 'density':sample/area if sample is not None and area and area>0 else None,
                 'gather':gather/sample if gather is not None and sample and sample>0 else None}
        for key,label in [('resident','居民指数'),('visitor','游客指数')]:
            valid=[number(r.get(label)) for r in members];valid=[v for v in valid if v is not None]
            metrics[key]=sum(valid)/len(valid) if valid else None
        for key,column,categories in [('ageMix','年龄',['幼年','青年','中年','老年']),('postureMix','姿态',['落座','站立/倚靠']),('socialMix','社交状态',['独立','集聚'])]:
            counts=Counter(r.get(column) for r in members);metrics[key]=entropy([counts[c] for c in categories])
        behaviors=['观察','光顾','等待','打卡','社交','争吵/纠纷','饮食','休憩','避雨/遮阳','工作','娱乐','运动','照看','整理']
        metrics['activityMix']=entropy([sum(number(r.get('行为_'+b)) or 0 for r in members) for b in behaviors])
        identity=[(number(r.get('居民指数')),number(r.get('游客指数'))) for r in members]
        identity=[(a,b) for a,b in identity if a is not None and b is not None and a!=b]
        metrics['identityMix']=entropy([sum(a>b for a,b in identity),sum(b>a for a,b in identity)])
        mixing=[metrics[k] for k,_ in dimensions['mix']]
        result.append({'id':node.get('点位ID') or str(index),'name':node.get('完整地址','案例观测'),
                       'values':values,'metrics':metrics,'mixScore':sum(mixing)/len(mixing) if all(v is not None for v in mixing) else None,
                       'vitality':None,'peopleCount':len(members)})
    # Use only within-case variation; a single node cannot define min–max calibration.
    keys=['sample','clusters','density','gather']
    bounds={k:[p['metrics'][k] for p in result if p['metrics'][k] is not None] for k in keys}
    if all(len(v)>1 and max(v)>min(v) for v in bounds.values()):
        for p in result:
            if all(p['metrics'][k] is not None for k in keys):
                p['vitality']=sum((p['metrics'][k]-min(bounds[k]))/(max(bounds[k])-min(bounds[k])) for k in keys)/len(keys)
    xkind='vitality' if kind=='mismatch' else 'quality';ykind='vitality' if kind=='qualityVitality' else 'mix'
    correlations=[]
    for i,(x,_) in enumerate(dimensions[xkind]):
        for j,(y,_) in enumerate(dimensions[ykind]):
            pairs=[((p['values'] if xkind=='quality' else p['metrics']).get(x),p['metrics'].get(y)) for p in result]
            pairs=[(a,b) for a,b in pairs if a is not None and b is not None]
            rho=pvalue=None
            reason='有效节点观测不足3条' if len(pairs)<3 else '指标没有变化'
            if len(pairs)>=3 and len({a for a,b in pairs})>1 and len({b for a,b in pairs})>1:
                r=spearmanr(*zip(*pairs));rho=float(r.statistic);pvalue=float(r.pvalue);reason=''
            if not pairs:reason='指标缺失，无法配对'
            correlations.append({'x':i,'y':j,'rho':rho,'p':pvalue,'n':len(pairs),'reason':reason})
    return {'points':result,'correlations':correlations,'nodeCount':len(nodes),'peopleCount':len(people),
            'limitations':'Spearman 以节点观测为样本；行人记录仅用于计算本案例构成，不作为重复的节点观测。居民/游客指数缺失时，身份混合度与混合度综合评分不计算；单节点无法进行活力度最小最大标准化。'}
