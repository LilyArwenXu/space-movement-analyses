from build_data import ROOT,read_source
import json,re
from urllib.parse import urlsplit
data=json.loads((ROOT/'spacemovement/survey-data.js').read_text(encoding='utf-8').removeprefix('window.SURVEY = ').strip().rstrip(';'))
_,raw=read_source()
source=[r for r in raw[3:] if isinstance(r.get('C'),str) and r['C'].strip()]
assert len(source)==len(data['rows'])==135
assert len({r['C'].strip() for r in source})==len(data['nodes'])==133
for key in ['AU','AV','AX','AY','BA','BB']:
    assert sum(r.get(key,0) or 0 for r in source)==sum(r.get(key,0) or 0 for r in data['nodes'])
assert all(r['rho'] is None for r in data['correlations'] if r['y'] in ['BR','BS'])
matrix=data['matrixCorrelations']
assert len(matrix)==len(data['matrixFields'])*(len(data['matrixFields'])+1)//2
for pair in data['correlations']:
    if pair['rho'] is None: continue
    match=next(m for m in matrix if {m['x'],m['y']}=={pair['x'],pair['y']})
    assert abs(match['rho']-pair['rho'])<1e-12 and match['n']==pair['n']
for html in (ROOT/'dist').rglob('*.html'):
    for url in re.findall(r'(?:href|src)="([^"]+)"',html.read_text(encoding='utf-8')):
        if url.startswith(('http','#','data:')):continue
        assert (html.parent/urlsplit(url).path).exists(),(html,url)
for name in ['studies.js','studies.css','survey-data.js','echarts.min.js']:
    assert (ROOT/'spacemovement'/name).read_bytes()==(ROOT/'dist/spacemovement'/name).read_bytes()
print('Source record counts, address aggregation, six behavior totals, missing metrics, local links and published-directory copies verified.')
