"""Separate population/regression navigation and refresh the SHAP presentation."""
from pathlib import Path
import hashlib
import json
import re
import shutil
from html import escape
from catalog import CATALOG

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    'heat':(1,'人员热力图'), 'composition':(2,'人群构成分析'),
    'correlations':(3,'空间行为相关性分析'), 'mixRegression':(4,'混合度回归分析'),
    'weights':(5,'界面品质回归分析'), 'memory':(6,'空间活力度回归分析'),
    'qualityVitality':(7,'不配得性Ⅰ：高界面品质是否必然带来高空间活力度？'),
    'qualityMix':(8,'不配得性Ⅱ：高界面品质是否必然促进人群的高度混合？'),
    'mismatch':(9,'不配得性Ⅲ：混合度与活力度有何关联特征？'),
}
SHAP_RENDERER = r'''function shapAnalysis(){
 /*
  * 三个“不配得性分析”页面不再根据
  * “高XX低XX / 低XX高XX”切换图片。
  *
  * 根据当前 PAGE，直接选择固定的 SHAP 图片文件夹。
  *
  * qualityVitality → 不配得性Ⅰ
  * qualityMix      → 不配得性Ⅱ
  * mismatch        → 不配得性Ⅲ
  */

 const content=window.SHAP_CAPTIONS;

 // -------------------------------------------------
 // 1. 根据当前页面决定图片文件夹
 // -------------------------------------------------
 const folderMap={
  qualityVitality:'活力度界面品质',
  qualityMix:'混合度界面品质',
  mismatch:'活力度混合度'
 };

 // -------------------------------------------------
// 三个不配得性页面的文字内容
//
// 每个页面有三组文字，分别对应：
// 1.png
// 2.png
// 3.png
//
// description = 上方正文
// conclusion  = 下方结论
// -------------------------------------------------
const textMap={

 qualityVitality:[
  {
   description:'这里填写不配得性Ⅰ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅰ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅰ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅰ第三张图片旁边的结论。'
  }
 ],

 qualityMix:[
  {
   description:'这里填写不配得性Ⅱ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅱ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅱ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅱ第三张图片旁边的结论。'
  }
 ],

 mismatch:[
  {
   description:'这里填写不配得性Ⅲ第一张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第一张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅲ第二张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第二张图片旁边的结论。'
  },
  {
   description:'这里填写不配得性Ⅲ第三张图片旁边的正文。',
   conclusion:'这里填写不配得性Ⅲ第三张图片旁边的结论。'
  }
 ]

};

 const folder=folderMap[PAGE];

 /*
  * 理论上本函数只会在三个不配得性页面中调用。
  * 如果以后代码结构改变，这里可以避免出现错误路径。
  */
 if(!folder){
  note('当前页面没有配置不配得性分析图片。');
  return;
 }

 // -------------------------------------------------
 // 2. 保留原来的标题位置(已经不要啦！)
 // -------------------------------------------------
 

 // -------------------------------------------------
 // 3. 保留原来的图片 + 右侧文字整体布局
 // -------------------------------------------------
 const gallery=el('section','shap-gallery');

 /*
  * 保留原来的文字换行规则。
  */
 const lines=s=>String(s||'')
  .replace(/([；;。])\s*/g,'$1\n')
  .trim();

 // -------------------------------------------------
 // 4. 固定加载 1.png / 2.png / 3.png
 // -------------------------------------------------
 [1,2,3].forEach((number,index)=>{

  // 每一行仍然使用：
  // 左侧图片 + 右侧文字
  const figure=el('figure','shap-figure',gallery);
  const row=el('div','shap-row',figure);

  // 图片
  const img=el('img','shap-image',row);

  /*
   * 最终浏览器路径：
   *
   * ../assets/data/shap/活力度界面品质/1.png
   * ../assets/data/shap/活力度界面品质/2.png
   * ../assets/data/shap/活力度界面品质/3.png
   *
   * 等。
   *
   * regression_revision.py 的 pages() 会自动把
   * result/shap 整个复制到 aerial/assets/data/shap，
   * 所以不需要手工复制图片。
   */
  img.src=
   '../assets/data/shap/'
   +folder
   +'/'
   +number
   +'.png?v='
   +content.assetVersion;

  img.alt=folder+' · '+number+'.png';

  // -------------------------------------------------
  // 5. 右侧文字区域
  // -------------------------------------------------
  const side=el('aside','shap-side',row);

  /*
   * 你目前还没有准备新的文字，
   * 所以这里暂时继续沿用原来的文字数据。
   *
   * 为了避免删除“高低类型切换”之后旧 label 不存在，
   * 这里按照当前页面寻找一组已有文字作为临时内容。
   */

  // 当前图片对应的文字
const text=textMap[PAGE][index];

// 第一段正文
el('p','shap-description',side).textContent=
 lines(text.description);

// 第二段结论
el('p','shap-conclusion',side).textContent=
 lines(text.conclusion);
 });

 note('');
}
'''
CSS = '''.macro-stage.expanded .mismatch-entry{transform:translateX(-200%)}
.mismatch-menu{left:33.333333%}
.critic-method>summary{cursor:pointer;font-size:23px;line-height:1.6;font-weight:400;list-style-position:inside}
.critic-method>summary:focus-visible{outline:2px solid #111;outline-offset:4px}
.critic-method[open]>summary{margin-bottom:24px}.critic-method:not([open]){padding:16px 0}
.shap-side{max-height:none;overflow:visible;padding-right:0}
.shap-side .shap-description{margin:0;white-space:pre-line;font:inherit}
.shap-side .shap-conclusion{margin:26px 0 0;padding-top:18px;border-top:1px solid #ddd;white-space:pre-line;font:inherit}
'''

