/* Export every macro tab, nested tab and road drill-down from the built site. */
const fs = require('fs'), path = require('path'), {pathToFileURL} = require('url');
const runtime = process.env.CODEX_NODE_MODULES || 'C:/Users/11346/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {chromium} = require(require.resolve('playwright', {paths:[runtime]}));
const root = path.resolve(__dirname, '..'), output = path.join(root, 'result');
const clean = s => s.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').trim().slice(0, 55);
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({channel:'msedge', headless:true});
  const context = await browser.newContext({viewport:{width:1800,height:1200},deviceScaleFactor:2});
  const page = await context.newPage(), sheet = await context.newPage();
  const only=process.argv.find(a=>a.startsWith('--only='))?.slice(7);
  const previous=only&&fs.existsSync(path.join(output,'manifest.json'))?JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8')):null;
  const errors=[], manifest=previous?.files||[], views=previous?.views||[];
  page.on('pageerror', e=>errors.push(String(e)));
  await sheet.setContent('<html><body style="margin:0;background:white"></body></html>');
  await page.goto(pathToFileURL(path.join(root,'docs/visualizations.html')).href);
  const panels = await page.locator('.panel').evaluateAll(nodes=>nodes.map(n=>({url:n.href,title:n.getAttribute('aria-label')})));
  async function groups() {
    return page.evaluate(()=>{
      const parents=[...new Set([...document.querySelectorAll('button[role="tab"], .road-buttons > button')].filter(b=>b.getClientRects().length).map(b=>b.parentElement))];
      return parents.map((p,i)=>{p.dataset.exportGroup=String(i);return [...p.children].filter(b=>b.tagName==='BUTTON').map(b=>b.textContent)});
    });
  }
  async function capture(panel, selections) {
    const items=await page.evaluate(()=>[...document.querySelectorAll('.plot,.map-stage,.covariance')].filter(n=>n.getClientRects().length).map((n,i)=>{n.dataset.exportItem=i;const c=echarts.getInstanceByDom(n);return {id:i,chart:!!c,title:c?(c.getOption().title||[]).map(t=>t.text).filter(Boolean).join(' '):n.className};}));
    if(!views.some(v=>v.panel===panel.title&&JSON.stringify(v.tabs)===JSON.stringify(selections)))views.push({panel:panel.title,tabs:selections,charts:items.length});
    for (const item of items) {
      const locator=page.locator(`[data-export-item="${item.id}"]`);
      const meta=await locator.evaluate(n=>{
        const scope=n.closest('.case-scatter')||n.parentElement;
        const c=echarts.getInstanceByDom(n);
        if(c && !c.getOption().textStyle.fontFamily.startsWith('SimSun'))throw new Error('Chart font is not SimSun');
        return {note:document.querySelector('.readme').textContent,captions:[...scope.querySelectorAll('.caption')].map(n=>n.textContent),legend:(scope.querySelector('.case-legend')||document.querySelector('.heat-legend'))?.outerHTML||''};
      });
      let image;
      if(item.chart) image=await locator.evaluate(n=>{
        const c=echarts.getInstanceByDom(n),w=c.getWidth(),h=c.getHeight();
        c.setOption({animation:false,toolbox:{show:false}});
        c.resize({width:Math.max(w,1200),height:Math.max(h,600),animation:{duration:0}});
        c.getZr().flush();
        const url=c.getDataURL({type:'png',pixelRatio:2,backgroundColor:'#fff',excludeComponents:['toolbox']});
        c.resize({width:w,height:h,animation:{duration:0}});
        return url;
      });
      else if(item.title==='covariance') image=await page.evaluate(()=>{
        // Hover-only labels are made permanent for the static export.
        const d=window.INCLUSIVE,ys=Object.keys(d.ys),cellW=125,cellH=40,left=320,top=220;
        const canvas=document.createElement('canvas');canvas.width=left+ys.length*cellW+20;canvas.height=top+d.fields.length*cellH+30;
        const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.font='18px SimSun';ctx.fillStyle='#292929';
        ys.forEach((key,x)=>{ctx.save();ctx.translate(left+(x+.5)*cellW,top-15);ctx.rotate(-Math.PI/4);ctx.fillText(d.ys[key],0,0);ctx.restore()});
        const cells=[...document.querySelectorAll('.cov-cell')];
        d.fields.forEach((field,y)=>{
          ctx.fillStyle='#292929';ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(field.label,left-12,top+(y+.5)*cellH,left-20);
          ys.forEach((key,x)=>{const r=d.correlations.find(r=>r.x===field.key&&r.y===key);ctx.fillStyle=getComputedStyle(cells[y*ys.length+x]).backgroundColor;ctx.fillRect(left+x*cellW,top+y*cellH,cellW-1,cellH-1);ctx.fillStyle='#292929';ctx.textAlign='center';ctx.fillText(Number.isFinite(r.rho)?r.rho.toFixed(2)+(r.p<.001?'***':r.p<.01?'**':r.p<.05?'*':''):'—',left+(x+.5)*cellW,top+(y+.5)*cellH);});
        });
        return canvas.toDataURL('image/png');
      });
      else {
        await locator.locator('img').evaluateAll(async imgs=>{await Promise.all(imgs.map(i=>i.decode()))});
        await page.addStyleTag({content:'.dom-chart-download{visibility:hidden!important}'});
        image='data:image/png;base64,'+(await locator.screenshot({animations:'disabled'})).toString('base64');
      }
      const heading=[panel.title,...selections,item.title].filter(Boolean).join(' / ');
      await sheet.evaluate(async ({image,heading,meta})=>{
        document.body.replaceChildren();
        const box=document.createElement('article');box.id='export';box.style.cssText='width:1600px;padding:30px;box-sizing:border-box;background:white;color:#292929;font:18px/1.65 SimSun,serif;';
        const title=document.createElement('div');title.textContent=heading;title.style.cssText='font-size:23px;margin-bottom:18px';box.append(title);
        if(meta.legend){const legend=document.createElement('div');legend.innerHTML=meta.legend;legend.style.marginBottom='12px';legend.querySelectorAll('.case-legend-item').forEach(n=>n.style.cssText='display:inline-flex;align-items:center;gap:8px;margin-right:24px');legend.querySelectorAll('.case-legend-dot').forEach(n=>{n.style.display='inline-block';n.style.width='12px';n.style.height='12px';n.style.borderRadius='50%'});legend.querySelectorAll('.heat-gradient').forEach(n=>n.style.cssText='display:inline-block;width:180px;height:14px;background:linear-gradient(90deg,#2166ac,#67a9cf,#f7f7f7,#f4a582,#b2182b)');box.append(legend);}
        const img=new Image();img.src=image;img.style.cssText='display:block;width:100%;height:auto';box.append(img);
        const note=document.createElement('div');note.textContent=[...new Set([...meta.captions,meta.note].filter(Boolean))].join('\n\n');note.style.cssText='white-space:pre-line;margin-top:20px;font:18px/1.65 SimSun,serif';box.append(note);
        document.body.append(box);await img.decode();await document.fonts.ready;
      },{image,heading,meta});
      const dir=clean(panel.title);fs.mkdirSync(path.join(output,dir),{recursive:true});
      const filename=String(manifest.length+1).padStart(3,'0')+'_'+clean(selections.join('_')||'图表')+'_'+clean(item.title||String(item.id+1))+'.png';
      const existing=manifest.find(m=>m.panel===panel.title&&m.title===item.title&&JSON.stringify(m.tabs)===JSON.stringify(selections));
      const relative=existing?.file||path.join(dir,filename);
      await sheet.locator('#export').screenshot({path:path.join(output,relative)});
      if(!existing)manifest.push({file:relative,panel:panel.title,tabs:selections,title:item.title});
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
    for(const panel of panels.filter(p=>!only||p.title.startsWith(only))){
      await page.goto(panel.url);await page.evaluate(()=>document.fonts.ready);
      await walk(panel,0,[]);
      console.log(panel.title+': '+manifest.filter(m=>m.panel===panel.title).length+' PNG');
    }
    fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({images:manifest.length,views,files:manifest,errors},null,2));
    fs.writeFileSync(path.join(output,'README.txt'),`宏观数据分析图表导出\n共 ${manifest.length} 张 PNG；${views.length} 个选项卡/道路视图。\n字体：宋体 SimSun；白底，宽 3200 像素，含图例与说明。\n按宏观目录的8个板块分文件夹；包括所有主选项卡、二级选项卡、道路展开及案例横轴选项。\n保留网页默认指标显示状态和默认回归条带参数；缺失数据提示原样保留。\n完整选项卡及文件对应关系见 manifest.json。\n重新导出：node scripts/export_macro_png.cjs\n`);
    if(errors.length)throw new Error(errors.join('\n'));
    console.log(`Exported ${manifest.length} PNGs from ${views.length} views.`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
