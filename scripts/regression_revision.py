"""
Separate population/regression navigation
and refresh the mismatch / SHAP presentation.

主要功能：
1. 保留原有 01-09 页面及筛选逻辑。
2. 在“不配得性分析”子菜单中增加：
   “什么是不配得性？”
3. “什么是不配得性？”包含：
   - 研究目的
   - 算法逻辑
   - 读图概述
4. 不配得性Ⅰ、Ⅱ、Ⅲ：
   - “筛选”保持原逻辑不变
   - “不配得性分析”从 mismatch_content.json 读取内容
   - 图片和文字均可自由增删、修改、排序
5. mismatch_content.json 中的内容会被转换成：
   aerial/assets/data/mismatch-content.js
   供浏览器读取。
"""

from pathlib import Path
import hashlib
import json
import re
import shutil
from html import escape

from catalog import CATALOG


# ============================================================
# 基本路径
# ============================================================

ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# 页面标题
# ============================================================

TITLES = {
    'heat': (
        1,
        '人员热力图'
    ),

    'composition': (
        2,
        '人群构成分析'
    ),

    'correlations': (
        3,
        '空间行为相关性分析'
    ),

    'mixRegression': (
        4,
        '混合度回归分析'
    ),

    'weights': (
        5,
        '界面品质回归分析'
    ),

    'memory': (
        6,
        '空间活力度回归分析'
    ),

    'qualityVitality': (
        7,
        '不配得性Ⅰ：高界面品质是否必然带来高空间活力度？'
    ),

    'qualityMix': (
        8,
        '不配得性Ⅱ：高界面品质是否必然促进人群的高度混合？'
    ),

    'mismatch': (
        9,
        '不配得性Ⅲ：混合度与活力度有何关联特征？'
    ),
}


# ============================================================
# 不配得性Ⅰ、Ⅱ、Ⅲ：
# “不配得性分析”页面的浏览器端渲染函数
#
# 注意：
# 这里不再直接写正文。
#
# 所有图片、正文、结论都从：
#
# scripts/mismatch_content.json
#
# 读取。
# ============================================================