def renderer(js):
    """
    对最终图表 JavaScript 做构建期修改。

    本函数不会修改“筛选”页面的绘图逻辑。

    本次修改重点：
    三个不配得性页面进入“不配得性分析”后，
    不再出现“高XX低XX / 低XX高XX”的二级切换按钮，
    而是直接展示固定的三张 SHAP 图片。
    """

    # 如果当前图表脚本中根本不存在 shapAnalysis，
    # 则说明不是相关页面，不进行处理。
    if 'function shapAnalysis(label){' not in js:
        return js

    # ---------------------------------------------------------
    # 原有功能：人群构成页面
    # 保持不变
    # ---------------------------------------------------------
    js=re.sub(
        r"if\(PAGE==='composition'\)mainTabs\(\['构成分析','系数表征','混合度总表'\].*?;\n",
        "if(PAGE==='composition')mainTabs(D.mixDimensions.map(d=>d.label),dimensionBars);\n",
        js
    )

    # ---------------------------------------------------------
    # 原有功能：混合度回归分析
    # 保持不变
    # ---------------------------------------------------------
    if "if(PAGE==='mixRegression')" not in js:
        js=js.replace(
            "if(PAGE==='composition')",
            "if(PAGE==='mixRegression')mainTabs(['系数表征','混合度总表'],i=>i?mixedTotal():coefficient('mix'));\n"
            "if(PAGE==='composition')"
        )

    # ---------------------------------------------------------
    # 原有 Critic 内容
    # 保持不变
    # ---------------------------------------------------------
    js=js.replace(
        "el('section','critic-method',box)",
        "el('details','critic-method',box)"
    )

    js=js.replace(
        "el('section','critic-method',NOTE)",
        "el('details','critic-method',NOTE)"
    )

    js=js.replace(
        '<h2>Critic权重算法</h2>',
        '<summary>Critic权重算法</summary>'
    )

    # ---------------------------------------------------------
    # 替换 shapAnalysis()
    #
    # 原 shapAnalysis(label)
    # 会根据 label 选择：
    #
    #   高XX低XX
    #   低XX高XX
    #
    # 现在改成 shapAnalysis()，
    # 根据 PAGE 固定决定文件夹。
    # ---------------------------------------------------------
    start=js.index('function shapAnalysis(label){')
    end=js.index('function mismatchView(i){',start)

    js=js[:start]+SHAP_RENDERER+js[end:]

    # ---------------------------------------------------------
    # 修改“不配得性分析”页面的入口
    #
    # 原来：
    #
    # sectionTabs(labels,j=>shapAnalysis(labels[j]))
    #
    # 会产生高/低分类按钮。
    #
    # 修改以后：
    #
    # shapAnalysis()
    #
    # 直接显示三张图片。
    # ---------------------------------------------------------
    start=js.index('function mismatchView(i){')

    if "if(i){if(PAGE==='mismatch')" in js[start:]:

        js=js[:start]+re.sub(
            r" if\(i\)\{.*?return;\}\n const c=chart\(W,610\)",

            " if(i){shapAnalysis();return;}\n"
            " const c=chart(W,610)",

            js[start:],
            count=1,
            flags=re.S
        )

    return js

def card(route,kind):
    number,title=TITLES[kind]
    group=' regression' if kind in ['mixRegression','weights','memory'] else ''
    return f'<a class="panel{group}" href="spacemovement/{route}" aria-label="{number:02d} {escape(title)}"><span class="panel-spine">{number:02d} / {escape(title)}</span><div class="panel-detail"><span class="panel-number">{number:02d}</span><h2>{escape(title)}</h2><span class="panel-link">OPEN VISUALIZATION ⟶</span></div></a>'

