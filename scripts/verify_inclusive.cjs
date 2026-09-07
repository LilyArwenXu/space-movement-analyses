const fs=require('fs'),vm=require('vm'),assert=require('assert');
const echarts=require('../spacemovement/echarts.min.js');
const payload=fs.readFileSync('aerial/assets/data/inclusive-data.js','utf8');
const pages=['heat','weights','composition','memory','space','diversity','correlations','mismatch'];
let renders=0;
function setup(page,width=1360){
 const all=[],made=[];
 function element(tag='div'){
  const n={tag,children:[],style:{},dataset:{},attrs:{},listeners:{},className:'',textContent:'',innerHTML:'',hidden:false,
   append(v){this.children.push(v)},replaceChildren(){this.children=[];this.innerHTML=''},setAttribute(k,v){this.attrs[k]=String(v)},addEventListener(k,f){this.listeners[k]=f},remove(){},scrollIntoView(){this.scrolled=true},
   querySelectorAll(selector){const test=v=>selector==='button'?v.tag==='button':selector[0]==='.'?v.className.split(' ').includes(selector.slice(1)):false;const result=[];function walk(v){v.children.forEach(c=>{if(test(c))result.push(c);walk(c)})}walk(this);return result;},
   querySelector(s){return this.querySelectorAll(s)[0]||null},click(){this.onclick?.()},
   getContext(){return {createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)}},putImageData(){}}},toDataURL(){return 'data:image/png;base64,verified'}
  };
  n.classList={add(v){n.className+=' '+v},remove(v){n.className=n.className.split(' ').filter(x=>x!==v).join(' ')},toggle(v,on){on?this.add(v):this.remove(v)}};all.push(n);return n;
 }
 const elements={};['.workspace','.tabs','.readme','.meta'].forEach(k=>elements[k]=element());const body=element('body');body.dataset.page=page;
 const context={console,setTimeout,clearTimeout,Float32Array,Uint8ClampedArray,window:{innerWidth:width,innerHeight:900,addEventListener(){},matchMedia(){return {matches:true}}},document:{body,querySelector(s){return elements[s]||body.querySelector(s)},createElement:element,createElementNS(_,tag){return element(tag)}},echarts:{init(el){const c=echarts.init(null,null,{renderer:'svg',ssr:true,width,height:parseInt(el.style.height)||520});made.push(c);return c;}}};
 const source=fs.readFileSync('docs/assets/js/chart-'+String(pages.indexOf(page)+1).padStart(2,'0')+'.js','utf8');
 vm.createContext(context);vm.runInContext(payload,context);vm.runInContext(source,context);
 function check(){made.filter(c=>!c.isDisposed()).forEach(c=>{const o=c.getOption();assert.equal(o.backgroundColor,'#fff');if(page==='diversity'&&o.radar){assert.equal(o.radar[0].splitLine.lineStyle.color,'#C6B8A7');o.series.forEach(s=>{if(s.type==='radar')assert.equal(s.lineStyle.color,s.lineStyle.type==='dashed'?'#FCB45E':'#A4A6A7')});}const svg=c.renderToSVGString();assert(svg.includes('<path'));assert(!svg.includes('NaN'));renders++;fs.writeFileSync(`.site-build/inclusive-${page}-${width}.svg`,svg);});}
 return {all,made,elements,context,check,dispose(){made.filter(c=>!c.isDisposed()).forEach(c=>c.dispose())}};
}
for(const page of ['heat','weights','composition','memory','space','diversity','correlations','mismatch']){
 const t=setup(page);t.check();
 if(page==='space'){
  const sub=t.elements['.workspace'].children.find(n=>n.className==='subtabs');assert.equal(sub.children.length,3);
  for(const b of sub.children){b.click();t.check();assert.equal(t.made.filter(c=>!c.isDisposed()).length,1);assert.equal(t.made.filter(c=>!c.isDisposed())[0].getOption().legend.length,0);}
 }
 if(page==='heat'){
  assert.equal(t.all.filter(n=>n.className.includes('map-point')).length,135);
  const controls=t.all.find(n=>n.className==='map-tools activity-tabs');assert.equal(controls.children.length,6);
  assert.deepEqual(controls.children.map(b=>b.textContent),['观察人数','光顾人数','打卡人数','饮食人数','社交人数','休憩人数']);
  for(const b of controls.children)b.click();
 }
 if(page==='correlations'){assert(t.elements['.workspace'].children[0].innerHTML.includes('B1'));assert(t.elements['.workspace'].children[0].innerHTML.includes('circle'));}
 for(const b of t.elements['.tabs'].children.slice(1)){b.click();t.check();
  if(page==='diversity'){
   const roadButtons=t.elements['.workspace'].children.find(n=>n.className==='road-buttons');
   for(const road of roadButtons.children){road.click();t.check();const last=t.made.filter(c=>!c.isDisposed());assert.equal(last.length,4);const lorenz=last[2].getOption();assert.equal(lorenz.xAxis[0].data.length,15);assert(lorenz.legend[0].top>lorenz.title[0].top+25);assert(lorenz.grid[0].top>lorenz.legend[0].top+25);assert.equal(last[3].getOption().xAxis[0].axisLabel.show,false);}
  }
 }
 if(page==='mismatch'){const sub=t.elements['.workspace'].children.find(n=>n.className==='subtabs');for(const b of sub.children.slice(1)){b.click();t.check();}}
 t.dispose();
}
for(const width of [375,768,1920]){const t=setup('memory',width);t.check();for(const b of t.elements['.tabs'].children.slice(1)){b.click();t.check();}for(const c of t.made.filter(c=>!c.isDisposed())){c.reflow();t.check();}t.dispose();}
console.log(`Verified eight study routes, all road drilldowns, six indicators, map selectors and ${renders} SVG renderings.`);