SHAP_RENDERER = r'''function shapAnalysis(){

 const all=window.MISMATCH_CONTENT;

 if(!all || !all.analysis){
  note('未找到不配得性内容配置。');
  return;
 }

 const config=all.analysis[PAGE];

 if(!config){
  note('当前页面没有配置不配得性分析内容。');
  return;
 }


 /*
  * ==========================================================
  * 整个图片区
  * ==========================================================
  */

 const gallery=el(
  'section',
  'shap-gallery'
 );

 /*
  * 直接写内联样式。
  *
  * 不再依赖旧项目里的 .shap-gallery CSS，
  * 防止原有样式把新布局覆盖。
  */
 gallery.style.cssText=`
  display:block !important;
  width:100% !important;
  max-width:none !important;
  margin:0 !important;
  padding:0 !important;
 `;


 /*
  * ==========================================================
  * JSON 文字转换
  * ==========================================================
  *
  * 支持：
  *
  * "description":"普通字符串"
  *
  * 以及：
  *
  * "description":[
  *   "第一行",
  *   "第二行",
  *   "",
  *   "第四行"
  * ]
  */

 const lines=s=>{

  if(Array.isArray(s)){
   return s.join('\n');
  }

  return String(s||'').trim();

 };


 /*
  * ==========================================================
  * 根据 mismatch_content.json 创建所有图片
  * ==========================================================
  */

 (config.items||[]).forEach(
  (item,index)=>{


   /*
    * --------------------------------------------------------
    * 每一张图的总容器
    * --------------------------------------------------------
    */

   const figure=el(
    'figure',
    'shap-figure',
    gallery
   );


   figure.style.cssText=`
    box-sizing:border-box !important;
    display:block !important;
    width:100% !important;
    max-width:none !important;
    margin:0 0 72px 0 !important;
    padding:0 0 72px 0 !important;
    border-bottom:1px solid #dedede !important;
   `;


   /*
    * 最后一张图不要底部横线和额外空白。
    */
   if(
    index===
    (config.items||[]).length-1
   ){

    figure.style.marginBottom=
     '0';

    figure.style.paddingBottom=
     '0';

    figure.style.borderBottom=
     '0';

   }


   /*
    * --------------------------------------------------------
    * 图文容器
    * --------------------------------------------------------
    */

   const row=el(
    'div',
    'shap-row',
    figure
   );


   /*
    * ========================================================
    * full
    *
    * 图片占满整行；
    * 正文和结论在图片下面。
    * ========================================================
    */

   if(item.layout==='full'){

    figure.classList.add(
     'shap-figure-full'
    );

    row.classList.add(
     'shap-row-full'
    );


    row.style.cssText=`
     box-sizing:border-box !important;
     display:block !important;
     width:100% !important;
     max-width:none !important;
     margin:0 !important;
     padding:0 !important;
    `;

   }


   /*
    * ========================================================
    * side
    *
    * 默认：
    *
    * 左边图片；
    * 右边正文。
    * ========================================================
    */

   else{

    figure.classList.add(
     'shap-figure-side'
    );

    row.classList.add(
     'shap-row-side'
    );


    row.style.cssText=`
     box-sizing:border-box !important;
     display:grid !important;
     grid-template-columns:
      minmax(0,58%)
      minmax(0,1fr) !important;
     column-gap:42px !important;
     align-items:start !important;
     width:100% !important;
     max-width:none !important;
     margin:0 !important;
     padding:0 !important;
    `;

   }


   /*
    * --------------------------------------------------------
    * 图片
    * --------------------------------------------------------
    */

   let img=null;


   if(item.image){

    img=el(
     'img',
     'shap-image',
     row
    );


    img.src=
     '../assets/data/shap/'
     +config.folder
     +'/'
     +item.image
     +'?v='
     +(all.assetVersion||'');


    img.alt=
     config.folder
     +' · '
     +item.image;


    /*
     * full 图片：
     *
     * 真正强制占满所在内容区。
     */

    if(item.layout==='full'){

     img.style.cssText=`
      box-sizing:border-box !important;
      display:block !important;
      width:100% !important;
      max-width:none !important;
      height:auto !important;
      object-fit:contain !important;
      margin:0 !important;
      padding:0 !important;
     `;

    }


    /*
     * side 图片：
     *
     * 占左边这一列的 100%。
     */

    else{

     img.style.cssText=`
      box-sizing:border-box !important;
      display:block !important;
      width:100% !important;
      max-width:100% !important;
      height:auto !important;
      object-fit:contain !important;
      margin:0 !important;
      padding:0 !important;
     `;

    }

   }


   /*
    * --------------------------------------------------------
    * 正文容器
    * --------------------------------------------------------
    */

   const side=el(
    'aside',
    'shap-side',
    row
   );


   /*
    * full：
    *
    * 因为 row 是 block，
    * aside 自然位于图片下方。
    */

   if(item.layout==='full'){

    side.style.cssText=`
     box-sizing:border-box !important;
     display:block !important;
     width:100% !important;
     max-width:none !important;
     height:auto !important;
     max-height:none !important;
     overflow:visible !important;
     margin:32px 0 0 0 !important;
     padding:0 !important;
    `;

   }


   /*
    * side：
    *
    * 正文占右边列。
    */

   else{

    side.style.cssText=`
     box-sizing:border-box !important;
     display:block !important;
     width:100% !important;
     max-width:none !important;
     height:auto !important;
     max-height:none !important;
     overflow:visible !important;
     margin:0 !important;
     padding:0 !important;
    `;

   }


   /*
    * --------------------------------------------------------
    * 读图
    * --------------------------------------------------------
    */

   if(item.description){
    const details=el('details','shap-reading',side);
    el('summary','mini-heading',details).textContent=item.descriptionTitle||'读图';
    el('p','shap-description caption',details).textContent=lines(item.description);
   }0


   /*
    * --------------------------------------------------------
    * 结论
    * --------------------------------------------------------
    */

   if(item.conclusion){

    const conclusion=el(
     'p',
     'shap-conclusion',
     side
    );


    conclusion.textContent=
     lines(item.conclusion);


    conclusion.style.cssText=`
     box-sizing:border-box !important;
     display:block !important;
     width:100% !important;
     max-width:none !important;
     margin:26px 0 0 0 !important;
     padding:18px 0 0 0 !important;
     border-top:1px solid #dddddd !important;
     white-space:pre-line !important;
     font:inherit !important;
     line-height:1.8 !important;
    `;

   }

  }
 );


 /*
  * 页面顶部原来的说明区域清空。
  */
 note('');

}

/* Three horizontal, button-driven analysis groups. */
function shapAnalysis(){
 const all=window.MISMATCH_CONTENT,config=all&&all.analysis&&all.analysis[PAGE];
 if(!config){note('当前页面没有配置不配得性分析内容。');return;}
 const gallery=el('section','shap-gallery mismatch-slides');
 const tabs=el('nav','subtabs mismatch-analysis-tabs',gallery);tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','不配得性分析方式');
 const text=value=>Array.isArray(value)?value.join('\n'):String(value||'').trim();
 const draw=(host,item)=>{
  const figure=el('figure','shap-figure',host),row=el('div','shap-row',figure);
  row.classList.add(item.layout==='full'?'shap-row-full':'shap-row-side');
  const image=el('img','shap-image',row);image.src='../assets/data/shap/'+config.folder+'/'+item.image+'?v='+(all.assetVersion||'');image.alt=config.folder+' · '+item.image;
  const side=el('aside','shap-side',row);
  if(item.description){const details=el('details','shap-reading',side);el('summary','mini-heading',details).textContent=item.descriptionTitle||'读图';el('p','shap-description caption',details).textContent=text(item.description);}
  const conclusion=el('p','shap-conclusion',side);conclusion.textContent=text(item.conclusion);
 };
 const labels=['单指标分析','多指标组合筛选','联合效应影响'];
 (config.groups||[[0,1],[2,3],[4,6,5]]).forEach((indexes,groupIndex)=>{
  const tab=el('button','',tabs);tab.type='button';tab.textContent=labels[groupIndex];tab.setAttribute('role','tab');
  const group=el('section','mismatch-slide-group',gallery),stage=el('div','mismatch-slide-stage',group),back=el('button','mismatch-slide-button mismatch-slide-back',stage),viewport=el('div','mismatch-slide-viewport',stage),track=el('div','mismatch-slide-track',viewport),more=el('button','mismatch-slide-button mismatch-slide-more',stage);
  group.setAttribute('role','tabpanel');group.hidden=groupIndex!==0;tab.setAttribute('aria-selected',String(groupIndex===0));
  indexes.forEach(index=>{const panel=el('div','mismatch-slide',track);draw(panel,config.items[index]);});
  back.type=more.type='button';back.textContent='BACK';more.textContent='MORE';back.setAttribute('aria-label','返回上一张图');more.setAttribute('aria-label','查看下一张图');
  let active=0;const update=()=>{track.style.transform='translateX('+(-active*100)+'%)';back.hidden=active===0;more.hidden=active===indexes.length-1;stage.classList.toggle('is-first',active===0);stage.classList.toggle('is-last',active===indexes.length-1);};
  back.onclick=()=>{active--;update();};more.onclick=()=>{active++;update();};update();
  tab.onclick=()=>{[...gallery.querySelectorAll('.mismatch-slide-group')].forEach((panel,index)=>panel.hidden=index!==groupIndex);[...tabs.querySelectorAll('[role=tab]')].forEach((button,index)=>button.setAttribute('aria-selected',String(index===groupIndex)));};
 });
 note('');
}
'''


