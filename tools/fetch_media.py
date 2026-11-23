#!/usr/bin/env python3
"""Descarga fotos y videos reales con licencia libre de Wikimedia Commons.
Lee media/pedidos.txt (una línea por búsqueda):  <carpeta>|<búsqueda fotos>|<n fotos>|<n videos>|<búsqueda videos (opcional, p. ej. 'sloth')>
Guarda en media/<carpeta>/: f01.jpg… (fotos ≥1080 px), v01.mp4… (clips sin audio ≤8 s, 1080 px de alto) y creditos.json.
Una carpeta que ya existe no se vuelve a descargar. Corre en GitHub Actions (tiene internet y ffmpeg)."""
import json,os,re,subprocess,urllib.request,urllib.parse,sys,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));MED=os.path.join(ROOT,'media')
UA={'User-Agent':'curiosidades-animales-bot/1.0 (github.com/JohelGB/curiosidades-animales)'}
OK_LIC=re.compile(r'^(CC0|Public domain|PD|CC BY(-SA)? [0-9.]+|CC BY(-SA)?)',re.I)
BAD=re.compile(r'(map|range|distribution|skeleton|skull|fossil|diagram|logo|stamp|drawing|illustration|painting|svg|chart|museum|specimen|taxiderm|coat of arms)',re.I)
def api(**p):
    p.update(format='json',action='query')
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
def search(q,ftype,n):
    r=api(generator='search',gsrnamespace=6,gsrsearch=f'{q} filetype:{ftype}',gsrlimit=50,prop='imageinfo',
          iiprop='url|size|mime|extmetadata',iiurlwidth=1440)
    pages=sorted((r.get('query') or {}).get('pages',{}).values(),key=lambda p:p.get('index',99))
    out=[]
    for p in pages:
        ii=(p.get('imageinfo') or [{}])[0];md=ii.get('extmetadata',{})
        lic=md.get('LicenseShortName',{}).get('value','');t=p['title']
        if not OK_LIC.match(lic) or BAD.search(t): continue
        if ftype=='bitmap' and (ii.get('width',0)<1000 or ii.get('height',0)<700): continue
        art=re.sub('<[^>]+>','',md.get('Artist',{}).get('value','')).strip()[:120]
        out.append({'title':t,'url':ii.get('thumburl') if ftype=='bitmap' else ii['url'],'page':ii.get('descriptionurl'),'license':lic,'author':art,'duration':float(md.get('Duration',{}).get('value',0) or 0)})
        if len(out)>=n: break
    return out
def get(url,f):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120) as r,open(f,'wb') as fh: fh.write(r.read());return True
        except Exception as e: print('  reintento',e);time.sleep(5)
    return False
def main():
    ped=os.path.join(MED,'pedidos.txt')
    if not os.path.exists(ped): return
    for line in open(ped,encoding='utf-8'):
        line=line.strip()
        if not line or line.startswith('#'): continue
        parts=[x.strip() for x in line.split('|')]+['','','']
        slug,q=parts[0],parts[1];nf=int(parts[2] or 8);nv=int(parts[3] or 3)
        d=os.path.join(MED,slug)
        if os.path.exists(os.path.join(d,'creditos.json')): continue
        os.makedirs(d,exist_ok=True);cred=[];print('==',slug,q)
        for k,it in enumerate(search(q,'bitmap',nf),1):
            raw=os.path.join(d,'tmp');f=os.path.join(d,f'f{k:02d}.jpg')
            if get(it['url'],raw) and subprocess.run(['ffmpeg','-loglevel','error','-y','-i',raw,'-vf',"scale='min(1440,iw)':-2",'-q:v','3',f]).returncode==0:
                it['file']=os.path.basename(f);cred.append(it)
            if os.path.exists(raw): os.remove(raw)
        k=0;vq=parts[4] or q;vs=search(vq,'video',nv*3)
        if not vs: vs=search(vq.split()[0] if ' ' in vq else vq,'video',nv*3)
        print('  videos encontrados',len(vs))
        for it in vs:
            if k>=nv: break
            raw=os.path.join(d,'tmp.vid');f=os.path.join(d,f'v{k+1:02d}.mp4')
            if not get(it['url'],raw): continue
            ss=max(0,min(it['duration']/3,20)) if it['duration']>10 else 0
            r=subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(ss),'-i',raw,'-t','8','-an','-vf','scale=-2:1080,fps=30','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p',f])
            os.remove(raw)
            print('   video',it['title'][:60],'rc',r.returncode)
            if r.returncode==0 and os.path.exists(f) and os.path.getsize(f)>50000: k+=1;it['file']=os.path.basename(f);cred.append(it)
            elif os.path.exists(f): os.remove(f)
        # hoja de contacto para revisar qué salió
        imgs=sorted(x for x in os.listdir(d) if x.endswith('.jpg') and x.startswith('f'))
        vids=sorted(x for x in os.listdir(d) if x.endswith('.mp4'))
        thumbs=[]
        for x in imgs+vids:
            t=os.path.join(d,'_t_'+x+'.jpg')
            subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','1' if x.endswith('.mp4') else '0','-i',os.path.join(d,x),'-frames:v','1','-vf',f"scale=300:300:force_original_aspect_ratio=increase,crop=300:300,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{x}':x=8:y=8:fontsize=28:fontcolor=yellow:box=1:boxcolor=black",t])
            if os.path.exists(t): thumbs.append(t)
        if thumbs:
            cols=min(6,len(thumbs));rows=(len(thumbs)+cols-1)//cols
            inputs=sum([['-i',t] for t in thumbs],[])
            lay='|'.join(f'{(i%cols)*300}_{(i//cols)*300}' for i in range(len(thumbs)))
            subprocess.run(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',f'xstack=inputs={len(thumbs)}:layout={lay}:fill=black' if len(thumbs)>1 else 'null',os.path.join(d,'hoja.jpg')])
            for t in thumbs: os.remove(t)
        json.dump(cred,open(os.path.join(d,'creditos.json'),'w'),ensure_ascii=False,indent=1)
        print('  ',len(imgs),'fotos',len(vids),'videos')
main()
