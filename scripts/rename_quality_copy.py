"""One-time terminology migration; preserve resource paths and input columns."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD = '\u754c\u9762\u54c1\u8d28'
NEW = '\u8857\u9053\u54c1\u8d28'


def migrate(text):
    protected = []

    def keep(match):
        protected.append(match.group())
        return f'__QUALITY_RESOURCE_{len(protected)-1}__'

    # These values resolve existing files; changing their spelling breaks images.
    text = re.sub(r'"(?:folder|file|path|src|href|column)"\s*:\s*"[^"\n]*"', keep, text)
    text = re.sub(r'''["'](?:\.\.?[/\\]|(?:assets|result|spacemovement)/)[^"'\n]*["']''', keep, text)
    text = text.replace(OLD, NEW)
    for index, original in enumerate(protected):
        text = text.replace(f'__QUALITY_RESOURCE_{index}__', original)
    return text


if __name__ == '__main__':
    changed = 0
    for folder in ('aerial', 'dist', 'docs', 'spacemovement', 'scripts', 'chart_python/current'):
        for path in (ROOT / folder).rglob('*'):
            if path.suffix not in ('.html', '.js', '.json', '.svg', '.py'):
                continue
            if '跑图代码' in path.parts or path.name == 'shap_revision.py':
                continue
            original = path.read_text(encoding='utf-8')
            updated = migrate(original)
            if updated != original:
                path.write_text(updated, encoding='utf-8')
                changed += 1
    # The SVG is also a source asset copied by subsequent builds.
    svg = ROOT / 'result/shap/intro_logic/algorithm_flowchart_text.svg'
    original = svg.read_text(encoding='utf-8')
    svg.write_text(original.replace(OLD, NEW), encoding='utf-8')
    print(f'Updated terminology in {changed} website/source files and the source SVG.')