# ============================================================
# 页面附加 CSS
# ============================================================

CSS = r'''
/* ==========================================================
   不配得性入口
   ========================================================== */

.macro-stage.expanded .mismatch-entry{
 transform:translateX(-200%);
}

.mismatch-menu{
 left:33.333333%;
}


/* ==========================================================
   Critic
   ========================================================== */

.critic-method>summary{
 cursor:pointer;
 font-size:23px;
 line-height:1.6;
 font-weight:400;
 list-style-position:inside;
}

.critic-method>summary:focus-visible{
 outline:2px solid #111;
 outline-offset:4px;
}

.critic-method[open]>summary{
 margin-bottom:24px;
}

.critic-method:not([open]){
 padding:16px 0;
}


/* ==========================================================
   “什么是不配得性？”入口
   ========================================================== */

.mismatch-intro-card .panel-detail h2{
 max-width:90%;
}


/* ==========================================================
   SHAP 总区域
   ========================================================== */

.shap-gallery{
 display:block !important;
 width:100% !important;
 max-width:none !important;
}


/*
 * figure 的 margin 默认值清除。
 */
.shap-gallery figure{
 box-sizing:border-box;
}


/*
 * 图片不要受浏览器默认 inline-image 基线影响。
 */
.shap-gallery img{
 display:block;
 height:auto;
}


/*
 * JSON 数组中的换行正常显示。
 */
.shap-description,
.shap-conclusion{
 white-space:pre-line;
}


/* ==========================================================
   手机 / 小屏幕
   ========================================================== */

@media(max-width:900px){

 /*
  * 即使是 side，
  * 小屏幕也改成上下排列。
  */

 .shap-row-side{
  display:block !important;
 }


 .shap-row-side .shap-image{
  width:100% !important;
  max-width:100% !important;
 }


 .shap-row-side .shap-side{
  width:100% !important;
  margin-top:28px !important;
 }

}
/* Reuse shared navigation and subtitle typography for the reading guides. */
.mismatch-intro-page{padding-top:24px}
.mismatch-intro-text{font-size:17px;line-height:1.9}
.mismatch-intro-image{display:block;width:100%;height:auto;margin:0 0 32px}
.mismatch-intro-copy{max-width:960px;overflow-wrap:anywhere}.mismatch-intro-copy p{margin:0 0 18px}.mismatch-intro-copy .mini-heading{margin:34px 0 18px;font-weight:700}.mismatch-intro-copy .mismatch-intro-spacer{height:8px;margin:0}
.shap-reading{white-space:normal}
.shap-reading>summary{cursor:pointer;line-height:1.8;list-style-position:inside;margin:0}
.shap-reading>summary:focus-visible{outline:2px solid var(--ink);outline-offset:4px}
.shap-reading .shap-description{margin:16px 0 0;overflow-wrap:anywhere}

.mismatch-slides{display:grid;gap:28px}.mismatch-analysis-tabs{margin:0 0 20px}
.mismatch-slide-group{border-bottom:1px solid #dedede;padding-bottom:48px}
.mismatch-slide-stage{display:grid;grid-template-columns:42px minmax(0,1fr) 42px;gap:14px;align-items:stretch}.mismatch-slide-stage.is-first{grid-template-columns:minmax(0,1fr) 42px}.mismatch-slide-stage.is-last{grid-template-columns:42px minmax(0,1fr)}
.mismatch-slide-viewport{min-width:0;overflow:hidden}
.mismatch-slide-track{display:flex;transition:transform .42s ease}
.mismatch-slide{flex:0 0 100%;min-width:0}
.mismatch-slide .shap-figure{border:0;padding:0;margin:0}
.mismatch-slide .shap-row-side{display:grid;grid-template-columns:minmax(0,58%) minmax(0,1fr);gap:42px;align-items:start}
.mismatch-slide .shap-row-full{display:block}.mismatch-slide .shap-row-full .shap-side{margin-top:32px}
.mismatch-slide .shap-image{display:block;width:100%;height:auto}.mismatch-slide .shap-conclusion{white-space:pre-line;line-height:1.8}
.mismatch-slide-button{width:42px;border:1px solid #222;background:#fff;color:#222;letter-spacing:.08em;writing-mode:vertical-rl}.mismatch-slide-button:hover{background:#222;color:#fff}
@media(max-width:800px){.mismatch-slide-stage{grid-template-columns:1fr;gap:12px}.mismatch-slide .shap-row-side{grid-template-columns:1fr;gap:24px}.mismatch-slide-button{writing-mode:initial;width:auto;min-height:38px;padding:8px 16px}.mismatch-slide-back{grid-row:2;justify-self:start}.mismatch-slide-more{grid-row:3;justify-self:end}}

'''


