"""Polished controls, coefficient explanations and mismatch presentation."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MIX_SUBTITLE = '第d维混合度 H_d=−Σ(p_k×ln p_k)/ln K_d；p_k=类别频数/该维频数合计，0×ln0记0。\n零合计或缺失不评分。\n综合混合度 M=0.149H年龄+0.141H活动+0.250H身份倾向+0.228H姿态+0.233H社交状态。\n权重按给定公式顺序使用，不二次归一化。\n权重说明保留给定w1–w5名称；综合混合度（综合评分）按指定M公式的维度顺序代入。'
MIX_CONCLUSION = '进一步结合指标相关性与CRITIC权重分析可见，姿态丰富度与身份倾向混合度对街区综合混合度的贡献最为突出。其中活动丰富度与社交状态混合度呈现较强的相关性，说明行人的行为活动与社交行为存在明显的耦合关系。而年龄混合度权重相对较低，对整体混合度的解释力有限。由此可以推测，街道空间能否容纳多样化的身体姿态行为、能否吸引多元身份人群到访，是提升街区混合度的核心驱动要素。'
MISMATCH_CONCLUSION = '活力度与人群身份混合度呈显著正相关，混合度整体随活力度上升。散点分布显示，多数点位混合度取值略高于活力度，仅少数样本呈高活力度—低混合度的背离特征。据此推断，人群构成的多元化或先于街道活力的提升而发生；通过增强街道空间包容性、适配多元人群需求，可有效促进街道活力。'
CRITIC = '''<h2>Critic权重算法</h2>
<h3>1. 对比强度</h3><p class="formula">S_j = √ [ (1/(n-1)) × Σ(x_ij - x̄_j)² ]</p>
<p>x_ij 是第i个样本第j个指标的值，x̄_j 是第j个指标的均值。\nΣ是对i从1到n求和。</p>
<p>标准差越大，说明这个指标越能区分不同样本，越重要。</p>
<h3>2. 冲突性</h3><p class="formula">R_j = Σ (1 - |r_jk|)</p>
<p>其中 r_jk 是第j个指标和第k个指标的皮尔逊相关系数，|r_jk| 是取绝对值。\nΣ是对k从1到m求和。\n当k=j时，自己跟自己的相关系数是1，1减1等于0，所以自己那一项自动为0。</p>
<p>R_j越大，说明这个指标跟别人越不相关，提供的信息越独特。</p>
<h3>3. 综合信息量及权重</h3><p class="formula">C_j = S_j × R_j</p><p class="formula">w_j = C_j / ΣC_j</p>
<p>其中ΣC_j是对所有指标的C_j求和。</p>'''

CSS = '''/* Gentle interaction transitions; screen captions remain Song. */
button,a.portal,[role="tab"],select,input{transition:background-color .22s ease,color .22s ease,border-color .22s ease,box-shadow .22s ease,transform .22s ease,opacity .22s ease}
#header nav a.portal{border:1px solid transparent!important;box-shadow:none!important}
#header nav a.portal:hover,#header nav a.portal:focus-visible{border-color:#000!important;box-shadow:inset 0 0 0 1px #000!important}
#header nav a.portal:active,#header nav a.portal.is-entering{background:#000!important;color:#fff!important;border-color:#000!important;transform:scale(.98)}
#header nav a.portal:active *,#header nav a.portal.is-entering *{color:#fff!important}
button:not(.cov-cell):not(.metric-toggle):hover{box-shadow:inset 0 0 0 1px #000}
body .metric-controls.axis-controls .metric-control .metric-toggle{width:20px!important;height:20px!important;min-width:20px;padding:0!important;border:2px solid #000!important;border-radius:50%!important;background:#fff!important;box-shadow:none!important;transform:scale(1);opacity:1!important}
body .metric-controls.axis-controls .metric-control .metric-toggle[data-phase="1"],body .metric-controls.axis-controls .metric-control .metric-toggle[data-phase="2"]{background:#000!important;border-color:#000!important}
body .metric-controls.axis-controls .metric-control .metric-toggle[data-phase="2"]{transform:scale(.6)}
.axis-controls .metric-toggle:focus-visible{outline:2px solid #000;outline-offset:4px}
.critic-method,.coefficient-conclusion,.mismatch-conclusion{font-family:SimSun,'Songti SC',serif;font-weight:400;line-height:1.9;white-space:pre-line}
.critic-method{margin:28px 0 36px;padding:24px 0;border-top:1px solid #ccc;border-bottom:1px solid #ccc;white-space:normal}
.critic-method p{white-space:pre-line;margin:12px 0}.critic-method h2{font-size:23px;margin:0 0 24px}.critic-method h3{font-size:18px;margin:24px 0 12px}.critic-method .formula{overflow-wrap:anywhere}
.coefficient-conclusion{margin:24px 0}.mismatch-conclusion{margin:24px 0 32px}
.mismatch-combined{width:100%;margin:12px 0 36px}.mismatch-combined h2{font-family:SimSun,'Songti SC',serif;font-size:22px;margin:24px 0 18px}
.mismatch-triptych{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start}.mismatch-triptych figure{margin:0;min-width:0}.mismatch-triptych img{display:block;width:100%;height:auto}
@media(max-width:650px){.mismatch-triptych{grid-template-columns:1fr;gap:18px}.critic-method{padding:20px 0}}
@media(prefers-reduced-motion:reduce){button,a.portal,[role="tab"],select,input{transition:none!important}}
'''
INTERACTIONS = '''document.addEventListener('click',event=>{
 const link=event.target.closest('a.portal');if(!link||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 link.classList.add('is-entering');if(link.target==='_blank'){setTimeout(()=>link.classList.remove('is-entering'),350);return;}
 event.preventDefault();setTimeout(()=>window.location.assign(link.href),window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:170);
});window.addEventListener('pageshow',()=>document.querySelectorAll('.is-entering').forEach(n=>n.classList.remove('is-entering')));
document.addEventListener('click',event=>{const tab=event.target.closest('[role="tab"]');if(!tab||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;const host=document.getElementById(tab.getAttribute('aria-controls'))||document.querySelector('.workspace');host?.animate([{opacity:.65,transform:'translateY(3px)'},{opacity:1,transform:'translateY(0)'}],{duration:230,easing:'ease-out'});});
window.exportAnnotatedChart=async(c,node)=>{
 await document.fonts.load('300 16px FZLanTingHei');
 const image=new Image();image.src=c.getDataURL({type:'png',pixelRatio:2,backgroundColor:'#fff',excludeComponents:['toolbox']});await image.decode();
 const caption=[...new Set([...node.parentElement.querySelectorAll('.caption'),document.querySelector('.readme')].filter(n=>n&&!n.hidden).map(n=>n.textContent.trim()).filter(Boolean))].join('\\n\\n');
 const width=c.getWidth(),padding=24,canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
 ctx.font='300 16px FZLanTingHei, SimHei, sans-serif';const lines=[];
 caption.split('\\n').forEach(paragraph=>{let line='';for(const char of paragraph){if(line&&ctx.measureText(line+char).width>width-padding*2){lines.push(line);line=char;}else line+=char;}lines.push(line);});
 const chartHeight=image.height/2;canvas.width=image.width;canvas.height=Math.ceil((chartHeight+(caption?padding*2+lines.length*26:0))*2);ctx.scale(2,2);ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width/2,canvas.height/2);ctx.drawImage(image,0,0,width,chartHeight);ctx.font='300 16px FZLanTingHei, SimHei, sans-serif';ctx.fillStyle='#000';ctx.textBaseline='top';if(caption)lines.forEach((line,i)=>ctx.fillText(line,padding,chartHeight+padding+i*26));
 const a=document.createElement('a');a.download=document.title.split('｜')[0]+'.png';a.href=canvas.toDataURL('image/png');a.click();
};
'''

def renderer(js):
    axis_title="name:{quality:'所有点位（按界面品质从低到高）',mix:'所有点位（按综合混合度从低到高）',vitality:'所有点位（按空间活力度从低到高）'}[kind]"
    js=js.replace('name:original.xAxis[0].name',axis_title)
    old="saveAsImage:{type:'png',name:(document.title||'图表').split('｜')[0],title:'下载 PNG',pixelRatio:2,backgroundColor:'#fff',excludeComponents:['toolbox']}"
    new="mySaveAsImage:{show:true,title:'下载 PNG',icon:'path://M4,16 L4,21 L20,21 L20,16 M12,2 L12,16 M6,10 L12,16 L18,10',onclick:()=>window.exportAnnotatedChart(c,node)}"
    js=js.replace(old,new)
    js=js.replace('async function exportDOMChart(node){',"async function exportDOMChart(node){\n await document.fonts.load('300 16px FZLanTingHei');") if "await document.fonts.load('300 16px FZLanTingHei');" not in js else js
    js=js.replace('ctx.font=css.font;',"ctx.font='300 '+css.fontSize+' FZLanTingHei, SimHei, sans-serif';")
    if '/* interaction-revision */' in js:
        return js
    js=js.replace("data:points.map(p=>p.name+' · '+p.id),axisLabel", "data:points.map(p=>p.address),axisLabel")
    js=js.replace("main.style.background=PALETTE[j%PALETTE.length];", "main.dataset.phase='0';")
    js=js.replace("controls.querySelectorAll('button').forEach((b,k)=>b.setAttribute('aria-pressed',String(k===selected)));", "controls.querySelectorAll('button').forEach((b,k)=>{b.setAttribute('aria-pressed',String(k===selected));b.dataset.phase=String(k===selected?phase:0);});")
    js=js.replace("controls.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed','false'));", "controls.querySelectorAll('button').forEach(b=>{b.setAttribute('aria-pressed','false');b.dataset.phase='0';});")
    js=js.replace("const controls=el('div','metric-controls axis-controls',host)", "original.xAxis.forEach(axis=>axis.name={quality:'所有点位（按界面品质从低到高）',mix:'所有点位（按综合混合度从低到高）',vitality:'所有点位（按空间活力度从低到高）'}[kind]);\n const controls=el('div','metric-controls axis-controls',host)")
    js=js.replace("name:'所有点位（按综合评分从低到高）'", axis_title)
    js=js.replace(" const lower=el('div','coefficient-tables',box)", " el('section','critic-method',box).innerHTML="+json.dumps(CRITIC,ensure_ascii=False)+";\n const lower=el('div','coefficient-tables',box)")
    js=js.replace(" const label={mix:'混合度',quality:'界面品质',vitality:'活力度'}", " if(kind==='mix')el('p','coefficient-conclusion',left).textContent="+json.dumps(MIX_CONCLUSION.replace('。','。\n').strip(),ensure_ascii=False)+";\n const label={mix:'混合度',quality:'界面品质',vitality:'活力度'}")
    js=js.replace("MFORM+'\\n权重说明保留给定w1–w5名称；综合评分按指定M公式的维度顺序代入。'",json.dumps(MIX_SUBTITLE,ensure_ascii=False))
    js=js.replace("if(i){sectionTabs(labels,j=>shapAnalysis(labels[j]));return;}", "if(i){if(PAGE==='mismatch'){labels.forEach(label=>{const group=el('section','mismatch-combined shap-gallery');el('h2','',group).textContent=label;const row=el('div','mismatch-triptych',group);[1,2,3].forEach(number=>{const figure=el('figure','',row),img=el('img','',figure);img.src='../assets/data/shap/'+label+'/'+number+'.png';img.alt=label+' · 图'+number;});});note('');}else sectionTabs(labels,j=>shapAnalysis(labels[j]));return;}")
    needle="el('p','caption').textContent=labels.map(label=>label+'：'+D.points.filter(p=>p.mismatchGroups[PAGE]===label).length+' 个点位').join('；');"
    js=js.replace(needle,needle+"\n if(PAGE==='mismatch')el('p','mismatch-conclusion').textContent="+json.dumps(MISMATCH_CONCLUSION.replace('。','。\n').strip(),ensure_ascii=False)+";")
    return js+'\n/* interaction-revision */\n'

def pages():
    for folder in ['aerial','dist','docs']:
        site=ROOT/folder
        (site/'assets/css/interaction-revision.css').write_text(CSS,encoding='utf-8')
        (site/'assets/js/interaction-revision.js').write_text(INTERACTIONS,encoding='utf-8')
        for file in (site/'assets/js').glob('chart-*.js'):
            file.write_text(renderer(file.read_text(encoding='utf-8')),encoding='utf-8')
        for file in site.rglob('*.html'):
            if 'assets' in file.relative_to(site).parts:continue
            s=file.read_text(encoding='utf-8')
            if 'interaction-revision.css' in s:continue
            prefix='../' if file.parent.name=='spacemovement' else ''
            s=s.replace('</head>',f'<link rel="stylesheet" href="{prefix}assets/css/interaction-revision.css"></head>')
            s=s.replace('</body>',f'<script src="{prefix}assets/js/interaction-revision.js"></script></body>')
            file.write_text(s,encoding='utf-8')

if __name__=='__main__':
    pages()
    print('Updated interactions, coefficient methods, labels, and mismatch panels.')
