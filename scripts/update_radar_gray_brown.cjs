const fs=require('fs');
for(const file of ['aerial/assets/js/inclusive.js','chart_python/current/06_people_diversity_radar.py']){
 const source=fs.readFileSync(file,'utf8');
 const updated=source.replace(/function radar\([\s\S]*?(?=\nfunction scorePlot)/,s=>s
  .replaceAll("color:'#A4A6A7'","color:'#C6B8A7'")
  .replaceAll("color:g===groups[0]?'#FCB45E':'#292929'","color:g===groups[0]?'#FCB45E':'#A4A6A7'"));
 if(updated===source)throw Error('Radar renderer not found: '+file);
 fs.writeFileSync(file,updated);
}
const test='scripts/verify_inclusive.cjs';
fs.writeFileSync(test,fs.readFileSync(test,'utf8')
 .replace("o.radar[0].splitLine.lineStyle.color,'#A4A6A7'","o.radar[0].splitLine.lineStyle.color,'#C6B8A7'")
 .replace("s.lineStyle.type==='dashed'?'#FCB45E':'#292929'","s.lineStyle.type==='dashed'?'#FCB45E':'#A4A6A7'"));