# ============================================================
# “什么是不配得性？”说明页面
#
# 页面内容来自 mismatch_content.json。
#
# 用户已经建立：
#
# aerial/spacemovement/mismatch_intro.html
#
# 但每次 build 时本函数会重新生成它，
# 因此以后不要手工修改该 HTML 的正文。
#
# 正文统一修改：
#
# scripts/mismatch_content.json
# ============================================================

def mismatch_intro_page():
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>什么是不配得性？｜Inclusive Vitality</title>
<link rel="stylesheet" href="../assets/css/inclusive.css">
<link rel="stylesheet" href="../assets/css/interface.css">
<link rel="stylesheet" href="../assets/css/final-revision.css">
<link rel="stylesheet" href="../assets/css/palette-revision.css">
<link rel="stylesheet" href="../assets/css/interaction-revision.css">
<link rel="stylesheet" href="../assets/css/regression-revision.css">
</head>
<body data-page="mismatchIntro">
<header class="topbar unified-topbar">
<a class="brand" href="../visualizations.html">← INCLUSIVE VITALITY</a>
<h1 id="mismatch-intro-title">什么是不配得性？</h1>
<span class="meta"></span>
</header>
<nav class="tabs" id="mismatch-intro-tabs" role="tablist" aria-label="不配得性介绍"></nav>
<main class="workspace mismatch-intro-page">
<section class="mismatch-intro-text" id="mismatch-intro-text"></section>
</main>
<script src="../assets/data/mismatch-content.js"></script>
<script>
(function(){
 const content=(window.MISMATCH_CONTENT||{}).intro||{};
 const title=document.getElementById('mismatch-intro-title');
 const tabs=document.getElementById('mismatch-intro-tabs');
 const text=document.getElementById('mismatch-intro-text');
 title.textContent=content.title||'什么是不配得性？';

 // Use the same tab controls for the introduction and its seven reading guides.
 function makeTabs(nav,host,items,prefix){
  function select(index){
   render(items[index],host);
   host.setAttribute('aria-labelledby',prefix+'-'+index);
   Array.from(nav.children).forEach((button,i)=>{
    button.classList.toggle('active',i===index);
    button.setAttribute('aria-selected',String(i===index));
    button.tabIndex=i===index?0:-1;
   });
  }
  host.id=prefix+'-panel';
  host.setAttribute('role','tabpanel');
  items.forEach((item,index)=>{
   const button=document.createElement('button');
   button.type='button';
   button.id=prefix+'-'+index;
   button.textContent=item.title||('选项 '+(index+1));
   button.setAttribute('role','tab');
   button.setAttribute('aria-controls',host.id);
   button.addEventListener('click',()=>select(index));
   button.addEventListener('keydown',event=>{
    let next=index;
    if(event.key==='ArrowRight')next=(index+1)%items.length;
    else if(event.key==='ArrowLeft')next=(index+items.length-1)%items.length;
    else if(event.key==='Home')next=0;
    else if(event.key==='End')next=items.length-1;
    else return;
    event.preventDefault();
    select(next);
    nav.children[next].focus();
   });
   nav.appendChild(button);
  });
  if(items.length)select(0);
 }
 function render(item,host){
  host.replaceChildren();
  if(item.image){
   const image=document.createElement('img');
   image.className='mismatch-intro-image';
   image.src=item.image;
   image.alt=item.imageAlt||item.title||'';
   image.loading='lazy';
   image.decoding='async';
   host.appendChild(image);
  }
  if(item.tabs){
   const nav=document.createElement('nav');
   nav.className='subtabs';
   nav.setAttribute('role','tablist');
   nav.setAttribute('aria-label','读图类型');
   const panel=document.createElement('section');
   host.append(nav,panel);
   makeTabs(nav,panel,item.tabs,'mismatch-reading');
  }else{
   if(item.heading){
    const heading=document.createElement('h2');
    heading.className='mini-heading';
    heading.textContent=item.heading;
    host.appendChild(heading);
   }
   const copy=document.createElement('div');
   copy.className='mismatch-intro-copy';
   const lines=Array.isArray(item.text)?item.text:[item.text||''];
   const headings=new Set(item.headings||[]);
   lines.forEach((line,index)=>{
    const node=document.createElement(headings.has(index)?'h2':'p');
    node.textContent=line;
    if(headings.has(index))node.className='mini-heading';
    if(!line)node.classList.add('mismatch-intro-spacer');
    copy.appendChild(node);
   });
   host.appendChild(copy);
  }
 }
 makeTabs(tabs,text,content.tabs||[],'mismatch-intro');
})();
</script>
</body>
</html>
'''


# ============================================================
# 修改各 chart-xx.js
# ============================================================

def renderer(js):
    """
    对最终图表 JavaScript 做构建期修改。

    重点：

    1. 保持“筛选”页面原来的逻辑。

    2. 不配得性Ⅰ、Ⅱ、Ⅲ进入
       “不配得性分析”后，
       直接调用 shapAnalysis()。

    3. 不再出现：
       “高XX低XX / 低XX高XX”
       二级切换。

    4. shapAnalysis() 的图片和文字
       从 mismatch_content.json 读取。

    5. 同时兼容：
       function shapAnalysis(label){
       和
       function shapAnalysis(){

       这样已经 build 过一次以后，
       再修改本文件继续 build，
       renderer 仍然能够正确覆盖。
    """


    # --------------------------------------------------------
    # 找到现有 shapAnalysis
    #
    # 兼容：
    #
    # function shapAnalysis(label){
    #
    # 以及已经被我们改过的：
    #
    # function shapAnalysis(){
    # --------------------------------------------------------

    match=re.search(
        r'function\s+shapAnalysis\s*\([^)]*\)\s*\{',
        js
    )


    if not match:
        return js


    # --------------------------------------------------------
    # 原有功能：
    # 人群构成页面
    # --------------------------------------------------------

    js=re.sub(
        r"if\(PAGE==='composition'\)mainTabs\(\['构成分析','系数表征','混合度总表'\].*?;\n",
        "if(PAGE==='composition')mainTabs(D.mixDimensions.map(d=>d.label),dimensionBars);\n",
        js
    )


    # --------------------------------------------------------
    # 原有功能：
    # 混合度回归分析
    # --------------------------------------------------------

    if "if(PAGE==='mixRegression')" not in js:

        js=js.replace(

            "if(PAGE==='composition')",

            "if(PAGE==='mixRegression')"
            "mainTabs("
            "['系数表征','混合度总表'],"
            "i=>i?mixedTotal():coefficient('mix')"
            ");\n"
            "if(PAGE==='composition')"

        )


    # --------------------------------------------------------
    # 原有 Critic 内容
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 替换 shapAnalysis()
    #
    # 重新搜索一次，
    # 因为前面可能对 js 做过修改。
    # --------------------------------------------------------

    match=re.search(
        r'function\s+shapAnalysis\s*\([^)]*\)\s*\{',
        js
    )


    if not match:
        return js


    start=match.start()


    try:
        end=js.index(
            'function mismatchView(i){',
            start
        )
    except ValueError:
        return js


    js=(
        js[:start]
        +SHAP_RENDERER
        +js[end:]
    )


    # --------------------------------------------------------
    # 修改“不配得性分析”的入口
    #
    # 原来可能是：
    #
    # if(i){
    #   sectionTabs(...)
    #   return;
    # }
    #
    # 现在统一为：
    #
    # if(i){
    #   shapAnalysis();
    #   return;
    # }
    #
    # i = 0 的筛选部分不动。
    # --------------------------------------------------------

    start=js.index(
        'function mismatchView(i){'
    )


    tail=js[start:]


    tail=re.sub(

        r" if\(i\)\{.*?return;\}\n const c=chart\(W,610\)",

        " if(i){shapAnalysis();return;}\n"
        " const c=chart(W,610)",

        tail,

        count=1,

        flags=re.S

    )


    js=js[:start]+tail


    return js


# ============================================================
# 普通分析卡片
# ============================================================

def card(route,kind):

    number,title=TITLES[kind]


    group=(
        ' regression'
        if kind in [
            'mixRegression',
            'weights',
            'memory'
        ]
        else ''
    )


    return (
        f'<a '
        f'class="panel{group}" '
        f'href="spacemovement/{route}" '
        f'aria-label="{number:02d} {escape(title)}">'
        f'<span class="panel-spine">'
        f'{number:02d} / {escape(title)}'
        f'</span>'
        f'<div class="panel-detail">'
        f'<span class="panel-number">'
        f'{number:02d}'
        f'</span>'
        f'<h2>{escape(title)}</h2>'
        f'<span class="panel-link">'
        f'OPEN VISUALIZATION ⟶'
        f'</span>'
        f'</div>'
        f'</a>'
    )


# ============================================================
# “什么是不配得性？”风琴块
# ============================================================

def mismatch_intro_card():

    return (
        '<a '
        'class="panel mismatch-intro-card" '
        'href="spacemovement/mismatch_intro.html" '
        'aria-label="什么是不配得性？">'
        '<span class="panel-spine">'
        '什么是不配得性？'
        '</span>'
        '<div class="panel-detail">'
        '<span class="panel-number">'
        'INFO'
        '</span>'
        '<h2>'
        '什么是不配得性？'
        '</h2>'
        '<span class="panel-link">'
        'OPEN INTRODUCTION ⟶'
        '</span>'
        '</div>'
        '</a>'
    )


# ============================================================
# 页面构建
# ============================================================

def pages():

    site=ROOT/'aerial'


    # ========================================================
    # 1. 原有 mismatch captions
    #
    # 暂时继续保留。
    #
    # 这样不会影响项目中可能仍依赖
    # shap-captions.js 的其他代码。
    # ========================================================

    inputs=json.loads(
        (
            ROOT
            /'scripts'
            /'mismatch_captions.json'
        ).read_text(
            encoding='utf-8'
        )
    )


    marker='/* Updated mismatch III captions */'


    caption=site/'assets/data/shap-captions.js'


    base=caption.read_text(
        encoding='utf-8'
    ).split(
        marker
    )[0]


    desc=inputs['descriptions']


    overrides={

        '高混合度低活力度':[
            desc['summary'],
            desc['interaction'],
            desc['summary']
        ],

        '高活力度低混合度':[
            desc['summary'],
            desc['interaction'],
            desc['trend']
        ]

    }


    # ========================================================
    # 2. 查找所有 SHAP 图片
    # ========================================================

    files=sorted(
        (
            ROOT/'result/shap'
        ).glob(
            '*/*'
        )
    )


    files=[
        file
        for file in files
        if file.is_file()
    ]


    # ========================================================
    # 3. 图片版本号
    #
    # 图片变化以后 hash 会变化，
    # 可以减少浏览器缓存旧图片的问题。
    # ========================================================

    if files:

        version=hashlib.sha256(

            b''.join(

                hashlib.sha256(
                    file.read_bytes()
                ).digest()

                for file in files

            )

        ).hexdigest()[:12]

    else:

        version='1'


    # ========================================================
    # 4. 保留原 shap-captions.js
    # ========================================================

    base+=(
        '\n'
        +marker
        +'\n'
        +'Object.assign('
        +'window.SHAP_CAPTIONS.groups,'
        +json.dumps(
            inputs['groups'],
            ensure_ascii=False
        )
        +');\n'
        +'window.SHAP_CAPTIONS.descriptionOverrides='
        +json.dumps(
            overrides,
            ensure_ascii=False
        )
        +';\n'
        +'window.SHAP_CAPTIONS.assetVersion='
        +json.dumps(version)
        +';\n'
    )


    caption.write_text(
        base,
        encoding='utf-8'
    )


    # ========================================================
    # 5. 读取新的 mismatch_content.json
    # ========================================================

    content_path=(
        ROOT
        /'scripts'
        /'mismatch_content.json'
    )


    mismatch_content=json.loads(
        content_path.read_text(
            encoding='utf-8'
        )
    )


    # 把图片版本号同时放进新的内容配置。
    mismatch_content[
        'assetVersion'
    ]=version


    # ========================================================
    # 6. 转换成浏览器可以直接读取的 JS
    #
    # 输出：
    #
    # aerial/assets/data/mismatch-content.js
    # ========================================================

    mismatch_js=(
        'window.MISMATCH_CONTENT='
        +json.dumps(
            mismatch_content,
            ensure_ascii=False
        )
        +';\n'
    )


    mismatch_js_path=(
        site
        /'assets'
        /'data'
        /'mismatch-content.js'
    )


    mismatch_js_path.write_text(
        mismatch_js,
        encoding='utf-8'
    )


    # ========================================================
    # 7. 把 result/shap 全部复制到网站资源
    # ========================================================

    shutil.copytree(
        ROOT/'result/shap',
        site/'assets/data/shap',
        dirs_exist_ok=True
    )


    # ========================================================
    # 8. 修改所有 chart JS
    #
    # 所有 chart 快照共用 renderer，
    # 最终根据 PAGE 判断执行哪个页面逻辑。
    # ========================================================

    for file in (
        site/'assets/js'
    ).glob(
        'chart-*.js'
    ):

        original=file.read_text(
            encoding='utf-8'
        )


        updated=renderer(
            original
        )


        file.write_text(
            updated,
            encoding='utf-8'
        )


    # ========================================================
    # 9. mixRegression 页面
    # ========================================================

    shutil.copy2(
        site/'assets/js/chart-03.js',
        site/'assets/js/chart-10.js'
    )


    template=(
        site
        /'spacemovement'
        /'people_composition.html'
    ).read_text(
        encoding='utf-8'
    )


    (
        site
        /'spacemovement'
        /'mixing_regression.html'
    ).write_text(

        template
        .replace(
            'data-page="composition"',
            'data-page="mixRegression"'
        )
        .replace(
            'chart-03.js',
            'chart-10.js'
        ),

        encoding='utf-8'

    )


    # ========================================================
    # 10. 写入 regression-revision.css
    # ========================================================

    (
        site
        /'assets'
        /'css'
        /'regression-revision.css'
    ).write_text(
        CSS,
        encoding='utf-8'
    )


    # ========================================================
    # 11. 生成“什么是不配得性？”说明页面
    #
    # 即使你已经手动创建了：
    #
    # aerial/spacemovement/mismatch_intro.html
    #
    # 每次 build 仍会重新覆盖为这里的版本。
    #
    # 所以以后：
    #
    # 页面结构 → 改本 Python
    # 页面文字 → 改 mismatch_content.json
    # ========================================================

    intro_path=(
        site
        /'spacemovement'
        /'mismatch_intro.html'
    )


    intro_path.write_text(
        mismatch_intro_page(),
        encoding='utf-8'
    )


    # 同步一份到项目根目录 spacemovement，
    # 保持项目现有页面镜像习惯。
    root_intro=(
        ROOT
        /'spacemovement'
        /'mismatch_intro.html'
    )


    root_intro.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    shutil.copy2(
        intro_path,
        root_intro
    )


    # ========================================================
    # 12. 逐一更新 01-09 页面
    # ========================================================

    for _,route,_,kind in CATALOG:

        path=(
            site
            /'spacemovement'
            /route
        )


        s=path.read_text(
            encoding='utf-8'
        )


        number,title=TITLES[kind]


        # ----------------------------------------------------
        # 页面 title
        # ----------------------------------------------------

        s=re.sub(
            r'<title>.*?</title>',
            f'<title>'
            f'{escape(title)}'
            f'｜Inclusive Vitality'
            f'</title>',
            s
        )


        # ----------------------------------------------------
        # 页面 H1
        # ----------------------------------------------------

        s=re.sub(
            r'<h1>.*?</h1>',
            f'<h1>'
            f'{number:02d} '
            f'{escape(title)}'
            f'</h1>',
            s
        )


        # ----------------------------------------------------
        # regression revision CSS
        # ----------------------------------------------------

        if (
            'regression-revision.css'
            not in s
        ):

            s=s.replace(

                '</head>',

                '<link '
                'rel="stylesheet" '
                'href="../assets/css/'
                'regression-revision.css">'
                '</head>'

            )


        # ----------------------------------------------------
        # 三个不配得性页面加载：
        #
        # mismatch-content.js
        #
        # 注意：
        # 只给 07、08、09 添加。
        # ----------------------------------------------------

        if kind in [
            'qualityVitality',
            'qualityMix',
            'mismatch'
        ]:

            if (
                'mismatch-content.js'
                not in s
            ):

                s=s.replace(

                    '</head>',

                    '<script '
                    'src="../assets/data/'
                    'mismatch-content.js">'
                    '</script>'
                    '</head>'

                )


        # ----------------------------------------------------
        # 写回 aerial
        # ----------------------------------------------------

        path.write_text(
            s,
            encoding='utf-8'
        )


        # ----------------------------------------------------
        # 同步到根目录 spacemovement
        # ----------------------------------------------------

        shutil.copy2(
            path,
            ROOT/'spacemovement'/route
        )


    # ========================================================
    # 13. 修改 visualizations.html
    #
    # 原来：
    #
    # 不配得性Ⅰ
    # 不配得性Ⅱ
    # 不配得性Ⅲ
    #
    # 现在：
    #
    # 什么是不配得性？
    # 不配得性Ⅰ
    # 不配得性Ⅱ
    # 不配得性Ⅲ
    # ========================================================

    path=site/'visualizations.html'


    s=path.read_text(
        encoding='utf-8'
    )


    # 根据 TITLES 中的编号重新排序。
    ordered=sorted(
        CATALOG,
        key=lambda entry:
        TITLES[
            entry[3]
        ][0]
    )


    cards=[
        card(
            route,
            kind
        )
        for _,route,_,kind
        in ordered
    ]


    # 前 6 个普通分析
    first_six=''.join(
        cards[:6]
    )


    # 不配得性介绍 + 07/08/09
    mismatch_cards=(
        mismatch_intro_card()
        +''.join(
            cards[6:]
        )
    )


    # --------------------------------------------------------
    # 整个风琴结构
    # --------------------------------------------------------

    main=(

        '<main class="macro-stage">'

        '<div class="accordion">'

        +first_six+

        '<button '
        'class="panel mismatch-entry" '
        'aria-expanded="false" '
        'aria-controls="mismatch-menu">'

        '<span class="panel-spine">'
        '07–09 / 不配得性分析'
        '</span>'

        '<div class="panel-detail">'

        '<span class="panel-number">'
        '07–09'
        '</span>'

        '<h2>'
        '不配得性分析'
        '</h2>'

        '<span class="panel-link">'
        '展开分析 ⟶'
        '</span>'

        '</div>'

        '</button>'

        '</div>'


        '<section '
        'id="mismatch-menu" '
        'class="mismatch-menu" '
        'inert>'

        '<button class="menu-back">'
        '← 返回全部分析'
        '</button>'

        +mismatch_cards+

        '</section>'

        '</main>'

    )


    s=re.sub(
        r'<main\b.*?</main>',
        lambda _:
        main,
        s,
        flags=re.S
    )


    # 仍然是 9 个正式 study。
    # “什么是不配得性？”是说明页，
    # 不占用 10 号。
    s=s.replace(
        '08 STUDIES',
        '09 STUDIES'
    )


    if (
        'regression-revision.css'
        not in s
    ):

        s=s.replace(

            '</head>',

            '<link '
            'rel="stylesheet" '
            'href="assets/css/'
            'regression-revision.css">'
            '</head>'

        )


    path.write_text(
        s,
        encoding='utf-8'
    )


    # ========================================================
    # 14. 数据 CSV
    # ========================================================

    for name in [
        'data-extract.csv',
        'data_extract.csv'
    ]:

        shutil.copy2(
            ROOT/name,
            site/'assets/data'/name
        )


# ============================================================
# 总刷新
# ============================================================

def refresh():

    # --------------------------------------------------------
    # 原有数据修订
    # --------------------------------------------------------

    from final_revision import revise


    path=(
        ROOT
        /'aerial'
        /'assets'
        /'data'
        /'inclusive-data.js'
    )


    data=json.loads(

        path
        .read_text(
            encoding='utf-8'
        )
        .split(
            '=',
            1
        )[1]
        .strip()
        .rstrip(';')

    )


    revise(
        data
    )


    path.write_text(

        'window.INCLUSIVE='
        +json.dumps(
            data,
            ensure_ascii=False,
            allow_nan=False
        )
        +';\n',

        encoding='utf-8'

    )


    # --------------------------------------------------------
    # 页面 / SHAP / 说明页
    # --------------------------------------------------------

    pages()


    # --------------------------------------------------------
    # aerial → dist
    # --------------------------------------------------------

    from sync_static import copy_static


    shutil.copytree(
        ROOT/'aerial',
        ROOT/'dist',
        dirs_exist_ok=True,
        copy_function=copy_static
    )


    # --------------------------------------------------------
    # dist → docs / GitHub Pages
    # --------------------------------------------------------

    from prepare_pages import prepare


    prepare()


    # --------------------------------------------------------
    # 构建诊断信息
    # --------------------------------------------------------

    print(

        json.dumps(

            {

                'scoreMeans':
                data['scoreMeans'],

                'groupCounts':{

                    kind:{

                        label:
                        sum(

                            p[
                                'mismatchGroups'
                            ][kind]
                            ==label

                            for p
                            in data['points']

                        )

                        for label
                        in sorted({

                            p[
                                'mismatchGroups'
                            ][kind]

                            for p
                            in data['points']

                            if p[
                                'mismatchGroups'
                            ][kind]

                        })

                    }

                    for kind in [
                        'qualityVitality',
                        'qualityMix',
                        'mismatch'
                    ]

                }

            },

            ensure_ascii=False

        )

    )


# ============================================================
# 单独执行本文件时
# ============================================================

if __name__=='__main__':
    refresh()
