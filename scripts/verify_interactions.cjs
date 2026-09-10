/* Exercise revised renderer state with the existing non-browser SSR harness. */
const source=require('fs').readFileSync('scripts/verify_revision.cjs','utf8').split('for(const page of PAGES)')[0]
 .replace('append(c){this.children.push(c)}','append(c){if(this.children.length)this.children.at(-1).nextElementSibling=c;this.children.push(c);c.parentElement=this},animate(){}')
 .replace('remove(){}','remove(){if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(c=>c!==this)}');
eval(source+String.raw`
for(const [page,kind,index,title] of [['weights','quality',2,'界面品质'],['composition','mix',2,'综合混合度'],['memory','vitality',1,'空间活力度']]){
 const t=setup(page);t.elements['.tabs'].children[index].click();
 let c=t.made.filter(c=>!c.isDisposed()).at(-1);
 assert.equal(c.getOption().xAxis[0].name,'所有点位（按'+title+'从低到高）');
 const nav=t.all.filter(n=>n.className==='subtabs').at(-1);nav.children[1].click();
 const controls=t.all.filter(n=>n.className==='metric-controls axis-controls').at(-1),button=controls.children[0].children[0];
 assert.equal(button.dataset.phase,'0');
 for(const phase of ['1','2','0']){button.click();assert.equal(button.dataset.phase,phase);}
 assert.equal(c.getOption().yAxis.filter(a=>a.show).length,controls.children.length);
 t.elements['.tabs'].children[page==='memory'?0:1].click();
 assert(t.all.find(n=>n.className==='critic-method').innerHTML.includes('C_j = S_j × R_j'));
 if(kind==='mix'){
  assert(t.all.find(n=>n.className==='coefficient-conclusion').textContent.includes('核心驱动要素。'));
  assert(t.elements['.readme'].textContent.includes('综合混合度（综合评分）'));
  t.elements['.tabs'].children[0].click();
  const sub=t.all.filter(n=>n.className==='subtabs').at(-1);
  for(let i=0;i<5;i++){sub.children[i].click();c=t.made.filter(c=>!c.isDisposed()).at(-1);assert.deepEqual(Array.from(c.getOption().yAxis[0].data),Array.from(t.context.window.INCLUSIVE.points,p=>p.address));assert(c.getOption().textStyle.fontFamily.startsWith('SimSun'));}
 }
 t.dispose();
}
const t=setup('mismatch');assert(t.all.find(n=>n.className==='mismatch-conclusion').textContent.split('\n').length===3);
t.elements['.tabs'].children[1].click();
const groups=t.elements['.workspace'].children.filter(n=>n.className==='mismatch-combined shap-gallery');assert.equal(groups.length,2);assert.equal(groups[0].children[0].textContent,'高混合度低活力度');assert.equal(groups[1].children[0].textContent,'高活力度低混合度');
groups.forEach(g=>{assert.equal(g.children[1].children.length,3);g.children[1].children.forEach(f=>{assert.equal(f.children.length,1);assert.equal(f.children[0].tag,'img');});});t.dispose();
console.log('Verified five address axes, three button cycles and axis titles, CRITIC content, Song chart fonts and six combined SHAP images.');
`);
