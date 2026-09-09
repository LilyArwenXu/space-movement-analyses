const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),runtime=process.env.CODEX_NODE_MODULES||'C:/Users/11346/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const sharp=require(require.resolve('sharp',{paths:[runtime]}));
(async()=>{
 const output=path.join(root,'result'),m=JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8'));
 if(m.errors.length)throw Error(m.errors.join('\n'));
 if(m.images!==37||m.views.length!==37)throw Error('Unexpected chart/tab coverage');
 for(const f of m.files){const meta=await sharp(path.join(output,f.file)).metadata();if(meta.density!==300)throw Error('Incorrect DPI: '+f.file);if(meta.width<3000)throw Error('Insufficient pixel width: '+f.file);}
 if(m.views.filter(v=>v.charts===0).length!==6)throw Error('Expected six intentional mismatch placeholder tabs');
 m.dpi=300;fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(m,null,2));
 fs.writeFileSync(path.join(output,'README.txt'),'宏观行为分析图表导出（2026-09-10）\n共37张PNG，覆盖8个板块、37个末级选项卡视图。\n全部导出图片为300 dpi，宽5000像素，保留图例、公式与说明；长图按全部135个点位扩展高度。\n包括3张系数表征；六个不配得性后续分析选项卡按要求无图，清单明确记录为0。\n权重目录M/Q/V.png为用户提供的原始输入图片，保持原文件。\n完整对应关系见manifest.json。重新导出：node scripts/export_macro_png.cjs；核验：node scripts/verify_final_exports.cjs。\n');
 console.log('Verified 37 PNGs at 300 dpi, 37 tab views, 6 intentional empty analysis tabs; no rendering errors.');
})().catch(e=>{console.error(e);process.exitCode=1});
