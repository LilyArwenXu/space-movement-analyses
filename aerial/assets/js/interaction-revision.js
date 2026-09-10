document.addEventListener('click',event=>{
 const link=event.target.closest('a.portal');if(!link||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 link.classList.add('is-entering');if(link.target==='_blank'){setTimeout(()=>link.classList.remove('is-entering'),350);return;}
 event.preventDefault();setTimeout(()=>window.location.assign(link.href),window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:170);
});window.addEventListener('pageshow',()=>document.querySelectorAll('.is-entering').forEach(n=>n.classList.remove('is-entering')));
document.addEventListener('click',event=>{const tab=event.target.closest('[role="tab"]');if(!tab||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;const host=document.getElementById(tab.getAttribute('aria-controls'))||document.querySelector('.workspace');host?.animate([{opacity:.65,transform:'translateY(3px)'},{opacity:1,transform:'translateY(0)'}],{duration:230,easing:'ease-out'});});
window.exportAnnotatedChart=async(c,node)=>{
 await document.fonts.load('300 16px FZLanTingHei');
 const image=new Image();image.src=c.getDataURL({type:'png',pixelRatio:2,backgroundColor:'#fff',excludeComponents:['toolbox']});await image.decode();
 const caption=[...new Set([...node.parentElement.querySelectorAll('.caption'),document.querySelector('.readme')].filter(n=>n&&!n.hidden).map(n=>n.textContent.trim()).filter(Boolean))].join('\n\n');
 const width=c.getWidth(),padding=24,canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
 ctx.font='300 16px FZLanTingHei, SimHei, sans-serif';const lines=[];
 caption.split('\n').forEach(paragraph=>{let line='';for(const char of paragraph){if(line&&ctx.measureText(line+char).width>width-padding*2){lines.push(line);line=char;}else line+=char;}lines.push(line);});
 const chartHeight=image.height/2;canvas.width=image.width;canvas.height=Math.ceil((chartHeight+(caption?padding*2+lines.length*26:0))*2);ctx.scale(2,2);ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width/2,canvas.height/2);ctx.drawImage(image,0,0,width,chartHeight);ctx.font='300 16px FZLanTingHei, SimHei, sans-serif';ctx.fillStyle='#000';ctx.textBaseline='top';if(caption)lines.forEach((line,i)=>ctx.fillText(line,padding,chartHeight+padding+i*26));
 const a=document.createElement('a');a.download=document.title.split('｜')[0]+'.png';a.href=canvas.toDataURL('image/png');a.click();
};
