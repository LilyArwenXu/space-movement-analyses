"""Load authoritative SHAP scores after validating their observation order."""
import csv
import math
import shutil
from build_data import ROOT

SOURCES = [('vitality', 'four.csv', '活力度'), ('mixScore', 'mixing_scores.csv', '混合度'), ('quality', 'gua.csv', '界面品质')]

def load_scores(data):
    source = ROOT / 'result/shap'
    data['scoreSources'] = {}
    for key, filename, column in SOURCES:
        with (source / filename).open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == len(data['points']), (filename, 'observation count mismatch')
        columns = list(rows[0])
        fields = ['M','S','R','AE','AF','AG','Y','Z','AA','U','V'] if key == 'quality' else ['sample','clusters','density','gather']
        for index, (row, point) in enumerate(zip(rows, data['points'])):
            original = point['values'] if key == 'quality' else point['metrics']
            for col, field in zip(columns, fields):
                actual = float(row[col]) if row[col] else math.nan
                expected = original.get(field)
                # Supplied CSVs explicitly encode missing workbook inputs as zero.
                assert (expected is None and (actual == 0 or not math.isfinite(actual))) or (expected is not None and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-10)), (filename, index+2, col, actual, expected)
            score = float(row[column]) if row[column] else math.nan
            point[key] = score if math.isfinite(score) else None
            point.setdefault('scoreSourceRows', {})[key] = index + 2
        scores = [float(row[column]) for row in rows if row[column] and math.isfinite(float(row[column]))]
        data['scoreSources'][key] = {'file': 'result/shap/'+filename, 'column': column, 'count': len(scores), 'mean': math.fsum(scores)/len(scores)}
    for point in data['points']:
        point['vitalityRaw'] = point['vitality']
    data['qualityRule'] = '直接使用 result/shap/gua.csv 的界面品质原始评分，不额外缩放'

def pages():
    shutil.copytree(ROOT/'result/shap', ROOT/'aerial/assets/data/shap', dirs_exist_ok=True)
    for folder in ['aerial/spacemovement', 'spacemovement']:
        for route in ['quality_vitality.html','quality_mixing.html','vitality_mixing.html']:
            path=ROOT/folder/route
            s=path.read_text(encoding='utf-8')
            s=s.replace('</head>', '<link rel="stylesheet" href="../assets/css/shap-analysis.css"><script src="../assets/data/shap-captions.js"></script></head>')
            path.write_text(s, encoding='utf-8')
