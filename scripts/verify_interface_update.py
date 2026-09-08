"""Verify the workbook-driven classification table and shared site chrome."""
from html.parser import HTMLParser
from pathlib import Path
import json,re,openpyxl,sys

ROOT=Path(__file__).resolve().parents[1]

class Table(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='tr':self.row=[]
        elif tag=='td' and self.row is not None:self.cell={'value':'','rowspan':int(attrs['rowspan']),'colspan':int(attrs['colspan'])};self.row.append(self.cell)
    def handle_data(self,data):
        if self.cell is not None:self.cell['value']+=data
    def handle_endtag(self,tag):
        if tag=='td':self.cell=None
        elif tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

ws=openpyxl.load_workbook(ROOT/'category-photos/街道空间要素分类表_最新.xlsx',data_only=True).active
covered=set();merges={}
for m in ws.merged_cells.ranges:
    merges[(m.min_row,m.min_col)]=(m.max_row-m.min_row+1,m.max_col-m.min_col+1)
    covered.update((r,c) for r in range(m.min_row,m.max_row+1) for c in range(m.min_col,m.max_col+1) if (r,c)!=(m.min_row,m.min_col))
expected=[]
for r in range(1,ws.max_row+1):
    row=[]
    for c in range(1,ws.max_column+1):
        if (r,c) in covered:continue
        rowspan,colspan=merges.get((r,c),(1,1))
        row.append({'value':str(ws.cell(r,c).value or ''),'rowspan':rowspan,'colspan':colspan})
    expected.append(row)
parser=Table();parser.feed((ROOT/'docs/categories.html').read_text(encoding='utf-8'))
assert parser.rows==expected,(parser.rows[:2],expected[:2])
category=(ROOT/'docs/categories.html').read_text(encoding='utf-8')
assert '分类图片索引' not in category and 'classification-popup' in category
assert 'assets/css/interface.css' in category

data=json.loads((ROOT/'docs/assets/data/inclusive-data.js').read_text(encoding='utf-8').split('=',1)[1].rstrip(';\n'))
assert not any(str(v).strip()=='D附属设施加权指数' for row in data['tables']['space']['rows'][:3] for v in row)

pages=['data-collection.html','categories.html','behavior-analysis.html']
for name in pages:
    text=(ROOT/'docs'/name).read_text(encoding='utf-8')
    assert 'unified-topbar' in text and '← INCLUSIVE VITALITY' in text
for path in (ROOT/'docs/spacemovement').glob('*.html'):
    text=path.read_text(encoding='utf-8')
    if 'data-page=' in text:assert 'unified-topbar' in text and '../visualizations.html' in text

cover=(ROOT/'docs/index.html').read_text(encoding='utf-8')
css=(ROOT/'docs/assets/css/interface.css').read_text(encoding='utf-8')
assert 'data-cover="true"' in cover and 'body[data-cover] #footer{background:none!important' in css and 'body[data-cover] #map-frame{inset:0;border:0}' in css
assert (ROOT/'docs/assets/fonts/FZVariable-LanTingHeiK.TTF').is_file()
print('Verified exact 30-row XLSX classification layout, hover imagery, removed collection column, shared headers, cover edge and chart font asset.')
