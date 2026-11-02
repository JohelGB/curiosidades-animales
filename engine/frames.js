// uso: node frames.js <workdir> t1 t2 ...  -> guarda <workdir>/frame_<t>.jpg
const {chromium}=require('playwright');const path=require('path');
const [wd,...ts]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(wd,'index.html'));await p.waitForTimeout(400);
for(const t of ts){await p.evaluate(x=>render(x),+t);await p.screenshot({path:path.join(wd,`frame_${t}.jpg`),type:'jpeg',quality:80});}
await b.close();})();
