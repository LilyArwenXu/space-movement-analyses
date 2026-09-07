const fs=require('fs');
for(const file of ['aerial/assets/js/inclusive.js','chart_python/current/01_address_people_heatmaps.py']){
 let s=fs.readFileSync(file,'utf8');
 s=s.replace('colors=[[21,35,52],[33,57,76],[62,87,108],[224,147,62],[252,180,94]]','colors=[[21,35,52],[79,71,63],[137,108,73],[194,144,84],[252,180,94]]');
 fs.writeFileSync(file,s);
}
