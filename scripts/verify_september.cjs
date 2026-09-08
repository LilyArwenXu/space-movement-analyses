const fs=require('fs'),vm=require('vm'),assert=require('assert'),echarts=require('../spacemovement/echarts.min.js');
const PAGES=['heat','weights','composition','memory','space','correlations','qualityVitality','qualityMix','mismatch'];let rendered=0;
function setup(page,width=1100){
 const all=[],made=[],timers=new Map();let timerId=0;const queue=f=>{timers.set(++timerId,f);return timerId;};
 function element(tag='div'){const n={tag,children:[],style:{setProperty(k,v){this[k]=v}},dataset:{},attrs:{},listeners:{},className:'',textContent:'',innerHTML:'',hidden:false,
 append(c){c.parent=this;this.children.push(c)},replaceChildren(){this.children=[];this.innerHTML=''},setAttribute(k,v){this.attrs[k]=String(v)},addEventListener(k,f){this.listeners[k]=f},scrollIntoView(){this.scrolled=true},remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this)},contains(c){return this.children.includes(c)},
 querySelectorAll(s){let found=[];for(const c of this.children){if((s==='button'&&c.tag==='button')||(s[0]==='.'&&c.className.split(' ').includes(s.slice(1))))found.push(c);found.push(...c.querySelectorAll(s));}return found},querySelector(s){return this.querySelectorAll(s)[0]||null},click(){this.onclick?.()},
 getContext(){return {createImageData(w,h){return {data:new Uint8ClampedArray(w*h*4)}},putImageData(){}}},toDataURL(){return 'data:image/png;base64,test'}};
 n.classList={add(s){n.className+=' '+s},remove(s){n.className=n.className.split(' ').filter(v=>v!==s).join(' ')},toggle(s,b){b?this.add(s):this.remove(s)}};all.push(n);return n;}
 const elements={};['.workspace','.tabs','.readme','.meta'].forEach(k=>elements[k]=element());const body=element('body');body.dataset.page=page;
 const context={console,setTimeout:queue,clearTimeout:id=>timers.delete(id),requestAnimationFrame:f=>f(),window:{innerWidth:width,innerHeight:900,addEventListener(){},matchMedia(){return {matches:true}}},document:{body,querySelector:s=>elements[s]||body.querySelector(s),createElement:element,createElementNS:(_,s)=>element(s)},echarts:{init(el){const c=echarts.init(null,null,{renderer:'svg',ssr:true,width,height:parseInt(el.style.height)||500});const resize=c.resize.bind(c);c.resize=()=>resize({width,height:parseInt(el.style.height)||500});made.push(c);return c;}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync('docs/assets/data/inclusive-data.js','utf8'),context);vm.runInContext(fs.readFileSync('docs/assets/js/chart-'+String(PAGES.indexOf(page)+1).padStart(2,'0')+'.js','utf8'),context);
 return {all,made,elements,context,advance(n){for(let i=0;i<n&&timers.size;i++){const [id,f]=timers.entries().next().value;timers.delete(id);f();}},check(){for(const c of made.filter(c=>!c.isDisposed())){const svg=c.renderToSVGString();assert(!svg.includes('NaN'),page+' invalid SVG');assert.equal(c.getOption().backgroundColor,'#fff');assert(c.getOption().toolbox[0].feature.saveAsImage);fs.writeFileSync(`.site-build/revision-${page}-${width}.svg`,svg);rendered++;}},dispose(){made.filter(c=>!c.isDisposed()).forEach(c=>c.dispose())}};
}

for(const page of PAGES.filter(p=>p!=='space')){
 const t=setup(page);t.check();
 for(const b of t.elements['.tabs'].children){b.click();t.check();
  const outer=t.elements['.workspace'].children.find(n=>n.className==='subtabs');
  if(outer)for(const sub of [...outer.children]){sub.click();t.check();
   const nested=t.elements['.workspace'].children.filter(n=>n.className==='subtabs'&&n!==outer);
   for(const nav of nested)for(const btn of [...nav.children]){btn.click();t.advance(60);t.check();}
  }
 }
 if(['qualityVitality','qualityMix','mismatch'].includes(page)){
  t.elements['.tabs'].children.at(-1).click();
  const nav=t.elements['.workspace'].children[0];
  vm.runInContext('D.points=[]',t.context);
  for(const b of nav.children){b.click();const below=t.elements['.workspace'].querySelector('.case-scatter');assert(below);assert.equal(below.parent.className,'case-layout');assert.equal(below.parent.children.length,2);assert.equal(below.parent.children[0].className,'case-photos');assert.equal(t.elements['.workspace'].querySelectorAll('.case-matrix').length,0);const xnav=below.children.find(n=>n.className.includes('case-x-tabs'));assert(xnav);assert.equal(below.querySelectorAll('select').length,0);
   for(const x of xnav.children){x.click();t.check();const c=t.made.filter(c=>!c.isDisposed()).at(-1),series=c.getOption().series;assert.equal(series.length,page==='qualityVitality'?7:6);assert(series.every(s=>s.type==='scatter'&&s.data.length<=nav.children.length&&s.label.show===false&&s.emphasis.label.show===false));for(const seriesItem of series)for(const datum of seriesItem.data){assert.equal(datum.itemStyle.borderWidth,0);assert(datum.value[0]>c.getOption().xAxis[0].min&&datum.value[0]<c.getOption().xAxis[0].max);assert.equal(datum.symbolSize,datum.value[2]===b.textContent?17:10);assert.equal(datum.itemStyle.opacity,datum.value[2]===b.textContent?1:.3);const tip=c.getOption().tooltip[0].formatter({data:datum,seriesName:seriesItem.name});assert(tip.includes(datum.value[2]));}if(['居民指数','游客指数'].includes(x.textContent))assert(series.every(s=>!s.data.length));else assert(series.some(s=>s.data.length===nav.children.length));}
  }
 }
 t.dispose();
}
console.log('Verified nested tabs, all 11 isolated cases and every case x-axis tab; '+rendered+' SVG chart renders.');

for(const [page,kind,count] of [['weights','quality',3],['memory','vitality',7],['composition','mix',6]]){
 const t=setup(page);t.elements['.tabs'].children[page==='memory'?0:1].click();
 const nav=t.elements['.workspace'].children.filter(n=>n.className==='subtabs').at(-1);nav.children[1].click();
 const c=t.made.filter(c=>!c.isDisposed()).at(-1),cards=t.elements['.workspace'].querySelectorAll('.metric-control');assert.equal(cards.length,count);assert(cards.every(card=>card.children[0].textContent===''&&card.children[0].attrs['aria-label']));
 for(const card of cards){card.children[0].click();t.advance(50);assert.equal(c.getOption().yAxis.filter(a=>a.show).length,1);assert(c.getOption().series.some(s=>String(s.id).startsWith('info-line')&&s.data.length));card.children[0].click();card.children[0].click();}
 t.check();fs.copyFileSync('.site-build/revision-'+page+'-1100.svg','.site-build/information-'+kind+'.svg');t.dispose();
}
{const t=setup('composition');const c=t.made.find(c=>!c.isDisposed());assert(c.getOption().yAxis[0].data.every(label=>Number(label.split('n=')[1])>=4));t.dispose();}
console.log('Verified n>=4 age filter and shared quality/vitality/mixing metric animations.');
