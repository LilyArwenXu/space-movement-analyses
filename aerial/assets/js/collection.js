'use strict';
const DATA=window.INCLUSIVE, view=document.querySelector('.document-view'),buttons=document.querySelectorAll('.sidebar button');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function show(index){buttons.forEach((b,i)=>b.setAttribute('aria-selected',String(i===index)));view.replaceChildren();if(index===0){if(!DATA.pdfPages.length){view.textContent='目录文件暂未提供。';return;}DATA.pdfPages.forEach((src,i)=>{const img=document.createElement('img');img.className='pdf-page';img.src=src;img.alt='目录索引 第'+(i+1)+'页';img.loading=i?'lazy':'eager';view.append(img)});return;}
 const key=index===1?'space':'people',data=DATA.tables[key],tools=document.createElement('div');tools.className='sheet-tools';tools.innerHTML='<label>查找 <input type="search" placeholder="输入地址、点位或字段"></label><span></span>';view.append(tools);const host=document.createElement('div');host.className='sheet-table';view.append(host);
 function render(query=''){const rows=data.rows.map((r,i)=>({r,i})).filter(({r,i})=>!query||i<(key==='space'?3:1)||r.some(v=>String(v??'').toLowerCase().includes(query.toLowerCase())));tools.querySelector('span').textContent=(key==='space'?DATA.spaceSheet:DATA.peopleSheet)+' · '+rows.length+' 行（含表头）';host.innerHTML='<table><thead><tr><th>行</th>'+data.columns.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(({r,i})=>'<tr><th class="row-index">'+(i+1)+'</th>'+r.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';}
 tools.querySelector('input').addEventListener('input',e=>render(e.target.value));render();
}
buttons.forEach((b,i)=>b.onclick=()=>show(i));show(0);
