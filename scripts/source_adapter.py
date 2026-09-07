"""Adapt the revised workbook columns without reusing old observation values."""
import json
from build_data import ROOT,read_source

def adapt(raw,praw):
    if raw[2].get('B')!='完整地址':return raw,praw
    locations=json.loads((ROOT/'hengfu-map-point-locations-2026-09-07/points.json').read_text(encoding='utf-8'))['points']
    byseq={p['sequence']:p for p in locations};byaddress={}
    for p in locations:byaddress.setdefault(p['full_address'],[]).append(p)
    mapping=dict(zip('E F G I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR AS AT AU AV AW AX AY AZ BA BB BC BD BE BF BG'.split(),
                         'C D E I J L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR AS AT AU AV AW AX AY AZ BA BB BC BD BE BF BG BH BI'.split()))
    mapping['BH']='BI'
    headers={k:raw[2].get(v) for k,v in mapping.items()};headers.update(A='序号',B='点位ID',C='完整地址',H='B3 构件延伸')
    output=raw[:2]+[headers]
    for r in raw[3:]:
        if not isinstance(r.get('A'),(int,float)) or not r.get('B'):continue
        pos=byseq.get(r['A']);assert pos and pos['full_address']==r['B'],('Unmatched source node',r['A'],r['B'])
        row={k:r.get(v) for k,v in mapping.items()}
        row.update(A=r['A'],B=pos['point_id'],C=r['B'],H='；'.join(str(r[k]) for k in ['F','G','H'] if r.get(k)),facilitySource=r.get('K'))
        output.append(row)
    # Old sheet is used only as a stable identity lookup for duplicate addresses.
    _,old=read_source('行人信息总表（0905）');oldbyseq={r['A']:r for r in old[1:] if r.get('A')}
    pm=dict(zip('A D E G H I J K L M N O P Q R S T U V W X Y AB AC AD AE'.split(), 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()))
    people=[{k:praw[0].get(v) for k,v in pm.items()}]
    for r in praw[1:]:
        if not r.get('A') or not r.get('B'):continue
        matches=byaddress.get(r['B'],[])
        if len(matches)==1:pid=matches[0]['point_id']
        else:
            prior=oldbyseq.get(r['A']);assert prior and prior['D']==r['B'] and prior['E']==r['C'],('Ambiguous node',r['A'])
            pid=prior['C']
        row={k:r.get(v) for k,v in pm.items()};row.update(B='ped-'+str(r['A']),C=pid);people.append(row)
    return output,people
