const fs=require('fs');
for(const file of ['aerial/assets/js/inclusive.js','chart_python/current/06_people_diversity_radar.py']){
 const source=fs.readFileSync(file,'utf8');
 const updated=source.replace(/function radar\([\s\S]*?(?=\nfunction scorePlot)/,s=>s
  .replaceAll("color:'#C6B8A7'","color:'#A4A6A7'")
  .replaceAll('color:PALETTE[j%5]',"color:g===groups[0]?'#FCB45E':'#292929'")
  .replace("opacity:j?.7:1,type:j?'solid':'dashed',width:j?1:2","opacity:1,type:g===groups[0]?'dashed':'solid',width:g===groups[0]?2:1"));
 if(updated===source)throw Error('Radar renderer not found: '+file);
 fs.writeFileSync(file,updated);
}
