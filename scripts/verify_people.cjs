const fs=require('fs'),vm=require('vm'),assert=require('assert');
const echarts=require('../spacemovement/echarts.min.js');
fs.mkdirSync('.site-build',{recursive:true});
let rendered=0;
for(const page of [9,10,11,12,13,14]){
  const elements={},created=[];
  function element(){return {children:[],style:{},attrs:{},append(x){this.children.push(x)},replaceChildren(){this.children=[]},setAttribute(k,v){this.attrs[k]=v},querySelectorAll(){return this.children},click(){this.onclick()},textContent:'',innerHTML:''};}
  for(const key of ['#workspace','nav','.note','h1','.meta'])elements[key]=element();
  const context={window:{},console,ResizeObserver:class{observe(){}},document:{body:{dataset:{study:page}},querySelector:s=>elements[s],createElement:element},echarts:{init(el){const c=echarts.init(null,null,{renderer:'svg',ssr:true,width:1360,height:parseInt(el.style.height)||650});created.push(c);return c;}}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('spacemovement/people-data.js','utf8'),context);
  vm.runInContext(fs.readFileSync('spacemovement/people-studies.js','utf8'),context);
  let state=0;
  function check(){
    for(const c of created.filter(c=>!c.isDisposed())){
      const svg=c.renderToSVGString();assert(svg.includes('<path'));assert(!svg.includes('NaN'));
      fs.writeFileSync(`.site-build/people-${page}-${state}.svg`,svg);
      const o=c.getOption();
      c.getModel().eachSeries(series=>{
        const d=series.getData();assert(d.count()>0);
        if(series.subType==='heatmap')for(let i=0;i<d.count();i++){
          assert.equal(typeof d.getItemVisual(i,'style').fill,'string','heat cells need numeric color mapping');
          assert(d.getItemGraphicEl(i),'missing heat cell');
        }
      });
      if(page===9){for(let i=0;i<o.series[0].data.length;i++)assert(Math.abs(o.series.reduce((sum,s)=>sum+s.data[i],0)-100)<1e-8);assert(o.series[0].markLine.data[0].xAxis>=0);}
      if(page===10)assert.equal(o.radar[0].indicator.length,4);
      if(page===11){assert.equal(o.series[1].data.length,15);assert.deepEqual(o.series[1].data[14],[1,1]);}
      if(page===12)assert.equal(o.series[0].data.length,111*4);
      if(page===13){assert.equal(o.series[0].data.length,19);assert.equal(o.series[1].type,'custom');assert(elements['#workspace'].children[1].innerHTML.includes('92'));}
      if(page===14)assert(o.series[0].data.every(d=>d.value[3].q!==null));
      rendered++;state++;
    }
  }
  check();for(const b of elements.nav.children.slice(1)){b.click();check();}
  for(const c of created)if(!c.isDisposed())c.dispose();
}
console.log(`Rendered and checked ${rendered} new chart states, including CI whiskers and FDR heatmap cells.`);
