/* Export-only typography overrides. Never writes website files. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {pathToFileURL}=require('url');
const runtime=process.env.CODEX_NODE_MODULES||'C:/Users/11346/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {chromium}=require(require.resolve('playwright',{paths:[runtime]}));
const sharp=require(require.resolve('sharp',{paths:[runtime]}));
const root=path.resolve(__dirname,'..'),out=path.join(root,'result/02 混合度计算');
function siteHashes(){const hashes={};for(const name of ['aerial','dist','docs']){const walk=dir=>{for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())walk(file);else if(/\.(html|css|js)$/.test(file))hashes[path.relative(root,file)]=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');}};walk(path.join(root,name));}return hashes;}
(async()=>{
 const before=siteHashes(),browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1800,height:1100}});
  await page.goto(pathToFileURL(path.join(root,'docs/spacemovement/people_composition.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  const files=[];
  for(let i=0;i<5;i++){
   const result=await page.evaluate(async index=>{
    document.querySelectorAll('.workspace>.subtabs>button')[index].click();
    const chart=echarts.getInstanceByDom(document.querySelector('.plot')),option=chart.getOption();
    const family='Microsoft YaHei',font='300 18px "Microsoft YaHei"';
    await document.fonts.load(font);
    function restyle(value){
     if(!value||typeof value!=='object')return;
     for(const [key,item] of Object.entries(value)){
      if(key==='fontFamily')value[key]=family;
      else if(key==='fontWeight')value[key]=300;
      else if(key==='font'&&typeof item==='string')value[key]=item.replace(/(?:SimSun|Songti SC|serif)/g,'Microsoft YaHei');
      else restyle(item);
     }
    }
    restyle(option);option.textStyle={...option.textStyle,fontFamily:family,fontWeight:300};
    option.animation=false;option.animationDuration=0;option.animationDurationUpdate=0;
    option.toolbox=[{show:false}];option.yAxis[0].data=window.INCLUSIVE.points.map(p=>p.address);
    const measure=document.createElement('canvas').getContext('2d');measure.font='300 '+(option.yAxis[0].axisLabel.fontSize||12)+'px "Microsoft YaHei"';
    option.grid[0].left=Math.ceil(Math.max(...option.yAxis[0].data.map(address=>measure.measureText(address).width))+28);
    option.legend.forEach(legend=>{legend.type='plain';legend.textStyle={...legend.textStyle,fontFamily:family,fontWeight:300};});
    chart.resize({width:1600,height:Math.max(650,window.INCLUSIVE.points.length*28+140),animation:{duration:0}});
    chart.setOption(option,{notMerge:true});chart.getZr().flush();
    const expected=window.INCLUSIVE.points.map(p=>p.address);
    if(JSON.stringify(chart.getOption().yAxis[0].data)!==JSON.stringify(expected))throw Error('Address labels do not match');
    const text=chart.getZr().storage.getDisplayList(true).filter(el=>el.type==='tspan');
    if(!text.length||text.some(el=>/SimSun|Songti|serif/i.test(el.style.font||'')))throw Error('Unexpected serif text in export');
    const chartURL=chart.getDataURL({type:'png',pixelRatio:3.125,backgroundColor:'#fff',excludeComponents:['toolbox']});
    const note=document.querySelector('.readme').textContent;
    const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),padding=26,lines=[];
    ctx.font=font;
    note.split('\n').forEach(paragraph=>{let line='';for(const character of paragraph){if(line&&ctx.measureText(line+character).width>1600-padding*2){lines.push(line);line=character;}else line+=character;}lines.push(line);});
    canvas.width=5000;canvas.height=Math.ceil((padding*2+lines.length*29)*3.125);
    ctx.scale(3.125,3.125);ctx.fillStyle='#fff';ctx.fillRect(0,0,1600,canvas.height/3.125);
    ctx.fillStyle='#000';ctx.font=font;ctx.textBaseline='top';lines.forEach((line,j)=>ctx.fillText(line,padding,padding+j*29));
    const footerURL=canvas.toDataURL('image/png');canvas.width=0;canvas.height=0;
    return {name:window.INCLUSIVE.mixDimensions[index].label,url:chartURL,footer:footerURL,points:expected.length,textCount:text.length};
   },i);
   const filename=String(8+i).padStart(3,'0')+'_构成分析_'+result.name+'_'+result.name+'.png';
   const target=path.join(out,filename);
   const body=Buffer.from(result.url.split(',')[1],'base64'),footer=Buffer.from(result.footer.split(',')[1],'base64');
   const bodyMeta=await sharp(body,{limitInputPixels:false}).metadata(),footerMeta=await sharp(footer).metadata();
   await sharp({create:{width:5000,height:bodyMeta.height+footerMeta.height,channels:4,background:'#fff'},limitInputPixels:false}).composite([{input:body,left:0,top:0},{input:footer,left:0,top:bodyMeta.height}]).withMetadata({density:300}).png().toFile(target);
   const meta=await sharp(target,{limitInputPixels:false}).metadata();assert.equal(meta.width,5000);assert.equal(meta.density,300);
   files.push({file:filename,width:meta.width,height:meta.height,points:result.points,font:'Microsoft YaHei Light (300)',textCount:result.textCount});
   console.log(filename+' — '+meta.width+' × '+meta.height+' px, 300 dpi');
  }
  assert.deepStrictEqual(siteHashes(),before,'Website source changed during export');
  fs.writeFileSync(path.join(out,'构成分析_导出说明.json'),JSON.stringify({files,websiteUnchanged:true},null,2));
  console.log('Verified all five PNGs; website HTML, CSS and JavaScript are unchanged.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
