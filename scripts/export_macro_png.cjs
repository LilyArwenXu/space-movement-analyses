/* Export every macro tab, nested tab and road drill-down from the built site. */
const fs = require('fs'), path = require('path'), {pathToFileURL,fileURLToPath} = require('url');
const runtime = process.env.CODEX_NODE_MODULES || 'C:/Users/11346/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {chromium} = require(require.resolve('playwright', {paths:[runtime]}));
const sharp = require(require.resolve('sharp', {paths:[runtime]}));
const root = path.resolve(__dirname, '..'), output = path.join(root, 'result');
const clean = s => s.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').trim().slice(0, 55);
async function screenshotTiled(page,locator){
  await page.evaluate(()=>window.scrollTo(0,0));
  const box=await locator.boundingBox(),scale=3.125;
  if(box.height*scale<11000)return locator.screenshot({animations:'disabled'});
  const pieces=[];let top=0,width=0;
  for(let offset=0;offset<box.height;offset+=1200){
    const png=await page.screenshot({fullPage:true,animations:'disabled',clip:{x:box.x,y:box.y+offset,width:box.width,height:Math.min(1200,box.height-offset)}});
    const meta=await sharp(png).metadata();width=meta.width;pieces.push({input:png,left:0,top});top+=meta.height;
  }
  return sharp({create:{width,height:top,channels:4,background:'#fff'},limitInputPixels:false}).composite(pieces).png().toBuffer();
}
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({channel:'msedge', headless:true});
  const context = await browser.newContext({viewport:{width:1800,height:1200},deviceScaleFactor:3.125});
  const page = await context.newPage(), sheet = await context.newPage();
  const only=process.argv.find(a=>a.startsWith('--only='))?.slice(7);
  const from=process.argv.find(a=>a.startsWith('--from='))?.slice(7);
  const oldFiles=fs.existsSync(path.join(output,'manifest.json'))?JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8')).files:[];
  const previous=(only||from)&&fs.existsSync(path.join(output,'manifest.json'))?JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8')):null;
  const errors=[], manifest=previous?.files||[], views=previous?.views||[];
  page.on('pageerror', e=>errors.push(String(e)));
  await sheet.setContent('<html><body style="margin:0;background:white"></body></html>');
  await sheet.evaluate(async url=>{const font=new FontFace('ExportHei',`url("${url}")`,{weight:'100 900'});await font.load();document.fonts.add(font);},'data:font/ttf;base64,'+fs.readFileSync(path.join(root,'docs/assets/fonts/FZVariable-LanTingHeiK.TTF')).toString('base64'));
  await page.goto(pathToFileURL(path.join(root,'docs/visualizations.html')).href);
  const panels = await page.locator('a.panel').evaluateAll(nodes=>nodes.map(n=>({url:n.href,title:n.getAttribute('aria-label')})));
  async function groups() {
    return page.evaluate(()=>{
      const parents=[...new Set([...document.querySelectorAll('button[role="tab"], .road-buttons > button')].filter(b=>b.getClientRects().length).map(b=>b.parentElement))];
      return parents.map((p,i)=>{p.dataset.exportGroup=String(i);return [...p.children].filter(b=>b.tagName==='BUTTON').map(b=>b.textContent)});
    });
  }
  async function capture(panel, selections) {
    await page.evaluate(()=>document.querySelectorAll('[data-export-item]').forEach(n=>n.removeAttribute('data-export-item')));
    await page.evaluate(()=>document.querySelectorAll('.coefficients .score-table-wrap').forEach(n=>{n.style.maxHeight='none';n.style.overflow='visible';}));
    const items=await page.evaluate(()=>[...document.querySelectorAll('.plot,.map-stage,.covariance,.coefficients,.shap-gallery:not(:has(.shap-triptych))>.shap-figure,.shap-gallery:has(.shap-triptych),.mismatch-combined')].filter(n=>n.getClientRects().length&&!n.closest('[hidden]')).map((n,i)=>{n.dataset.exportItem=i;const c=echarts.getInstanceByDom(n);return {id:i,chart:!!c,title:c?(c.getOption().title||[]).map(t=>t.text).filter(Boolean).join(' '):n.classList.contains('mismatch-combined')?n.querySelector('h2').textContent:n.classList.contains('shap-figure')?n.querySelector('img').alt:n.className};}));
    if(!views.some(v=>v.panel===panel.title&&JSON.stringify(v.tabs)===JSON.stringify(selections)))views.push({panel:panel.title,tabs:selections,charts:items.length});
    for (const item of items) {
      const locator=page.locator(`[data-export-item="${item.id}"]`);
      const meta=await locator.evaluate(n=>{
        const scope=n.closest('.case-scatter')||n.parentElement;
        const c=echarts.getInstanceByDom(n);
        if(c && !c.getOption().textStyle.fontFamily.startsWith('SimSun'))throw new Error('Chart font is not SimSun');
        const sourceLegend=scope.querySelector('.case-legend')||document.querySelector('.heat-legend'),legend=sourceLegend?.cloneNode(true);
        if(legend)sourceLegend.querySelectorAll('.heat-gradient,.correlation-gradient').forEach((source,i)=>{const target=legend.querySelectorAll('.heat-gradient,.correlation-gradient')[i];target.style.cssText='display:inline-block;width:260px;height:16px;vertical-align:middle;background:'+getComputedStyle(source).backgroundImage;target.className='export-gradient';});
        return {note:document.querySelector('.readme').textContent,captions:[...scope.querySelectorAll('.caption,.critic-method,.coefficient-conclusion,.mismatch-conclusion')].map(n=>n.textContent),legend:legend?.outerHTML||''};
      });
      let image,coefficientPNG;
      if(item.chart) image=await locator.evaluate(n=>{
        const c=echarts.getInstanceByDom(n),w=c.getWidth(),h=c.getHeight();
        c.setOption({animation:false,toolbox:{show:false}});
        c.resize({width:Math.max(w,1200),height:Math.max(h,600),animation:{duration:0}});
        c.getZr().flush();
        const url=c.getDataURL({type:'png',pixelRatio:3.125,backgroundColor:'#fff',excludeComponents:['toolbox']});
        c.resize({width:w,height:h,animation:{duration:0}});
        return url;
      });
      else if(item.title==='covariance') image=await page.evaluate(()=>{
        // Hover-only labels are made permanent for the static export.
        const d=window.INCLUSIVE,ys=Object.keys(d.ys),cellW=125,cellH=40,left=320,top=220;
        const canvas=document.createElement('canvas');canvas.width=(left+ys.length*cellW+20)*3.125;canvas.height=(top+d.fields.length*cellH+30)*3.125;
        const ctx=canvas.getContext('2d');ctx.scale(3.125,3.125);ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.font='18px SimSun';ctx.fillStyle='#292929';
        ys.forEach((key,x)=>{ctx.save();ctx.translate(left+(x+.5)*cellW,top-15);ctx.rotate(-Math.PI/4);ctx.fillText(d.ys[key],0,0);ctx.restore()});
        const cells=[...document.querySelectorAll('.cov-cell')];
        d.fields.forEach((field,y)=>{
          ctx.fillStyle='#292929';ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(field.label,left-12,top+(y+.5)*cellH,left-20);
          ys.forEach((key,x)=>{const r=d.correlations.find(r=>r.x===field.key&&r.y===key);ctx.fillStyle=getComputedStyle(cells[y*ys.length+x]).backgroundColor;ctx.fillRect(left+x*cellW,top+y*cellH,cellW-1,cellH-1);ctx.fillStyle=getComputedStyle(cells[y*ys.length+x]).color;ctx.textAlign='center';ctx.fillText(Number.isFinite(r.rho)?r.rho.toFixed(2)+(r.p<.001?'***':r.p<.01?'**':r.p<.05?'*':''):'—',left+(x+.5)*cellW,top+(y+.5)*cellH);});
        });
        d.fields.forEach((field,y)=>ys.forEach((key,x)=>{const r=d.correlations.find(r=>r.x===field.key&&r.y===key);if(Number.isFinite(r.p)&&r.p<.05){ctx.strokeStyle='#000';ctx.lineWidth=1.5;ctx.strokeRect(left+x*cellW+1,top+y*cellH+1,cellW-3,cellH-3);}}));
        return canvas.toDataURL('image/png');
      });
      else if(item.title==='coefficients') {
        const source=await locator.locator('.coefficient-image').evaluate(img=>img.src);
        image='data:image/png;base64,'+fs.readFileSync(fileURLToPath(source)).toString('base64');
      }
      else {
        await locator.locator('img').evaluateAll(async imgs=>{await Promise.all(imgs.map(i=>i.decode()))});
        await locator.locator('.shap-side').evaluateAll(notes=>{
          for(const note of notes)if(note.scrollHeight>note.clientHeight+1)throw new Error('SHAP side caption clipped');
        });
        await page.addStyleTag({content:'.dom-chart-download{visibility:hidden!important}'});
        const exportStyle=await page.addStyleTag({content:'.shap-side,.shap-bottom,.shap-conclusion{font-family:FZLanTingHei,SimHei,sans-serif!important;font-weight:300!important;color:#000!important}'});
        const png=await screenshotTiled(page,locator);
        await exportStyle.evaluate(n=>n.remove());
        if(item.title==='coefficients')coefficientPNG=png;
        else image='data:image/png;base64,'+png.toString('base64');
      }
      const heading=[panel.title,...selections,item.title].filter(Boolean).join(' / ');
      await sheet.evaluate(async ({image,heading,meta})=>{
        document.body.replaceChildren();
        const box=document.createElement('article');box.id='export';box.style.cssText='width:1600px;padding:30px;box-sizing:border-box;background:white;color:#292929;font:18px/1.65 SimSun,serif;';
        const title=document.createElement('div');title.textContent=heading;title.style.cssText='font-size:23px;margin-bottom:18px';box.append(title);
        if(meta.legend){const legend=document.createElement('div');legend.innerHTML=meta.legend;legend.style.marginBottom='12px';legend.querySelectorAll('.case-legend-item').forEach(n=>n.style.cssText='display:inline-flex;align-items:center;gap:8px;margin-right:24px');legend.querySelectorAll('.case-legend-dot').forEach(n=>{n.style.display='inline-block';n.style.width='12px';n.style.height='12px';n.style.borderRadius='50%'});legend.querySelectorAll('.heat-gradient').forEach(n=>n.style.cssText='display:inline-block;width:180px;height:14px;background:linear-gradient(90deg, #2166ac, #67a9cf, #f7f7f7, #f4a582, #b2182b)');box.append(legend);}
        let img;if(image){img=new Image();img.src=image;img.style.cssText='display:block;width:100%;height:auto';box.append(img);}
        const note=document.createElement('div');note.textContent=[...new Set([...meta.captions,meta.note].filter(Boolean))].join('\n\n');note.style.cssText='white-space:pre-line;margin-top:20px;color:#000;font:300 18px/1.65 ExportHei,SimHei,sans-serif';box.append(note);
        document.body.append(box);if(img)await img.decode();await document.fonts.ready;
      },{image,heading,meta});
      const dir=clean(panel.title);fs.mkdirSync(path.join(output,dir),{recursive:true});
      const filename=String(manifest.length+1).padStart(3,'0')+'_'+clean(selections.join('_')||'图表')+'_'+clean((item.title||String(item.id+1)).replace(/\.png$/i,''))+'.png';
      const existing=manifest.find(m=>m.panel===panel.title&&m.title===item.title&&JSON.stringify(m.tabs)===JSON.stringify(selections));
      const relative=existing?.file||path.join(dir,filename);
      let png=await screenshotTiled(sheet,sheet.locator('#export'));
      if(coefficientPNG){
        const header=await sharp(png).metadata(),body=await sharp(coefficientPNG,{limitInputPixels:false}).resize({width:header.width}).png().toBuffer(),bodyMeta=await sharp(body,{limitInputPixels:false}).metadata();
        png=await sharp({create:{width:header.width,height:header.height+bodyMeta.height,channels:4,background:'#fff'},limitInputPixels:false}).composite([{input:png,left:0,top:0},{input:body,left:0,top:header.height}]).png().toBuffer();
      }
      await sharp(png,{limitInputPixels:false}).withMetadata({density:300}).toFile(path.join(output,relative));
      if(!existing)manifest.push({file:relative,panel:panel.title,tabs:selections,title:item.title});
      fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({images:manifest.length,dpi:300,views,files:manifest,errors},null,2));
    }
  }
  async function walk(panel,depth,selections) {
    const current=await groups();
    if(depth>=current.length){await capture(panel,selections);return;}
    for(let i=0;i<current[depth].length;i++){
      await groups();
      await page.locator(`[data-export-group="${depth}"] > button`).nth(i).evaluate(b=>b.click());
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      await walk(panel,depth+1,[...selections,current[depth][i]]);
    }
  }
  try {
    for(const panel of panels.filter(p=>(!only||p.title.startsWith(only))&&(!from||p.title.slice(0,2)>=from))){
      await page.goto(panel.url);await page.evaluate(()=>document.fonts.ready);
      await walk(panel,0,[]);
      console.log(panel.title+': '+manifest.filter(m=>m.panel===panel.title).length+' PNG');
    }
    fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({images:manifest.length,dpi:300,views,files:manifest,errors},null,2));
    fs.writeFileSync(path.join(output,'README.txt'),`宏观数据分析图表导出\n共 ${manifest.length} 张 PNG；${views.length} 个选项卡/道路视图。\n字体：宋体 SimSun；白底，300 dpi，常规组合图宽 5000 像素，含图例与说明。\n按宏观目录的8个板块分文件夹；包括所有主选项卡、二级选项卡、道路展开及SHAP图注组合图。\n保留网页默认指标显示状态和默认回归条带参数；缺失数据提示原样保留。\n完整选项卡及文件对应关系见 manifest.json。\n重新导出：node scripts/export_macro_png.cjs\n`);
    if(errors.length)throw new Error(errors.join('\n'));
    if(!only){const current=new Set(manifest.map(m=>path.resolve(output,m.file)));for(const old of oldFiles){const file=path.resolve(output,old.file);if(file.startsWith(output+path.sep)&&file.endsWith('.png')&&!current.has(file)&&fs.existsSync(file))fs.unlinkSync(file);}}
    console.log(`Exported ${manifest.length} PNGs from ${views.length} views.`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
