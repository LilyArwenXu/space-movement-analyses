const fs=require('fs'),vm=require('vm'),assert=require('assert');
const echarts=require('../spacemovement/echarts.min.js');
let count=0;
for(const page of [1,3,4,5,6,7,8]){
  const elements={};const created=[];
  function element(){return {children:[],style:{},attrs:{},append(x){this.children.push(x)},replaceChildren(){this.children=[]},setAttribute(k,v){this.attrs[k]=v},querySelectorAll(){return this.children},click(){this.onclick()},textContent:'',innerHTML:''};}
  for(const key of ['#workspace','nav','.note','h1','.meta'])elements[key]=element();
  const context={window:{},console,ResizeObserver:class{observe(){}},document:{body:{dataset:{study:page}},querySelector:s=>elements[s],createElement:element},echarts:{init(el){const c=echarts.init(null,null,{renderer:'svg',ssr:true,width:page===8?680:1360,height:parseInt(el.style.height)||650});created.push(c);return c;}}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('spacemovement/survey-data.js','utf8'),context);
  vm.runInContext(fs.readFileSync('spacemovement/studies.js','utf8'),context);
  const check=()=>{for(const c of created.filter(c=>!c.isDisposed())){const svg=c.renderToSVGString();assert(svg.includes('<path'),'empty chart');assert(!svg.includes('NaN'),'invalid geometry');
    c.getModel().eachSeries(series=>{
      if(series.subType==='line')assert.equal(series.option.lineStyle.opacity,.2,'regression lines should be faint');
      if(series.subType!=='heatmap')return;
      const data=series.getData();assert(data.count()>0,'heatmap has no cells');
      assert.equal(c.getOption().visualMap[0].dimension,2,'color must use the numeric value, not tooltip metadata');
      const fills=new Set();
      for(let i=0;i<data.count();i++){
        const fill=data.getItemVisual(i,'style').fill;
        assert(typeof fill==='string' && fill!=='none' && fill!=='transparent' && !fill.includes('NaN'),`invisible heatmap cell ${i}: ${fill}`);
        assert(data.getItemGraphicEl(i),'heatmap cell was not rendered');fills.add(fill);
      }
      if(series.name!=='地址位置')assert(fills.size>1,'different numeric values should have different shades');
    });
    if(page===1){
      const before=c.getOption(), series=c.getModel().getSeriesByIndex(1),data=series.getData();
      const coordinates=JSON.stringify(before.series[1].data.map(p=>p.slice(0,2)));
      assert.equal(before.series[0].data.length,context.window.SURVEY.nodes.length,'every address needs a fixed slot');
      const max=before.visualMap[0].max,low=Math.ceil(max/2);
      c.dispatchAction({type:'selectDataRange',visualMapIndex:0,selected:[low,max]});
      const filtered=c.getModel().getSeriesByIndex(1).getData();
      for(let j=0;j<filtered.count();j++)assert.equal(filtered.getItemVisual(j,'style').opacity,filtered.get('value',j)<low?0:1,'range must only hide cells outside selected population');
      assert.equal(JSON.stringify(c.getOption().series[1].data.map(p=>p.slice(0,2))),coordinates,'slider must not move addresses');
      assert.equal(JSON.stringify(c.getOption().grid),JSON.stringify(before.grid),'slider must not resize grid');
      c.dispatchAction({type:'selectDataRange',visualMapIndex:0,selected:[0,max]});
    }
    if(page===4){
      const data=c.getOption().series[0].data,fields=context.window.SURVEY.matrixFields;
      assert.equal(data.length,fields.length*(fields.length+1)/2,'complete triangular matrix');
      assert(data.every(p=>p[0]>=p[1]),'only one triangle should be populated');
      assert(data.filter(p=>p[0]===p[1]).every(p=>Math.abs(p[2]-1)<1e-10),'diagonal must show self correlation');
    }
    count++;} };
  check();
  for(const b of elements.nav.children.slice(1)){b.click();check();}
  if([5,6,8].includes(page)){vm.runInContext("highlight(D.streets[0]);highlight(null)",context);vm.runInContext("if(Math.abs(regression([[1,3],[2,5],[3,7]]).slope-2)>1e-10)throw Error('regression slope');if(regression([[1,3],[1,5]])!==null)throw Error('constant x');if(regression([[1,3],[2,3]]).r2!==null)throw Error('constant y');",context);}
  if(page===8)assert.equal(created.filter(c=>!c.isDisposed()).length,2);
  for(const c of created)if(!c.isDisposed())c.dispose();
}
{
const c=echarts.init(null,null,{renderer:'svg',ssr:true,width:1360,height:900});
const ctx={window:{addEventListener(){}},document:{getElementById(){return {}}},echarts:{init(){return c;}}};ctx.window.echarts=ctx.echarts;vm.createContext(ctx);
vm.runInContext(fs.readFileSync('spacemovement/monochrome.js','utf8'),ctx);
const html=fs.readFileSync('spacemovement/street_interface_weights.html','utf8');
for(const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))if(match[1].trim())vm.runInContext(match[1],ctx);
assert(c.renderToSVGString().includes('<path'));c.dispose();count++;
}
console.log(`Rendered ${count} chart states with ECharts SVG; all routes, tabs and street highlight calls passed.`);
