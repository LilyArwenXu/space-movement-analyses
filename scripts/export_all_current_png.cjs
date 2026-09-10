/* Export the current nine macro panels without changing website files. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {pathToFileURL}=require('url');
const runtime=process.env.CODEX_NODE_MODULES||'C:/Users/11346/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {chromium}=require(require.resolve('playwright',{paths:[runtime]}));
const sharp=require(require.resolve('sharp',{paths:[runtime]}));
sharp.cache({memory:32,files:0,items:20});
const root=path.resolve(__dirname,'..'),output=path.join(root,'result'),scale=3.125,width=5000;
const clean=s=>s.replace(/[<>:"/\\|?*\x00-\x1f]/g,'_').trim().slice(0,90);
const buffer=url=>Buffer.from(url.split(',')[1],'base64');
function hashes(){const result={};for(const dir of ['aerial','dist','docs']){const walk=folder=>{for(const entry of fs.readdirSync(folder,{withFileTypes:true})){const file=path.join(folder,entry.name);if(entry.isDirectory())walk(file);else if(/\.(html|css|js)$/.test(file))result[path.relative(root,file)]=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');}};walk(path.join(root,dir));}return result;}
async function screenshotTiled(page,locator){
 await page.evaluate(()=>window.scrollTo(0,0));
 const box=await locator.boundingBox();if(!box)throw Error('Missing export surface');
 const parts=[];let top=0,pixels=0;
 for(let offset=0;offset<box.height;offset+=800){
  const png=await page.screenshot({animations:'disabled',fullPage:true,clip:{x:box.x,y:box.y+offset,width:box.width,height:Math.min(800,box.height-offset)}});
  const meta=await sharp(png).metadata();pixels=meta.width;parts.push({input:png,left:0,top});top+=meta.height;
 }
 return sharp({create:{width:pixels,height:top,channels:4,background:'#fff'},limitInputPixels:false}).composite(parts).png().toBuffer();
}
async function captionImage(sheet,text,heading=false){
 await sheet.evaluate(({text,heading})=>{document.body.innerHTML='';const box=document.createElement('div');box.id='caption';box.style.cssText='box-sizing:border-box;width:1600px;padding:24px 28px;background:white;color:#000;white-space:pre-line;overflow-wrap:anywhere;font:300 '+(heading?23:18)+'px/1.8 "Microsoft YaHei",sans-serif';box.textContent=text;document.body.append(box);},{text,heading});
 await sheet.evaluate(()=>document.fonts.ready);
 return screenshotTiled(sheet,sheet.locator('#caption'));
}
async function exportChart(locator,composition){
 return buffer(await locator.evaluate(async(n,composition)=>{
  const c=echarts.getInstanceByDom(n),o=c.getOption();await document.fonts.load('300 18px "Microsoft YaHei"');
  if(composition){
   const fix=x=>{if(!x||typeof x!=='object')return;for(const [k,v] of Object.entries(x)){if(k==='fontFamily')x[k]='Microsoft YaHei';else if(k==='fontWeight')x[k]=300;else fix(v);}};fix(o);
   o.textStyle={...o.textStyle,fontFamily:'Microsoft YaHei',fontWeight:300};o.yAxis[0].data=window.INCLUSIVE.points.map(p=>p.address);
   const ctx=document.createElement('canvas').getContext('2d');ctx.font='300 '+(o.yAxis[0].axisLabel.fontSize||12)+'px "Microsoft YaHei"';
   o.grid[0].left=Math.ceil(Math.max(...o.yAxis[0].data.map(a=>ctx.measureText(a).width))+28);
   o.legend.forEach(l=>l.type='plain');
  }
  if(!composition)(o.grid||[]).forEach(grid=>{if(typeof grid.left==='number')grid.left+=40;if(typeof grid.right==='number')grid.right+=50;});
  o.animation=false;o.animationDuration=0;o.animationDurationUpdate=0;o.toolbox=[{show:false}];
  c.resize({width:1600,height:Math.max(c.getHeight(),600),animation:{duration:0}});c.setOption(o,{notMerge:true});c.getZr().flush();
  if(composition){const labels=c.getOption().yAxis[0].data;if(JSON.stringify(labels)!==JSON.stringify(window.INCLUSIVE.points.map(p=>p.address)))throw Error('Address mismatch');
   if(c.getZr().storage.getDisplayList(true).filter(x=>x.type==='tspan').some(x=>/SimSun|Songti|serif/i.test(x.style.font||'')))throw Error('Unexpected serif composition label');}
  return c.getDataURL({type:'png',pixelRatio:3.125,backgroundColor:'#fff',excludeComponents:['toolbox']});
 },composition));
}
async function matrixImage(page){
 return buffer(await page.evaluate(()=>{
  const d=window.INCLUSIVE,ys=Object.keys(d.ys),cellW=125,cellH=40,left=320,top=220;
  const canvas=document.createElement('canvas');canvas.width=(left+ys.length*cellW+20)*3.125;canvas.height=(top+d.fields.length*cellH+30)*3.125;
  const ctx=canvas.getContext('2d');ctx.scale(3.125,3.125);ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.font='300 18px "Microsoft YaHei"';ctx.fillStyle='#292929';
  ys.forEach((key,x)=>{ctx.save();ctx.translate(left+(x+.5)*cellW,top-15);ctx.rotate(-Math.PI/4);ctx.fillText(d.ys[key],0,0);ctx.restore();});
  const cells=[...document.querySelectorAll('.cov-cell')];d.fields.forEach((field,y)=>{ctx.fillStyle='#292929';ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(field.label,left-12,top+(y+.5)*cellH,left-20);
   ys.forEach((key,x)=>{const r=d.correlations.find(r=>r.x===field.key&&r.y===key);ctx.fillStyle=getComputedStyle(cells[y*ys.length+x]).backgroundColor;ctx.fillRect(left+x*cellW,top+y*cellH,cellW-1,cellH-1);ctx.fillStyle=getComputedStyle(cells[y*ys.length+x]).color;ctx.textAlign='center';ctx.fillText(Number.isFinite(r.rho)?r.rho.toFixed(2)+(r.p<.001?'***':r.p<.01?'**':r.p<.05?'*':''):'—',left+(x+.5)*cellW,top+(y+.5)*cellH);if(Number.isFinite(r.p)&&r.p<.05){ctx.strokeStyle='#000';ctx.lineWidth=1.5;ctx.strokeRect(left+x*cellW+1,top+y*cellH+1,cellW-3,cellH-3);}});
  });return canvas.toDataURL('image/png');
 }));
}
(async()=>{
 const only=process.argv.find(a=>a.startsWith('--only='))?.slice(7),view=process.argv.find(a=>a.startsWith('--view='))?.slice(7);
 const from=process.argv.find(a=>a.startsWith('--from='))?.slice(7),previous=from?JSON.parse(fs.readFileSync(only?path.join(output,'manifest.json'):path.join(root,'.site-build/current-export-progress.json'),'utf8')):null;
 const before=hashes(),browser=await chromium.launch({channel:'msedge',headless:true}),files=previous?.files.filter(f=>f.panel.slice(0,2)<from)||[],views=previous?.views.filter(v=>v.panel.slice(0,2)<from)||[],errors=[];
 const context=await browser.newContext({viewport:{width:1800,height:1200},deviceScaleFactor:scale});
 const index=await context.newPage();await index.goto(pathToFileURL(path.join(root,'docs/visualizations.html')).href);
 const panels=await index.locator('a.panel').evaluateAll(nodes=>nodes.map(n=>({url:n.href,title:n.getAttribute('aria-label')})));await index.close();
 assert.equal(panels.length,9);
 const sheet=await context.newPage();await sheet.setContent('<html><body style="margin:0;background:#fff"></body></html>');
 try{
  for(const panel of panels.filter(p=>(!only||p.title.startsWith(only))&&(!from||p.title.slice(0,2)>=from))){
   const page=await context.newPage();page.on('pageerror',e=>errors.push(panel.title+': '+String(e)));
   await page.goto(panel.url);await page.evaluate(()=>document.fonts.ready);
   // Export-only layout: expose complete captions and collapsed methodology.
   await page.addStyleTag({content:'html,body{height:auto!important;overflow:visible!important}*,*::before,*::after{animation:none!important;transition:none!important}.screen-analysis{display:block!important}.workspace{height:auto!important;overflow:visible!important}.dom-chart-download{display:none!important}.shap-side{max-height:none!important;overflow:visible!important}.shap-side,.shap-side p,.coefficient-caption,.coefficient-conclusion,.critic-method,.readme,.caption{font-family:"Microsoft YaHei",sans-serif!important;font-weight:300!important;color:#000!important}.score-table-wrap{max-height:none!important;overflow:visible!important}'});
   async function groups(){return page.evaluate(()=>[...new Set([...document.querySelectorAll('button[role="tab"]')].filter(b=>b.getClientRects().length&&!b.closest('[hidden]')).map(b=>b.parentElement))].map((parent,i)=>{parent.dataset.exportGroup=i;return [...parent.children].filter(n=>n.tagName==='BUTTON').map(n=>n.textContent);}));}
   async function capture(tabs){
    if(view&&tabs[0]!==view)return;
    await page.evaluate(()=>document.querySelectorAll('[data-export-item]').forEach(n=>n.removeAttribute('data-export-item')));
    await page.evaluate(async()=>{document.querySelectorAll('details.critic-method').forEach(n=>n.open=true);await Promise.all([...document.querySelectorAll('.workspace img')].filter(n=>n.getClientRects().length).map(n=>n.decode()));});
    const items=await page.evaluate(()=>[...document.querySelectorAll('.plot,.map-stage,.covariance,.coefficients,.shap-gallery>.shap-figure')].filter(n=>n.getClientRects().length&&!n.closest('[hidden]')).map((n,i)=>{n.dataset.exportItem=i;const c=echarts.getInstanceByDom(n);return {id:i,chart:!!c,kind:n.className,title:c?(c.getOption().title||[]).map(t=>t.text).filter(Boolean).join(' '):n.classList.contains('shap-figure')?n.querySelector('img').alt:n.className};}));
    views.push({panel:panel.title,tabs,charts:items.length});
    for(const item of items){
     const locator=page.locator('[data-export-item="'+item.id+'"]');
     const meta=await locator.evaluate(n=>{const isCoefficient=n.classList.contains('coefficients'),scope=n.parentElement;return {note:document.querySelector('.readme')?.innerText||'',captions:isCoefficient?[]:[...scope.querySelectorAll('.caption,.mismatch-conclusion')].map(n=>n.innerText),legend:document.querySelector('.heat-legend')?.innerText||''};});
     const body=item.chart?await exportChart(locator,panel.title.startsWith('02 ')):item.kind==='covariance'?await matrixImage(page):await screenshotTiled(page,locator);
     const parts=[await captionImage(sheet,[panel.title,...tabs,item.title].filter(Boolean).join(' / '),true),body];
     const legend=page.locator('.heat-legend').first();if(await legend.count()&&await legend.isVisible()){await legend.evaluate(n=>{n.style.fontFamily='"Microsoft YaHei",sans-serif';n.style.fontWeight='300';});parts.push(await screenshotTiled(page,legend));}
     const note=[...new Set([meta.legend,...meta.captions,meta.note].filter(Boolean))].join('\n\n');if(note)parts.push(await captionImage(sheet,note));
     const composite=[];let top=0;
     for(const part of parts){const resized=await sharp(part,{limitInputPixels:false}).resize({width}).png().toBuffer(),m=await sharp(resized,{limitInputPixels:false}).metadata();composite.push({input:resized,left:0,top});top+=m.height;}
     const filename=String(files.length+1).padStart(3,'0')+'_'+clean(tabs.join('_')||'图表')+'_'+clean(item.title||String(item.id+1))+'.png';
     const dir=clean(panel.title),relative=path.join(dir,filename);fs.mkdirSync(path.join(output,dir),{recursive:true});
     await sharp({create:{width,height:top,channels:4,background:'#fff'},limitInputPixels:false}).composite(composite).withMetadata({density:300}).png().toFile(path.join(output,relative));
     const m=await sharp(path.join(output,relative),{limitInputPixels:false}).metadata();assert.equal(m.density,300);assert.equal(m.width,width);
     files.push({file:relative,panel:panel.title,tabs,title:item.title,width,height:top,dpi:300,captionFont:'Microsoft YaHei Light (300)',...(panel.title.startsWith('02 ')?{allTextFont:'Microsoft YaHei Light (300)',addressOnly:true}:{})});
     fs.writeFileSync(path.join(root,'.site-build/current-export-progress.json'),JSON.stringify({files,views,errors},null,2));
    }
   }
   async function walk(depth,tabs){const g=await groups();if(depth>=g.length){await capture(tabs);return;}for(let i=0;i<g[depth].length;i++){await groups();await page.locator('[data-export-group="'+depth+'"]>button').nth(i).evaluate(b=>b.click());await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await walk(depth+1,[...tabs,g[depth][i]]);}}
   await walk(0,[]);await page.close();console.log(panel.title+': '+files.filter(f=>f.panel===panel.title).length+' PNG');
  }
  assert.deepStrictEqual(hashes(),before,'Export modified website files');if(errors.length)throw Error(errors.join('\n'));
  if(!only){
   const current=new Set(files.map(f=>path.resolve(output,f.file))),archive=path.join(root,'.site-build/previous-chart-exports',new Date().toISOString().replace(/[:.]/g,'-'));
   for(const dir of fs.readdirSync(output,{withFileTypes:true}).filter(d=>d.isDirectory()&&/^\d{2} /.test(d.name))){for(const name of fs.readdirSync(path.join(output,dir.name)).filter(n=>n.endsWith('.png'))){const source=path.resolve(output,dir.name,name);if(!current.has(source)){assert(source.startsWith(output+path.sep));const target=path.join(archive,dir.name,name);fs.mkdirSync(path.dirname(target),{recursive:true});fs.renameSync(source,target);}}}
   fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({images:files.length,dpi:300,views,files,errors,websiteUnchanged:true},null,2));
   fs.writeFileSync(path.join(output,'README.txt'),'当前网页图表导出\n'+files.length+' 张PNG；'+views.length+' 个选项卡视图；9个板块。\n全部300 dpi、5000像素宽。图注采用微软雅黑细字重。\n人群构成分析五张图的所有文字均为微软雅黑细字重，纵坐标仅包含完整点位地址。\n网页宋体和数据不因导出而改变。\n完整对应关系见manifest.json。\n重新导出：node scripts/export_all_current_png.cjs\n');
  }else if(fs.existsSync(path.join(output,'manifest.json'))){
   const manifest=JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8'));
   for(const item of files.filter(f=>f.panel.startsWith(only))){const i=manifest.files.findIndex(f=>f.file===item.file);if(i>=0)manifest.files[i]=item;}
   fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2));
  }
  console.log('Exported '+files.length+' PNGs from '+views.length+' views; source files unchanged.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
