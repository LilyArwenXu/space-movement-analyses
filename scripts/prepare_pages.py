"""Prepare a self-contained GitHub Pages folder from the built static site."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def prepare():
    source=ROOT/'dist'
    target=ROOT/'docs'
    target.mkdir(exist_ok=True)
    for name in ['index.html','visualizations.html','behavior-analysis.html','LICENSE.txt']:
        shutil.copy2(source/name,target/name)
    for name in ['assets','spacemovement']:
        shutil.copytree(source/name,target/name,dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('sass','*.xlsx','*.docx','*.py','__pycache__'))
    (target/'.nojekyll').write_text('',encoding='utf-8')
    verify(target)
    archive=ROOT/'.site-build/github-pages.zip'
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(target.rglob('*')):
            if file.is_file():z.write(file,file.relative_to(target).as_posix())
    print('Prepared docs/ and .site-build/github-pages.zip')

def verify(folder):
    count=0
    def check(file,url):
        nonlocal count
        parsed=urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:return
        assert not parsed.path.startswith('/'),f'Root-relative URL breaks project Pages: {file}: {url}'
        dest=(file.parent/unquote(parsed.path)).resolve()
        assert dest.is_relative_to(folder.resolve()),f'Link escapes publishing folder: {url}'
        assert dest.is_file(),f'Missing resource: {file}: {url}'
        relative=dest.relative_to(folder.resolve())
        parent=folder
        for part in relative.parts:
            assert part in [p.name for p in parent.iterdir()],f'Filename case mismatch: {url}'
            parent=parent/part
        count+=1
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for key,val in attrs:
                if key in ['src','href'] and val:check(self.file,val)
    for file in folder.rglob('*.html'):
        parser=Links();parser.file=file;parser.feed(file.read_text(encoding='utf-8-sig'))
    for file in folder.rglob('*.css'):
        for url in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)',file.read_text(encoding='utf-8')):
            check(file,url)
    assert (folder/'index.html').is_file()
    directory=(folder/'visualizations.html').read_text(encoding='utf-8')
    routes=re.findall(r'href="(spacemovement/[^"]+\.html)"',directory)
    assert len(routes)==len(set(routes))==14
    print(f'Verified {count} local HTML/CSS resource links, exact filename case, and all {len(routes)} chart pages.')

if __name__=='__main__':prepare()
