#!/usr/bin/env python3
"""Construye un video a partir de un spec JSON.
uso: python3 engine/build.py specs/<slug>.json            -> videos/<slug>.mp4
     python3 engine/build.py specs/<slug>.json --frames    -> solo cuadros de prueba en work/<slug>/
"""
import json,os,sys,subprocess,shutil,wave
import numpy as np
ENG=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(ENG)
spec_path=sys.argv[1];frames_only='--frames' in sys.argv
spec=json.load(open(spec_path));slug=spec['slug']
wd=os.path.join(ROOT,'work',slug);os.makedirs(wd,exist_ok=True)
voice=spec.get('voice','es-MX-JorgeNeural');rate=spec.get('rate','+8%')
os.environ['NO_PROXY']='';os.environ['no_proxy']='';env=dict(os.environ)
def dur(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# 1) voz por escena (+ tiempos de cada palabra para subtitulos)
import re,asyncio
style=spec.get('style','classic')
def clean(t):return t.replace('*','')
async def tts_words(text,f):
    import edge_tts
    c=edge_tts.Communicate(text,voice,rate=rate);sb=[]
    with open(f,'wb') as fh:
        async for ch in c.stream():
            if ch['type']=='audio':fh.write(ch['data'])
            elif ch['type']=='SentenceBoundary':sb.append((ch['offset']/1e7,ch['duration']/1e7,ch['text']))
    # tiempos por palabra estimados dentro de cada oracion (peso = letras + pausa por puntuacion)
    ws=[]
    for o,d,tx in sb:
        toks=[t for t in tx.split() if re.sub(r'[^\w]','',t)]
        wts=[len(re.sub(r'[^\w]','',t))+2+(4 if re.search(r'[,:;.?!]$',t) else 0) for t in toks];tot=sum(wts) or 1;acc=0
        for t,wt in zip(toks,wts):
            ws.append({'w':re.sub(r'[¿?¡!.,:;]','',t),'o':o+d*acc/tot,'d':d*wt/tot});acc+=wt
    return ws
ds=[];wbs=[]
for i,sc in enumerate(spec['scenes']):
    f=os.path.join(wd,f'v{i}.mp3');wf=os.path.join(wd,f'v{i}.json')
    if not os.path.exists(f) or os.path.getsize(f)==0 or not os.path.exists(wf):
        import time
        for _try in range(4):
            try: ws=asyncio.run(tts_words(clean(sc['narration']),f));break
            except Exception as ex:
                if _try==3: raise
                time.sleep(3)
        json.dump(ws,open(wf,'w'))
    wbs.append(json.load(open(wf)));ds.append(dur(f))
# 2) tiempos
PAD=0.55;t=0.3;starts=[]
for i,(sc,d) in enumerate(zip(spec['scenes'],ds)):
    s=0 if i==0 else t;e=t+d+PAD+(1.2 if i==len(ds)-1 else 0);sc['s']=round(s,3);sc['e']=round(e,3)
    st0=0.3 if i==0 else s;starts.append(st0)
    hlset={re.sub(r'[^\wáéíóúñü]','',x.lower()) for x in re.findall(r'\*([^*]+)\*',sc['narration']) for x in x.split()}
    sc['words']=[{'w':w['w'],'s':round(st0+w['o'],3),'hl':re.sub(r'[^\wáéíóúñü]','',w['w'].lower()) in hlset,'first':j==0} for j,w in enumerate(wbs[i])]
    t=e
D=spec['scenes'][-1]['e']
# 3) pagina
shutil.copy(os.path.join(ENG,'blueprint.html' if style=='blueprint' else 'template.html'),os.path.join(wd,'index.html'));shutil.copy(os.path.join(ENG,'logo.png'),os.path.join(wd,'logo.png'))
open(os.path.join(wd,'spec.js'),'w').write('window.SPEC='+json.dumps(spec,ensure_ascii=False)+';')
if frames_only:
    mids=[round((sc['s']+sc['e'])/2,2) for sc in spec['scenes']]
    subprocess.run(['node',os.path.join(ENG,'frames.js'),wd]+[str(m) for m in mids],check=True)
    subprocess.run(['ffmpeg','-loglevel','error','-y']+sum([['-i',os.path.join(wd,f'frame_{m}.jpg')] for m in mids],[])+['-filter_complex',f'hstack={len(mids)},scale={360*len(mids)}:-1',os.path.join(wd,'sheet.jpg')],check=True)
    print('sheet',os.path.join(wd,'sheet.jpg'));sys.exit(0)
# 4) musica
sr=44100;n=int(sr*D);out=np.zeros(n)
def pluck(f,t0,dd=0.6,vol=0.25):
    i0=int(t0*sr);m=int(dd*sr);tt=np.arange(m)/sr
    s=(np.sin(2*np.pi*f*tt)+0.35*np.sin(4*np.pi*f*tt)+0.12*np.sin(6*np.pi*f*tt))*np.exp(-tt*6)*vol
    e=min(n,i0+m);out[i0:e]+=s[:e-i0]
beat=60/104;scale=[261.63,293.66,329.63,392.0,440.0,523.25,587.33]
chords=[[130.81,196.0],[110.0,164.81],[87.31,130.81],[98.0,146.83]];mel=[0,2,4,2,5,4,2,1,0,2,4,5,6,5,4,2]
k=0;tt0=0.0
while tt0<D-1:
    if (k%8)==0:
        for f in chords[(k//8)%4]:pluck(f,tt0,1.6,0.18)
    if k%3!=1:pluck(scale[mel[k%16]]*2,tt0,0.45,0.10)
    k+=1;tt0+=beat/2
for sc in spec['scenes']:
    i0=int(sc['s']*sr);m=int(0.12*sr);tt=np.arange(m)/sr;f=600+2400*np.exp(-tt*40)
    seg=np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt*30)*0.35;out[i0:i0+m]+=seg[:len(out[i0:i0+m])]
fo=int(1.5*sr);out[-fo:]*=np.linspace(1,0,fo);out=out/np.max(np.abs(out))*0.6
w=wave.open(os.path.join(wd,'music.wav'),'w');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
# 5) render
vid=os.path.join(wd,'video_tmp.mp4')
subprocess.run(['node',os.path.join(ENG,'render.js'),wd,str(D),vid],check=True)
# 6) mezcla
os.makedirs(os.path.join(ROOT,'videos'),exist_ok=True);final=os.path.join(ROOT,'videos',f'{slug}.mp4');tmp=final+'.part.mp4'
cmd=['ffmpeg','-loglevel','error','-y','-i',vid,'-i',os.path.join(wd,'music.wav')];flt=''
for i,s in enumerate(starts):
    cmd+=['-i',os.path.join(wd,f'v{i}.mp3')];ms=int(s*1000);flt+=f'[{i+2}:a]adelay={ms}|{ms}[a{i}];'
flt+='[1:a]volume=0.22[m];[m]'+''.join(f'[a{i}]' for i in range(len(starts)))+f'amix=inputs={len(starts)+1}:normalize=0,alimiter=limit=0.95[aout]'
cmd+=['-filter_complex',flt,'-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','160k','-shortest',tmp]
subprocess.run(cmd,check=True);os.replace(tmp,final)
print('OK',final,round(D,2),'s')
