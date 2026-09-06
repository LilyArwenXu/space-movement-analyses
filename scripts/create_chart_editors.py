"""Create editable snapshots once; never overwrite the user's Python edits."""
from pathlib import Path
from catalog import CATALOG
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'chart_python'
folder.mkdir(exist_ok=True)
for number,(_,route,title,kind) in enumerate(CATALOG,1):
    path=folder/f'{number:02d}_{Path(route).stem}.py'
    if path.exists(): continue
    html=(ROOT/'spacemovement'/route).read_text(encoding='utf-8')
    script='' if kind=='weights' else (ROOT/'spacemovement'/('people-studies.js' if kind=='people' else 'studies.js')).read_text(encoding='utf-8')
    source=('"""'+f'{number:02d} {title}\n修改下方 HTML / JAVASCRIPT 后运行本文件，即同步更新对应网页。\n数据仍读取项目中的最新数据文件；不要修改 SOURCE_SCRIPT。'+ '\n"""\n'
        +'from _export import export_chart\n\n'
        +f'ROUTE = {route!r}\nSOURCE_SCRIPT = '+repr('' if kind=='weights' else 'people-studies.js' if kind=='people' else 'studies.js')+'\n\n'
        +"HTML = r'''"+html+"'''\n\n# 绘图代码：可修改 subtitle、轴名称、series、grid、symbolSize 等设置。\nJAVASCRIPT = r'''"+script+"'''\n\n"
        +"if __name__ == '__main__':\n    export_chart(ROUTE, HTML, JAVASCRIPT, SOURCE_SCRIPT)\n")
    path.write_text(source,encoding='utf-8')
print('Editable Python chart snapshots ready:',len(CATALOG))
