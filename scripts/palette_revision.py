"""Apply the requested chart-only ten-color theme through the existing build."""
import re
from build_data import ROOT

PALETTE=['#cd96be','#c90097','#ff0051','#9c23ad','#9094c1','#6f52d4','#072e55','#0071ee','#4d74a0','#72a9bc']
def renderer(js):
    js=re.sub(r'PALETTE=\[[^\]]+\]', 'PALETTE='+repr(PALETTE),js,count=1)
    js=js.replace('PALETTE[j%7]','PALETTE[j%PALETTE.length]')
    mapping={'#607E95':'#4d74a0','#A8C3D6':'#72a9bc','#B8AEA6':'#9094c1','#E2D0BC':'#cd96be','#F3EEE8':'#cd96be','#D59BA8':'#c90097','#A45668':'#9c23ad','#8C793E':'#6f52d4','#497F73':'#0071ee','#806A96':'#9094c1','#BD7546':'#ff0051'}
    for old,new in mapping.items():js=js.replace(old,new)
    js=js.replace("fill:'#D59BA8'","fill:'#c90097'").replace('rgba(164,86,104,','rgba(156,35,173,').replace('rgba(75,75,75,','rgba(77,116,160,')
    js=re.sub(r'function color\(value\)\{[^\n]+', 'function color(value){return chartScale(value)}',js)
    js=re.sub(r'function correlationColor\(value\)\{[^\n]+', 'function correlationColor(value){return chartScale(value)}',js)
    # Preserve the five-stop heat kernel interpolation while changing its colors.
    js=re.sub(r'colors=\[\[96,126,149\].*?\]\]', 'colors=[[7,30,55],[7,46,85],[111,82,212],[201,0,151],[255,0,81]]',js)
    js=js.replace("['#4d74a0','#9c23ad','#6f52d4','#0071ee','#9094c1','#ff0051']", "['#064b3b','#9c23ad','#6f52d4','#0071ee','#40316b','#ff0051']")
    js=js.replace("蓝色表示人数少，玫红色表示人数多", "墨蓝色表示人数少，洋红色表示人数多")
    js=js.replace("颜色由蓝到玫红表示负相关到正相关，近零为浅色。", "颜色由深蓝到洋红表示负相关到正相关，近零为白色。")
    return js

def pages():
    for p in (ROOT/'aerial').glob('*.html'):
        s=p.read_text(encoding='utf-8')
        if 'final-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/css/final-revision.css"></head>')
        p.write_text(s,encoding='utf-8')
    (ROOT/'aerial/team.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>课程与团队信息</title><link rel="stylesheet" href="assets/css/inclusive.css"><link rel="stylesheet" href="assets/css/interface.css"><link rel="stylesheet" href="assets/css/final-revision.css"></head><body><header class="topbar unified-topbar"><a class="brand" href="index.html">← INCLUSIVE VITALITY</a><h1>课程与团队信息</h1></header><main class="team-information"><section lang="zh-CN"><p>同济大学 | 建筑与城市规划学院</p><h2>衡复容活</h2><p class="team-subtitle">城市活动与社会融合的人因空间驱动力</p><p>指导老师：闫超</p><p>蔡淙旭、常思语、丁文颖、黄希龄、黄子童、李严宇、苏嘉欣、孙靖琪、王霏杨、王倪潇、王一一、徐韵晨</p></section><section lang="en"><p>CAUP, Tongji University</p><h2>Inclusive Vitality</h2><p class="team-subtitle">Socio-Spatial Drivers of Urban Activity and Social Mixing in Fuheng District</p><p>Instructor：Chao Yan</p><p>Congxu Cai, Siyu Chang, Wenying Ding, Xiling Huang, Zitong Huang. Yanyu Li, Jiaxin Su, Jingqi Sun, Feiyang Wang, Nixiao Wang, Yiyi Wang, Yunchen Xu.</p></section></main></body></html>''',encoding='utf-8')
    for folder,prefix in [('aerial','assets/css/'),('aerial/spacemovement','../assets/css/'),('spacemovement','../assets/css/')]:
        for p in (ROOT/folder).glob('*.html'):
            s=p.read_text(encoding='utf-8')
            if 'palette-revision.css' not in s:s=s.replace('</head>',f'<link rel="stylesheet" href="{prefix}palette-revision.css"></head>')
            p.write_text(s,encoding='utf-8')
