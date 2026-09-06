const fs=require('fs'),vm=require('vm'),assert=require('assert');
const echarts=require('../spacemovement/echarts.min.js');
fs.mkdirSync('.site-build',{recursive:true});
let rendered=0;
for(const page of [9,10,11,12,13,14,15,16]){
  const elements={},created=[];
  function element(){return {children:[],style:{},attrs:{},append(x){this.children.push(x)},replaceChildren(){this.children=[]},setAttribute(k,v){this.attrs[k]=v},querySelectorAll(){return this.children},click(){this.onclick()},textContent:'',innerHTML:''};}
  for(const key of ['#workspace','nav','.note','h1','.meta'])elements[key]=element();
  const context={window:{},console,ResizeObserver:class{observe(){}},document:{body:{dataset:{study:page}},querySelector:s=>elements[s],createElement:element},echarts:{init(el){const c=echarts.init(null,null,{renderer:'svg',ssr:true,width:1360,height:parseInt(el.style.height)||650});created.push(c);return c;}}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('spacemovement/people-data.js','utf8'),context);
  const routes={9:'people_composition',10:'people_diversity_radar',11:'behavior_lorenz',13:'point_diversity_ci',14:'people_space_correlations',15:'economic_exclusion',16:'local_memory_sankey'};
  const inline=routes[page]?fs.readFileSync('spacemovement/'+routes[page]+'.html','utf8').match(/<script>\s*([\s\S]*?)<\/script>/):null;
  vm.runInContext(inline?inline[1]:fs.readFileSync('spacemovement/people-studies.js','utf8'),context);
  let state=0;
  function check(){
    for(const c of created.filter(c=>!c.isDisposed())){
      const svg=c.renderToSVGString();assert(svg.includes('<path'));assert(!svg.includes('NaN'));
      fs.writeFileSync(`.site-build/people-${page}-${state}.svg`,svg);
      const o=c.getOption();
      if(page===14){assert(o.xAxis[0].data.concat(o.yAxis[0].data).every(s=>!s.includes('人数')));if(state===1)assert(!o.yAxis[0].data.some(s=>s.includes('争吵')));}
      if(page===15){const labels=o.xAxis[0].data;assert(!labels.includes('功能未记录'));assert(labels.every((s,i)=>!i||s.length>=labels[i-1].length));assert.equal(elements['.note'].textContent,'按功能类型汇总三个指标有效值均值。');}
      c.getModel().eachSeries(series=>{
        const d=series.getData();assert(d.count()>0);
        if(series.subType==='heatmap')for(let i=0;i<d.count();i++){
          assert.equal(typeof d.getItemVisual(i,'style').fill,'string','heat cells need numeric color mapping');
          assert(d.getItemGraphicEl(i),'missing heat cell');
        }
      });
      if(page===9&&o.series[0].type==='bar'){for(let i=0;i<o.series[0].data.length;i++)assert(Math.abs(o.series.reduce((sum,s)=>sum+s.data[i],0)-100)<1e-8);assert(o.series[0].markLine.data[0].xAxis>=0);}
      if(page===10){assert.equal(o.radar[0].indicator.length,5);if(state>0)assert.equal(o.series.length,1+context.window.PEOPLE.adminRoads[context.window.PEOPLE.admins[state-1].name].length);}
      if(page===11){assert.equal(o.series[1].data.length,15);assert.deepEqual(o.series[1].data[14],[1,1]);}
      if(page===12)assert.equal(o.series[0].data.length,111*4);
      if(page===13){assert.equal(o.series[0].data.length,48);assert.equal(o.series[1].type,'custom');assert(elements['#workspace'].children[1].innerHTML.includes('63'));assert(elements['.note'].textContent.includes('\n'));}
      if(page===14){assert(o.series[0].data.every(d=>!('q' in d.value[3])));assert(o.xAxis[0].data.every(v=>!v.includes('占比')));assert(o.yAxis[0].data.every(v=>!v.includes('占比')));if(state===0){assert.equal(o.xAxis[0].data.length,7);assert.equal(o.yAxis[0].data.length,15);}}
      if(page===15){assert.equal(o.yAxis.length,3);assert.equal(o.series.length,3);assert.equal(new Set(o.series.map(s=>s.itemStyle.opacity)).size,3);}
      if(page===16){assert.equal(o.series[0].type,'sankey');assert.equal(o.series[0].links.reduce((s,d)=>s+d.value,0),context.window.PEOPLE.memory[state].n);assert(elements['.note'].textContent.includes('非历史实测'));}
      rendered++;state++;
    }
  }
  check();for(const b of elements.nav.children.slice(1)){b.click();check();}
  for(const c of created)if(!c.isDisposed())c.dispose();
}
console.log(`Rendered and checked ${rendered} pedestrian chart states, including CI whiskers, five-axis radar, three-axis bars and scenario Sankey.`);
