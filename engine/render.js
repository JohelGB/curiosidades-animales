// uso: node render.js <workdir> <duracion_s> <salida.mp4>
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const [wd,durS,out]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(wd,'index.html'));await p.waitForTimeout(400);
const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
const N=Math.ceil(+durS*30);for(let i=0;i<N;i++){await p.evaluate(x=>render(x),i/30);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();ff.on('close',c=>{b.close();process.exit(c)});})();
