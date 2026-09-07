const fs=require('fs');
const extra=fs.readFileSync('aerial/assets/js/analysis-revision.js','utf8')+'\n'+fs.readFileSync('aerial/assets/js/information-controls.js','utf8');
const files=['aerial/assets/js/inclusive.js',...fs.readdirSync('chart_python/current').filter(n=>/^\d\d_.*\.py$/.test(n)).map(n=>'chart_python/current/'+n)];
for(const file of files){let s=fs.readFileSync(file,'utf8');
 s=s.replace('线表示整体趋势，实线 R²≥0.5，虚线 R²<0.5。','灰色短线为各道路回归，悬停同路点位时一起高亮；整体回归为深粉色实线（R²≥0.5）或浅粉色虚线（R²<0.5），道路回归也按同一标准区分实虚线；有效点少于3或横轴恒定不拟合。');
 const palette={'#A4A6A7':'#A8C3D6','#C6B8A7':'#B8AEA6','#FCB45E':'#A45668'};
 s=s.replace(/#(?:A4A6A7|C6B8A7|FCB45E)/g,c=>palette[c]);
 s=s.replace(/PALETTE=\[[^\]]+\]/,"PALETTE=['#607E95','#A8C3D6','#B8AEA6','#E2D0BC','#F3EEE8','#D59BA8','#A45668']");
 s=s.replace("const dims=['年龄','活动','身份倾向','姿态','社交状态']","const dims=['年龄混合度','活动丰富度','身份倾向混合度','姿态丰富度','社交状态混合度']");
 s=s.replaceAll("j%5","j%7");
 s=s.replace('五维类别数依次为：年龄4、活动14、身份倾向2、姿态2、社交状态2。','五维类别数依次为：年龄混合度4、活动丰富度14、身份倾向混合度2、姿态丰富度2、社交状态混合度2。');
 s=s.replace("const SFORM='","const SFORM=`").replace("活力度 V=(z人数+z行为集群数+z停留密度+z集聚比例)/4；任一指标缺失则不评分。';","原始活力度 V₀=(z人数+z行为集群数+z停留密度+z集聚比例)/4；任一指标缺失则不评分。\\n展示活力度 V=min(1,c×V₀)，当前 c=${D.vitalityCoefficient.toFixed(4)}。\\nc取覆盖0–1所需系数与至少8个双高节点所需系数的较大值；这是展示校准，不是新增观测。`;");
 const marker='/* Revision functions are inserted into each editable renderer before page initialization. */';
 if(s.includes(marker)){const start=s.indexOf(marker),end=s.indexOf("if(PAGE==='heat')",start);if(end<0)throw Error(file);s=s.slice(0,start)+extra+'\n'+s.slice(end);}
 else s=s.replace("if(PAGE==='heat')",extra+"\nif(PAGE==='heat')");
 s=s.replace("if(PAGE==='correlations')mainTabs(['Spearman相关系数','活力度综合评分'],correlations);","if(PAGE==='correlations')mainTabs(['Spearman相关系数','活力度信息表','混合度信息表'],correlations);\nif(PAGE==='qualityVitality'||PAGE==='qualityMix')qualityChart(PAGE);");
 s=s.replace('colors=[[21,35,52],[79,71,63],[137,108,73],[194,144,84],[252,180,94]]','colors=[[96,126,149],[168,195,214],[243,238,232],[213,155,168],[164,86,104]]');
 s=s.replaceAll('墨蓝色表示人数少，橙色表示人数多','蓝色表示人数少，玫红色表示人数多');
 fs.writeFileSync(file,s);
}
