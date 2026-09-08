"""Check case provenance and missing-data behavior against the actual CSVs."""
from build_data import ROOT
from case_analysis import analyze, number
import csv,json,math

data=json.loads((ROOT/'docs/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].rstrip(';\n'))
assert 'caseCorrelations' not in data and 'predictionCritical' not in data
count=0
for kind,cases in data['cases'].items():
    for case in cases:
        def read(url):
            path=ROOT/'docs/spacemovement'/url
            with path.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
        nodes,people=map(read,case['csv'])
        actual=case['analysis'];assert actual==analyze(nodes,people,data['caseDimensions'],kind)
        assert actual['nodeCount']==1 and actual['peopleCount']==len(people)
        assert all(r['rho'] is None and r['p'] is None and r['n']<=1 for r in actual['correlations'])
        point=actual['points'][0];assert point['metrics']['sample']==number(nodes[0]['行人样本数'])
        assert point['metrics']['resident'] is None and point['metrics']['visitor'] is None
        assert point['metrics']['identityMix'] is None and point['vitality'] is None and point['mixScore'] is None
        for metric in ['ageMix','activityMix','postureMix','socialMix']:
            value=point['metrics'][metric];assert value is None or -1e-12<=value<=1+1e-12
        assert '0907' not in case['caption'] and '工作簿' not in case['caption']
        count+=1
assert count==11
print('Verified all 11 cases against their own CSVs, node-level sample size, unavailable indices and no full-dataset correlations.')
