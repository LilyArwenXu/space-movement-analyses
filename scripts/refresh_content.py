"""Refresh editable website copy without recomputing statistical datasets."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEAM_HOSTING = '''<section class="team-hosting" aria-label="GitHub 托管信息"><p style="overflow-wrap:anywhere">本网站已托管在Github上<br>
This website is now hosted on GitHub；<br>
网址 Pages：<a href="https://lilyarwenxu.github.io/space-movement-analyses/" style="text-decoration:underline">https://lilyarwenxu.github.io/space-movement-analyses/</a><br>
仓库 Repository：<a href="https://github.com/LilyArwenXu/space-movement-analyses/" style="text-decoration:underline">https://github.com/LilyArwenXu/space-movement-analyses/</a><br>
合作者 Collaborators：徐韵晨 LilyArwenXu、徐韵曦 Yunxi Xu (ArceeXu)</p></section>'''


def add_team_hosting(html):
    if 'class="team-hosting"' not in html:
        html = html.replace('</main>', TEAM_HOSTING + '</main>', 1)
    return html


def refresh():
    from regression_revision import CSS, mismatch_intro_page
    from micro_revision import pages as micro_pages

    micro_pages()
    content = json.loads((ROOT / 'scripts/mismatch_content.json').read_text(encoding='utf-8'))
    current = ROOT / 'aerial/assets/data/mismatch-content.js'
    existing = json.loads(current.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))
    if 'assetVersion' in existing:
        content['assetVersion'] = existing['assetVersion']
    payload = 'window.MISMATCH_CONTENT=' + json.dumps(content, ensure_ascii=False) + ';\n'
    for folder in ('aerial', 'dist', 'docs'):
        site = ROOT / folder
        (site / 'assets/data/mismatch-content.js').write_text(payload, encoding='utf-8')
        (site / 'spacemovement/mismatch_intro.html').write_text(mismatch_intro_page(), encoding='utf-8')
        (site / 'assets/css/regression-revision.css').write_text(CSS, encoding='utf-8')
        team = site / 'team.html'
        team.write_text(add_team_hosting(team.read_text(encoding='utf-8')), encoding='utf-8')
        if folder != 'aerial':
            source = ROOT / 'aerial/behavior-analysis.html'
            (site / 'behavior-analysis.html').write_bytes(source.read_bytes())
    (ROOT / 'spacemovement/mismatch_intro.html').write_text(mismatch_intro_page(), encoding='utf-8')
    print('Updated editable copy, introduction styles and team hosting details in aerial, dist and docs.')


def refresh_algorithm():
    from regression_revision import CSS, mismatch_intro_page

    content = json.loads((ROOT / 'scripts/mismatch_content.json').read_text(encoding='utf-8'))
    algorithm = next(tab for tab in content['intro']['tabs'] if tab['title'] == '算法逻辑')
    # Retain the site's agreed terminology when edited copy uses the former name.
    algorithm = dict(algorithm, text=[line.replace('界面品质', '街道品质') for line in algorithm['text']])
    for folder in ('aerial', 'dist', 'docs'):
        path = ROOT / folder / 'assets/data/mismatch-content.js'
        existing = json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))
        index = next(i for i, tab in enumerate(existing['intro']['tabs']) if tab['title'] == '算法逻辑')
        existing['intro']['tabs'][index] = algorithm
        path.write_text('window.MISMATCH_CONTENT=' + json.dumps(existing, ensure_ascii=False) + ';\n', encoding='utf-8')
        (ROOT / folder / 'spacemovement/mismatch_intro.html').write_text(mismatch_intro_page(), encoding='utf-8')
        (ROOT / folder / 'assets/css/regression-revision.css').write_text(CSS, encoding='utf-8')
    (ROOT / 'spacemovement/mismatch_intro.html').write_text(mismatch_intro_page(), encoding='utf-8')
    print('Updated algorithm copy in aerial, dist and docs.')


if __name__ == '__main__':
    if '--algorithm-only' in sys.argv:
        refresh_algorithm()
    else:
        refresh()
