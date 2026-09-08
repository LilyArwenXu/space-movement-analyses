'use strict';
const DATA=window.INCLUSIVE,view=document.querySelector('.document-view'),buttons=document.querySelectorAll('.sidebar button');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function show(index){buttons.forEach((b,i)=>b.setAttribute('aria-selected',String(i===index)));view.replaceChildren();if(index===0){DATA.pdfPages.forEach((src,i)=>{const img=document.createElement('img');img.className='pdf-page';img.src=src;img.alt='目录索引 第'+(i+1)+'页';img.loading=i?'lazy':'eager';view.append(img)});return;}
 const key=index===1?'space':'people',data=DATA.tables[key],tools=document.createElement('div');tools.className='sheet-tools';tools.innerHTML='<label>查找 <input type="search" placeholder="输入地址或字段"></label><span></span>';view.append(tools);const host=document.createElement('div');host.className='sheet-table';view.append(host);
 const covered=new Set(),starts=new Map();for(const [r,c,h,w] of data.merges){starts.set(r+','+c,[h,w]);for(let y=r;y<r+h;y++)for(let x=c;x<c+w;x++)if(y!==r||x!==c)covered.add(y+','+x);}
 function rowHTML(row,r){return '<tr>'+row.map((v,c)=>{if(covered.has(r+','+c))return '';const tag=r<data.headerRows?'th':'td',[h,w]=starts.get(r+','+c)||[1,1];return '<'+tag+' rowspan="'+h+'" colspan="'+w+'">'+esc(v)+'</'+tag+'>';}).join('')+'</tr>';}
 function render(query=''){const rows=data.rows.map((r,i)=>({r,i})).filter(({r,i})=>i>=data.headerRows&&(!query||r.some(v=>String(v??'').toLowerCase().includes(query.toLowerCase()))));tools.querySelector('span').textContent=(key==='space'?DATA.spaceSheet:DATA.peopleSheet)+' · '+rows.length+' 条记录';host.innerHTML='<table><thead>'+data.rows.slice(0,data.headerRows).map(rowHTML).join('')+'</thead><tbody>'+rows.map(({r,i})=>rowHTML(r,i)).join('')+'</tbody></table>';}
 tools.querySelector('input').addEventListener('input',e=>render(e.target.value));render();}
buttons.forEach((b,i)=>b.onclick=()=>show(i));show(0);
