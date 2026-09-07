const fs=require('fs');
for(const file of ['aerial/assets/js/inclusive.js','chart_python/current/01_address_people_heatmaps.py']){
 let s=fs.readFileSync(file,'utf8');
 s=s.replace('灰色表示人数少，橙色表示人数多','墨蓝色表示人数少，橙色表示人数多');
 s=s.replace("const tools=el('div','map-tools');let selected='AU';const pick=el('select','',tools);['AU','AV','AX','AY','BA','BB'].forEach(k=>{const option=el('option','',pick);option.value=k;option.textContent=D.headers[k]});if(mode===1)pick.hidden=true;", "const tools=el('div','map-tools activity-tabs');let selected='AU';if(mode===1)tools.hidden=true;tools.setAttribute('role','tablist');tools.setAttribute('aria-label','活动人数');");
 s=s.replace('colors=[[164,166,167],[182,175,167],[198,184,167],[225,182,130],[252,180,94]]','colors=[[21,35,52],[33,57,76],[62,87,108],[224,147,62],[252,180,94]]');
 s=s.replace('Math.min(.82,t*5)','Math.min(.72,t*8)');
 s=s.replace("pick.onchange=()=>{selected=pick.value;draw()};draw();if(mode)", "if(!mode){['AU','AV','AX','BA','AY','BB'].forEach(k=>{const b=el('button','',tools);b.textContent=D.headers[k];b.setAttribute('role','tab');b.setAttribute('aria-selected',String(k===selected));b.onclick=()=>{selected=k;tools.querySelectorAll('button').forEach(v=>v.setAttribute('aria-selected',String(v===b)));draw();};});}draw();if(mode)");
 fs.writeFileSync(file,s);
}
