// Shared nested navigation keeps the outer selection while reusing existing charts.
function sectionTabs(labels,render){const nav=el('div','subtabs');tabs(nav,labels,i=>{charts.forEach(c=>c.dispose());charts=[];Array.from(W.children).forEach(n=>{if(n!==nav)n.remove();});document.body.classList.remove('screen-analysis');render(i);});}
function mixingSection(){sectionTabs(['信息散点图','全域与所有街道',...D.admins.map(g=>g.name)],i=>{if(i===0){informationExplorer(W,'mix');return;}diversity(i-1);});}
if(PAGE==='heat')mainTabs(['热力分布图','样本数'],i=>mapView(1-i));
if(PAGE==='weights')mainTabs(['空间分析','界面品质信息表'],i=>{if(i)informationExplorer(W,'quality');else sectionTabs(['有效空间分析','舒适度分析'],space);});
if(PAGE==='composition')mainTabs(['人群构成','混合度信息表'],i=>{if(i)mixingSection();else sectionTabs(['点位年龄构成','街道年龄构成','身份倾向'],j=>composition([1,0,2][j]));});
if(PAGE==='memory')mainTabs(['在地记忆的假设','活力度信息表'],i=>{if(i)informationExplorer(W,'vitality');else sectionTabs(D.memory.map(g=>g.cohort+'群体'),memory);});
if(PAGE==='space')mainTabs(['有效空间分析','舒适度分析'],space);
if(PAGE==='diversity')mixingSection();
if(PAGE==='correlations')mainTabs(['Spearman相关性分析'],()=>covarianceMatrix());
if(PAGE==='qualityVitality'||PAGE==='qualityMix')mainTabs(['不配得性分析','案例分析'],i=>{if(i)caseStudy(PAGE);else qualityChart(PAGE);});
if(PAGE==='mismatch')mainTabs(['筛选','不配得性分析','案例分析'],i=>i===2?caseStudy(PAGE):mismatch(i));