def pages():
    site=ROOT/'aerial'
    inputs=json.loads((ROOT/'scripts/mismatch_captions.json').read_text(encoding='utf-8'))
    marker='/* Updated mismatch III captions */'
    caption=site/'assets/data/shap-captions.js'
    base=caption.read_text(encoding='utf-8').split(marker)[0]
    desc=inputs['descriptions']
    overrides={'高混合度低活力度':[desc['summary'],desc['interaction'],desc['summary']], '高活力度低混合度':[desc['summary'],desc['interaction'],desc['trend']]}
    files=sorted((ROOT/'result/shap').glob('*/*.png'))
    version=hashlib.sha256(b''.join(hashlib.sha256(f.read_bytes()).digest() for f in files)).hexdigest()[:12]
    base+='\n'+marker+'\nObject.assign(window.SHAP_CAPTIONS.groups,'+json.dumps(inputs['groups'],ensure_ascii=False)+');\nwindow.SHAP_CAPTIONS.descriptionOverrides='+json.dumps(overrides,ensure_ascii=False)+';\nwindow.SHAP_CAPTIONS.assetVersion='+json.dumps(version)+';\n'
    caption.write_text(base,encoding='utf-8')
    shutil.copytree(ROOT/'result/shap',site/'assets/data/shap',dirs_exist_ok=True)
    # All chart snapshots share the same functions and branch on data-page.
    for file in (site/'assets/js').glob('chart-*.js'):
        file.write_text(renderer(file.read_text(encoding='utf-8')),encoding='utf-8')
    shutil.copy2(site/'assets/js/chart-03.js',site/'assets/js/chart-10.js')
    template=(site/'spacemovement/people_composition.html').read_text(encoding='utf-8')
    (site/'spacemovement/mixing_regression.html').write_text(template.replace('data-page="composition"','data-page="mixRegression"').replace('chart-03.js','chart-10.js'),encoding='utf-8')
    (site/'assets/css/regression-revision.css').write_text(CSS,encoding='utf-8')
    for _,route,_,kind in CATALOG:
        path=site/'spacemovement'/route;s=path.read_text(encoding='utf-8');number,title=TITLES[kind]
        s=re.sub(r'<title>.*?</title>',f'<title>{escape(title)}｜Inclusive Vitality</title>',s)
        s=re.sub(r'<h1>.*?</h1>',f'<h1>{number:02d} {escape(title)}</h1>',s)
        if 'regression-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="../assets/css/regression-revision.css"></head>')
        path.write_text(s,encoding='utf-8')
        shutil.copy2(path,ROOT/'spacemovement'/route)
    path=site/'visualizations.html';s=path.read_text(encoding='utf-8')
    ordered=sorted(CATALOG,key=lambda entry:TITLES[entry[3]][0]);cards=[card(route,kind) for _,route,_,kind in ordered]
    main='<main class="macro-stage"><div class="accordion">'+''.join(cards[:6])+'<button class="panel mismatch-entry" aria-expanded="false" aria-controls="mismatch-menu"><span class="panel-spine">07–09 / 不配得性分析</span><div class="panel-detail"><span class="panel-number">07–09</span><h2>不配得性分析</h2><span class="panel-link">展开分析 ⟶</span></div></button></div><section id="mismatch-menu" class="mismatch-menu" inert><button class="menu-back">← 返回全部分析</button>'+''.join(cards[6:])+'</section></main>'
    s=re.sub(r'<main\b.*?</main>',lambda _:main,s,flags=re.S).replace('08 STUDIES','09 STUDIES')
    if 'regression-revision.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/css/regression-revision.css"></head>')
    path.write_text(s,encoding='utf-8')
    for name in ['data-extract.csv','data_extract.csv']:
        shutil.copy2(ROOT/name,site/'assets/data'/name)

def refresh():
    from final_revision import revise
    path=ROOT/'aerial/assets/data/inclusive-data.js'
    data=json.loads(path.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    revise(data)
    path.write_text('window.INCLUSIVE='+json.dumps(data,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8')
    pages()
    from sync_static import copy_static
    shutil.copytree(ROOT/'aerial',ROOT/'dist',dirs_exist_ok=True,copy_function=copy_static)
    from prepare_pages import prepare
    prepare()
    print(json.dumps({'scoreMeans':data['scoreMeans'],'groupCounts':{kind:{label:sum(p['mismatchGroups'][kind]==label for p in data['points']) for label in sorted({p['mismatchGroups'][kind] for p in data['points'] if p['mismatchGroups'][kind]})} for kind in ['qualityVitality','qualityMix','mismatch']}},ensure_ascii=False))

if __name__=='__main__':refresh()
