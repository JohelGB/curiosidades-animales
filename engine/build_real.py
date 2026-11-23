#!/usr/bin/env python3
"""Video con FOTOS y CLIPS REALES (media/ de Wikimedia Commons) + narración + subtítulos palabra por palabra.
uso: python3 engine/build_real.py specs/<slug>.json            -> videos/<slug>.mp4
     python3 engine/build_real.py specs/<slug>.json --frames   -> work/<slug>/sheet.jpg (un cuadro por escena)
spec: {"slug","style":"real","rate":"+12%","caption","title","ytTitle",
       "scenes":[{"media":"media/<carpeta>/f03.jpg"|"…/v01.mp4","narration":"…","text":"(opcional) titular arriba",
                  "badge":"(opcional) cifra grande","move":"in|out|left|right|up (fotos)","start":0 (seg. del clip)}, …,
                 {"cta":true,"narration":"Síguenos para más curiosidades animales.","media":"…"}]}
"""
import json,os,sys,subprocess,re,asyncio,time,wave
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageFont
ENG=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(ENG)
spec_path=sys.argv[1];frames_only='--frames' in sys.argv
spec=json.load(open(spec_path));slug=spec['slug']
wd=os.path.join(ROOT,'work',slug);os.makedirs(wd,exist_ok=True)
voice=spec.get('voice','es-MX-JorgeNeural');rate=spec.get('rate','+12%')
W,H,FPS=1080,1920,30;XF=0.35
os.environ['NO_PROXY']='';os.environ['no_proxy']=''
def dur(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# ---------- 1) voz con tiempos por palabra ----------
async def tts_words(text,f):
    import edge_tts
    c=edge_tts.Communicate(text,voice,rate=rate,boundary='WordBoundary');wb=[];sb=[]
    with open(f,'wb') as fh:
        async for ch in c.stream():
            if ch['type']=='audio':fh.write(ch['data'])
            elif ch['type']=='WordBoundary':wb.append({'w':ch['text'],'o':ch['offset']/1e7,'d':ch['duration']/1e7})
            elif ch['type']=='SentenceBoundary':sb.append((ch['offset']/1e7,ch['duration']/1e7,ch['text']))
    if wb:return wb
    ws=[]
    for o,d,tx in sb:
        toks=tx.split();wts=[len(t)+2 for t in toks];tot=sum(wts) or 1;acc=0
        for t,wt in zip(toks,wts):ws.append({'w':t,'o':o+d*acc/tot,'d':d*wt/tot});acc+=wt
    return ws
scenes=spec['scenes'];ds=[];wbs=[]
for i,sc in enumerate(scenes):
    f=os.path.join(wd,f'v{i}.mp3');wf=os.path.join(wd,f'v{i}.json')
    if not (os.path.exists(f) and os.path.getsize(f)>0 and os.path.exists(wf)):
        for k in range(4):
            try:ws=asyncio.run(tts_words(sc['narration'].replace('*',''),f));break
            except Exception:
                if k==3:raise
                time.sleep(3)
        json.dump(ws,open(wf,'w'))
    wbs.append(json.load(open(wf)));ds.append(dur(f))
# ---------- 2) tiempos ----------
PAD=0.3;t=0.0;starts=[]
for i,(sc,d) in enumerate(zip(scenes,ds)):
    v0=t+(0.25 if i==0 else 0.1);sc['v']=v0;starts.append(v0)
    sc['s']=t;sc['e']=v0+d+PAD+(1.3 if sc.get('cta') else 0);t=sc['e']
D=scenes[-1]['e'];NF=int(D*FPS)
# ---------- 3) fuentes de imagen ----------
def cover(img,w=W,h=H,extra=1.0):
    s=max(w/img.width,h/img.height)*extra;return img.resize((max(1,round(img.width*s)),max(1,round(img.height*s))),Image.LANCZOS)
class Photo:
    def __init__(s,path,move,dur_):
        im=Image.open(os.path.join(ROOT,path)).convert('RGB');s.big=cover(im,extra=1.22);s.move=move;s.d=dur_
    def frame(s,tt):
        p=min(max(tt/s.d,0),1);p=p*p*(3-2*p)  # suave
        bw,bh=s.big.size;z={'in':1+0.16*p,'out':1.16-0.16*p}.get(s.move,1.08)
        cw,ch=bw/z,bh/z
        cx,cy=bw/2,bh/2
        if s.move=='left':cx=bw/2+(bw-cw)/2*(0.9-1.8*p)
        if s.move=='right':cx=bw/2-(bw-cw)/2*(0.9-1.8*p)
        if s.move=='up':cy=bh/2+(bh-ch)/2*(0.9-1.8*p)
        x0,y0=cx-cw/2,cy-ch/2;sx=cw/W
        return np.asarray(s.big.transform((W,H),Image.AFFINE,(sx,0,x0,0,sx,y0),resample=Image.BICUBIC))
class Clip:
    def __init__(s,path,start,dur_):
        s.path=os.path.join(ROOT,path);s.start=start;s.d=dur_;s.p=None;s.n=0;s.last=None
        s.src=dur(s.path)
    def _open(s):
        vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        s.p=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',str(s.start),'-stream_loop','-1','-i',s.path,'-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    def frame(s,tt):
        if s.p is None:s._open()
        want=int(tt*FPS)
        while s.n<=want:
            b=s.p.stdout.read(W*H*3)
            if len(b)<W*H*3:break
            s.last=np.frombuffer(b,np.uint8).reshape(H,W,3);s.n+=1
        a=s.last;z=1+0.05*min(tt/max(s.d,0.1),1)  # leve zoom para que respire
        if a is None:return np.zeros((H,W,3),np.uint8)
        im=Image.fromarray(a);cw,ch=W/z,H/z
        return np.asarray(im.transform((W,H),Image.AFFINE,(1/z,0,(W-cw)/2,0,1/z,(H-ch)/2),resample=Image.BILINEAR))
    def close(s):
        if s.p:s.p.kill()
logo=Image.open(os.path.join(ENG,'logo.png')).convert('RGBA')
def src_for(i):
    sc=scenes[i];m=sc.get('media') or scenes[i-1].get('media');d=sc['e']-sc['s']+XF
    if m.endswith('.mp4'):return Clip(m,sc.get('start',0),d)
    return Photo(m,sc.get('move',['in','left','out','right','up'][i%5]),d)
def cta_frame(base,tt):
    im=Image.fromarray(base).filter(ImageFilter.GaussianBlur(18));im=Image.blend(im,Image.new('RGB',(W,H),(0,0,0)),0.45)
    k=min(tt/0.5,1);k=1-(1-k)**3;s=int(620*(0.7+0.3*k));lg=logo.resize((s,s),Image.LANCZOS)
    im.paste(lg,((W-s)//2,(H-s)//2-160),lg);return np.asarray(im)
# ---------- 4) subtítulos ASS (palabra por palabra) ----------
def ass_t(x):x=max(x,0);return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
def esc(s):return s.replace('{','(').replace('}',')').replace('\\','')
hdr=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Top,Poppins,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,3,22,0,8,70,70,190,1
Style: Badge,Poppins,120,&H0000E1FF,&H0000E1FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,9,4,8,60,60,430,1
Style: Cred,Poppins,30,&H00DDDDDD,&H00DDDDDD,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,40,40,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[];YEL='&H0000E1FF&'
for i,sc in enumerate(scenes):
    ws=[w for w in wbs[i] if re.sub(r'[^\wáéíóúñü]','',w['w'].lower())]
    if sc.get('text'):ev.append(f"Dialogue: 1,{ass_t(sc['s']+0.1)},{ass_t(sc['e'])},Top,,0,0,0,,{{\\fad(150,120)}}{esc(sc['text'])}")
    if sc.get('badge'):ev.append(f"Dialogue: 2,{ass_t(sc['v'])},{ass_t(sc['e'])},Badge,,0,0,0,,{{\\fad(100,150)\\fscx60\\fscy60\\t(0,220,\\fscx100\\fscy100)}}{esc(sc['badge'])}")
    if sc.get('cta'):continue
    # trozos de hasta 3 palabras (corta en puntuación)
    chunks=[];cur=[]
    for w in ws:
        cur.append(w)
        if len(cur)==3 or re.search(r'[,.;:?!…]$',w['w']):chunks.append(cur);cur=[]
    if cur:chunks.append(cur)
    for ci,ch in enumerate(chunks):
        for wi,w in enumerate(ch):
            a=sc['v']+w['o'];b=sc['v']+(ch[wi+1]['o'] if wi+1<len(ch) else (chunks[ci+1][0]['o'] if ci+1<len(chunks) else ds[i]+0.25))
            parts=[(f"{{\\c{YEL}\\fscx108\\fscy108}}" if k==wi else "")+esc(x['w'].upper())+("{\\c&H00FFFFFF&\\fscx100\\fscy100}" if k==wi else "") for k,x in enumerate(ch)]
            pop="{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}" if wi==0 else ""
            ev.append(f"Dialogue: 0,{ass_t(a)},{ass_t(b)},Cap,,0,0,0,,{{\\pos({W//2},{int(H*0.66)})}}{pop}{' '.join(parts)}")
cred=spec.get('credit','Imágenes: Wikimedia Commons (licencias libres)')
ev.append(f"Dialogue: 0,{ass_t(scenes[-1]['s'])},{ass_t(D)},Cred,,0,0,0,,{esc(cred)}")
ass=os.path.join(wd,'subs.ass');open(ass,'w',encoding='utf-8').write(hdr+'\n'.join(ev)+'\n')
FONTS='/usr/share/fonts/truetype/google-fonts'
# ---------- 5) render de cuadros ----------
def scene_at(t_):
    for i,sc in enumerate(scenes):
        if t_<sc['e']:return i
    return len(scenes)-1
srcs={}
def get_src(i):
    if i not in srcs:srcs[i]=src_for(i)
    return srcs[i]
def frame_at(t_):
    i=scene_at(t_);sc=scenes[i]
    base=get_src(i).frame(t_-sc['s'])
    if sc.get('cta'):base=cta_frame(base,t_-sc['s'])
    # cruce suave con la escena siguiente al final de esta
    if i+1<len(scenes) and t_>sc['e']-XF:
        a=(t_-(sc['e']-XF))/XF;n2=scenes[i+1];nx=get_src(i+1).frame(t_-n2['s'])
        if n2.get('cta'):nx=cta_frame(nx,0)
        base=(base*(1-a)+nx*a).astype(np.uint8)
    for k in [k for k in srcs if k<i-1]:
        try:srcs[k].close()
        except Exception:pass
        del srcs[k]
    return base
if frames_only:
    mids=[(sc['s']+sc['e'])/2 for sc in scenes];paths=[]
    for k,m in enumerate(mids):
        srcs.clear();fr=frame_at(m);p=os.path.join(wd,f'f{k}.png');Image.fromarray(fr).save(p)
        q=os.path.join(wd,f'fs{k}.jpg')
        # el filtro subtitles usa el tiempo del cuadro: renderizamos con -itsoffset
        subprocess.run(['ffmpeg','-loglevel','error','-y','-itsoffset',str(m),'-loop','1','-t','0.1','-i',p,'-vf',f"subtitles={ass}:fontsdir={FONTS}",'-ss',str(m),'-frames:v','1',q],check=True)
        paths.append(q)
    subprocess.run(['ffmpeg','-loglevel','error','-y']+sum([['-i',p] for p in paths],[])+['-filter_complex',f'hstack={len(paths)},scale={360*len(paths)}:-1',os.path.join(wd,'sheet.jpg')],check=True)
    print('sheet',os.path.join(wd,'sheet.jpg'),'duración',round(D,1),'s');sys.exit(0)
vid=os.path.join(wd,'video_tmp.mp4')
enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
     '-vf',f"subtitles={ass}:fontsdir={FONTS}",'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',vid],stdin=subprocess.PIPE)
for n in range(NF):enc.stdin.write(frame_at(n/FPS).tobytes())
enc.stdin.close();enc.wait()
for s in srcs.values():
    try:s.close()
    except Exception:pass
# ---------- 6) música suave + mezcla ----------
sr=44100;n=int(sr*D);out=np.zeros(n);tt=np.arange(n)/sr
chords=[[220.0,261.63,329.63],[174.61,220.0,261.63],[196.0,246.94,293.66],[164.81,196.0,246.94]];bar=2.4
for k in range(int(D/bar)+1):
    i0=int(k*bar*sr);m=min(int(bar*1.3*sr),n-i0)
    if m<=0:break
    t2=np.arange(m)/sr;env=np.minimum(t2/0.6,1)*np.exp(-t2*0.5)
    for f in chords[k%4]:out[i0:i0+m]+=0.05*np.sin(2*np.pi*f*t2)*env+0.02*np.sin(2*np.pi*2*f*t2)*env
pulse=(np.sin(2*np.pi*tt/(bar/4))>0.97).astype(float);out+=0.04*np.convolve(pulse,np.exp(-np.arange(2000)/300),'same')*np.sin(2*np.pi*55*tt)
fo=int(1.5*sr);out[-fo:]*=np.linspace(1,0,fo);out=out/np.max(np.abs(out))*0.6
wf_=wave.open(os.path.join(wd,'music.wav'),'w');wf_.setnchannels(1);wf_.setsampwidth(2);wf_.setframerate(sr);wf_.writeframes((out*32767).astype(np.int16).tobytes());wf_.close()
os.makedirs(os.path.join(ROOT,'videos'),exist_ok=True);final=os.path.join(ROOT,'videos',f'{slug}.mp4');tmp=final+'.part.mp4'
cmd=['ffmpeg','-loglevel','error','-y','-i',vid,'-i',os.path.join(wd,'music.wav')];flt=''
for i,s in enumerate(starts):
    cmd+=['-i',os.path.join(wd,f'v{i}.mp3')];ms=int(s*1000);flt+=f'[{i+2}:a]adelay={ms}|{ms}[a{i}];'
flt+='[1:a]volume=0.25[m];[m]'+''.join(f'[a{i}]' for i in range(len(starts)))+f'amix=inputs={len(starts)+1}:normalize=0,alimiter=limit=0.95[aout]'
cmd+=['-filter_complex',flt,'-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','160k','-shortest',tmp]
subprocess.run(cmd,check=True);os.replace(tmp,final)
print('OK',final,round(D,2),'s')
