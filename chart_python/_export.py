"""Shared local exporter. No third-party dependency required for styling edits."""
from pathlib import Path
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]

def export_chart(route, html, javascript, source_script, sync=True):
    target=ROOT/'spacemovement'/route
    if source_script:
        html=html.replace(f'<script src="{source_script}"></script>', '<script>\n'+javascript.replace('</script>', '<\\/script>')+'\n</script>')
    else:
        # Always use the newest computed weights, not the snapshot's old values.
        current=target.read_text(encoding='utf-8')
        data=re.search(r'const resData = .*?;',current).group(0)
        html=re.sub(r'const resData = .*?;',lambda _:data,html,count=1)
    target.write_text(html,encoding='utf-8',newline='\n')
    if sync:
        for directory in ['aerial','dist','docs']:
            dest=ROOT/directory/'spacemovement'
            dest.mkdir(parents=True,exist_ok=True)
            for path in (ROOT/'spacemovement').iterdir():
                if path.suffix in {'.js','.css'} or path.name==route:
                    shutil.copy2(path,dest/path.name)
        sys.path.insert(0,str(ROOT/'scripts'))
        from prepare_pages import prepare
        prepare()
        print('Updated:',target)

def apply_all():
    import runpy
    for path in sorted(Path(__file__).parent.glob('[0-9][0-9]_*.py')):
        config=runpy.run_path(str(path))
        export_chart(config['ROUTE'],config['HTML'],config['JAVASCRIPT'],config['SOURCE_SCRIPT'],sync=False)
