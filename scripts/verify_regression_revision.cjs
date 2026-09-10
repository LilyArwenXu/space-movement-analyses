const fs=require('fs'),path=require('path'),crypto=require('crypto');
const source=fs.readFileSync('scripts/verify_revision.cjs','utf8').split('for(const page of PAGES)')[0]
 .replace("'qualityMix','mismatch']","'qualityMix','mismatch','mixRegression']")
 .replace('append(c){this.children.push(c)}','append(c){if(this.children.length)this.children.at(-1).nextElementSibling=c;this.children.push(c);c.parentElement=this},animate(){},after(c){const p=this.parentElement,i=p.children.indexOf(this);p.children.splice(i+1,0,c);c.parentElement=p}')
 .replace('remove(){}','remove(){if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(c=>c!==this)}')
 .replace("vm.createContext(context);","vm.createContext(context);vm.runInContext(fs.readFileSync('docs/assets/data/shap-captions.js','utf8'),context);");
eval(source+String.raw`
const t=setup('composition');assert.equal(t.elements['.tabs'].children.length,5);
for(let i=0;i<5;i++){t.elements['.tabs'].children[i].click();const c=t.made.filter(c=>!c.isDisposed()).at(-1);assert.deepEqual(Array.from(c.getOption().yAxis[0].data),Array.from(t.context.window.INCLUSIVE.points,p=>p.address));assert(c.getOption().textStyle.fontFamily.startsWith('SimSun'));}t.dispose();
for(const [page,tabIndex] of [['mixRegression',0],['weights',1],['memory',0]]){const t=setup(page);t.elements['.tabs'].children[tabIndex].click();const method=t.all.filter(n=>n.className==='critic-method').at(-1);assert.equal(method.tag,'details');assert(!method.open);assert(method.innerHTML.includes('<summary>Critic权重算法</summary>'));if(page==='mixRegression'){assert.equal(t.elements['.tabs'].children.length,2);assert.equal(t.elements['.tabs'].children[1].textContent,'混合度总表');}t.dispose();}
for(const page of ['qualityVitality','qualityMix','mismatch']){const t=setup(page),c=t.made.filter(c=>!c.isDisposed()).at(-1),pairs={qualityVitality:['quality','vitality'],qualityMix:['quality','mixScore'],mismatch:['vitality','mixScore']}[page],means=t.context.window.INCLUSIVE.scoreMeans;const marks=c.getOption().series[0].markLine.data;assert.equal(marks[0].xAxis,means[pairs[0]]);assert.equal(marks[1].yAxis,means[pairs[1]]);assert.equal(c.getOption().series[0].data.length,135);
t.elements['.tabs'].children[1].click();const nav=t.elements['.workspace'].children.find(n=>n.className==='subtabs');assert.equal(nav.children.length,2);for(const b of nav.children){b.click();const gallery=t.elements['.workspace'].children.find(n=>n.className==='shap-gallery');assert.equal(gallery.children.length,3);gallery.children.forEach(figure=>{const row=figure.children[0];assert.equal(row.className,'shap-row');assert.equal(row.children[1].children[0].className,'shap-description');assert.equal(row.children[1].children[1].className,'shap-conclusion');assert(row.children[1].children[1].textContent.startsWith('结论：'));});}t.dispose();}
console.log('Verified five population tabs, isolated regression tabs, collapsed methods, CSV mean axes, and six SHAP side-by-side layouts.');
`);
const digest=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
for(const folder of fs.readdirSync('result/shap',{withFileTypes:true}).filter(d=>d.isDirectory()))for(const name of ['1.png','2.png','3.png']){
 const source=path.join('result/shap',folder.name,name);for(const site of ['aerial','dist','docs'])if(digest(source)!==digest(path.join(site,'assets/data/shap',folder.name,name)))throw Error('SHAP image mismatch: '+folder.name+'/'+name);
}
console.log('All 18 SHAP images match the updated source files in all website copies.');
