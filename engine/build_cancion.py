#!/usr/bin/env python3
"""Video estilo CANCIÓN (rima al ritmo, karaoke, animal que baila, aplausos, adivinanza).
uso: python3 engine/build_cancion.py specs/<slug>.json [--frames]
Spec: ver CLAUDE.md, sección "Estilo canción".
"""
import json, os, sys, re, subprocess, shutil, wave, asyncio, time, math
import numpy as np
os.environ['NO_PROXY'] = ''; os.environ['no_proxy'] = ''
ENG = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(ENG)
spec_path = sys.argv[1]; frames_only = '--frames' in sys.argv
spec = json.load(open(spec_path)); slug = spec['slug']
wd = os.path.join(ROOT, 'work', slug); os.makedirs(wd, exist_ok=True)
voice = spec.get('voice', 'es-MX-JorgeNeural'); rate = spec.get('rate', '+12%')
BPM = spec.get('bpm', 104); BEAT = 60 / BPM; BAR = 4 * BEAT
SR = 44100

def run(c): subprocess.run(c, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
def clean(t): return t.replace('*', '')

async def _tts(text, f):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(f)
def tts(text, f):
    for k in range(4):
        try: asyncio.run(_tts(text, f)); return
        except Exception:
            if k == 3: raise
            time.sleep(3)

# ---- 1) voz por línea, recortada y ajustada al compás ----
cache = {}; t = BAR  # 1 compás de intro (título + ritmo)
for i, ln in enumerate(spec['lines']):
    key = clean(ln['text'])
    if key not in cache:
        raw = os.path.join(wd, f'raw{len(cache)}.mp3'); trimmed = os.path.join(wd, f'l{len(cache)}.wav')
        tts(key, raw)
        run(['ffmpeg', '-y', '-i', raw, '-af', 'silenceremove=start_periods=1:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse', '-ar', str(SR), '-ac', '1', trimmed])
        d = dur(trimmed)
        bars = 1 if d <= BAR * 1.12 else 2
        target = bars * BAR * 0.9
        if d > target:
            tempo = min(1.5, d / target); fixed = trimmed.replace('.wav', 'f.wav')
            run(['ffmpeg', '-y', '-i', trimmed, '-af', f'atempo={tempo:.4f}', fixed]); trimmed = fixed; d = dur(trimmed)
        cache[key] = (trimmed, d, bars)
    f, d, bars = cache[key]
    ln['audio'] = f; ln['vd'] = d
    ln['s'] = round(t, 3); vs = t + 0.04
    toks = clean(ln['text']).split(); hlw = set()
    for grp in re.findall(r'\*([^*]+)\*', ln['text']):
        hlw |= {re.sub(r'[^\wáéíóúñü]', '', x.lower()) for x in grp.split()}
    wts = [len(re.sub(r'[^\w]', '', w)) + 2 + (3 if re.search(r'[,.!?]$', w) else 0) for w in toks]; tot = sum(wts) or 1; acc = 0; words = []
    for w, wt in zip(toks, wts):
        words.append({'w': w, 's': round(vs + d * acc / tot, 3), 'hl': re.sub(r'[^\wáéíóúñü]', '', w.lower()) in hlw}); acc += wt
    ln['words'] = words; ln['vstart'] = round(vs, 3)
    extra = 0
    if ln.get('kind') == 'quiz' and ln.get('countdown', True):
        ln['countdown'] = True
        ln['countdownStart'] = round(t + math.ceil((d + 0.1) / BEAT) * BEAT, 3); extra = 1
    t += (bars + extra) * BAR
    ln['e'] = round(t, 3)
D = t + BAR  # compás final
spec['lines'][-1]['e'] = round(D, 3)
spec['bpm'] = BPM

# ---- 2) página ----
shutil.copy(os.path.join(ENG, 'cancion.html'), os.path.join(wd, 'index.html'))
shutil.copy(os.path.join(ENG, 'logo.png'), os.path.join(wd, 'logo.png'))
pub = {k: v for k, v in spec.items()}
open(os.path.join(wd, 'spec.js'), 'w').write('window.SPEC=' + json.dumps(pub, ensure_ascii=False) + ';')
if frames_only:
    mids = [0.5] + [round((l['s'] + l['e']) / 2, 2) for l in spec['lines']]
    subprocess.run(['node', os.path.join(ENG, 'frames.js'), wd] + [str(m) for m in mids], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y'] + sum([['-i', os.path.join(wd, f'frame_{m}.jpg')] for m in mids], []) +
                   ['-filter_complex', f'hstack={len(mids)},scale={300*len(mids)}:-1', os.path.join(wd, 'sheet.jpg')], check=True)
    print('sheet', os.path.join(wd, 'sheet.jpg')); sys.exit(0)

# ---- 3) música alegre (batería + bajo + acordes + melodía) ----
n = int(SR * D); mus = np.zeros(n)
def add(sig, t0, vol=1.0):
    i0 = int(t0 * SR); e = min(n, i0 + len(sig))
    if i0 < n: mus[i0:e] += sig[:e - i0] * vol
def env(m, k): return np.exp(-np.arange(m) / SR * k)
rng = np.random.default_rng(1)
kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-np.arange(int(.25 * SR)) / SR * 30)) / SR) * env(int(.25 * SR), 14)
clap = rng.normal(0, 1, int(.18 * SR)) * env(int(.18 * SR), 22); clap = np.diff(np.concatenate([[0], clap]))
hat = rng.normal(0, 1, int(.05 * SR)) * env(int(.05 * SR), 90); hat = np.diff(np.concatenate([[0], hat]))
def tone(f, d, k=5, h=(1, .35, .12)):
    tt = np.arange(int(d * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * (j + 1) * tt) for j, a in enumerate(h)) * np.exp(-tt * k)
prog = [(130.81, [261.63, 329.63, 392.0]), (98.0, [196.0, 246.94, 293.66]), (110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63])]
scale = [523.25, 587.33, 659.25, 783.99, 880.0]
mel = [0, 2, 4, 2, 3, 2, 1, 0, 2, 4, 4, 3, 2, 1, 2, 0]
nb = int(D / BEAT)
for b in range(nb):
    tb = b * BEAT; bar = b // 4; root, ch = prog[bar % 4]
    add(kick, tb, .9)
    if b % 2 == 1: add(clap, tb, .35)
    add(hat, tb + BEAT / 2, .18); add(hat, tb, .12)
    add(tone(root, BEAT * .9, 6, (1, .2)), tb, .35)
    if b % 4 == 0:
        for f in ch: add(tone(f, BAR, 2.5), tb, .07)
    add(tone(scale[mel[(b * 2) % 16]], BEAT * .5, 9), tb, .06); add(tone(scale[mel[(b * 2 + 1) % 16]], BEAT * .5, 9), tb + BEAT / 2, .05)
for ln in spec['lines']:  # aplausos extra en el coro
    if ln.get('kind') == 'chorus':
        k = ln['s']
        while k < ln['e'] - 0.01: add(clap, k + BEAT, .5); add(clap, k + 3 * BEAT, .5); k += BAR
fo = int(1.2 * SR); mus[-fo:] *= np.linspace(1, 0, fo); mus = mus / np.max(np.abs(mus)) * 0.8
w = wave.open(os.path.join(wd, 'music.wav'), 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mus * 32767).astype(np.int16).tobytes()); w.close()

# ---- 4) render + mezcla ----
vid = os.path.join(wd, 'video_tmp.mp4')
subprocess.run(['node', os.path.join(ENG, 'render.js'), wd, str(D), vid], check=True)
os.makedirs(os.path.join(ROOT, 'videos'), exist_ok=True)
final = os.path.join(ROOT, 'videos', f'{slug}.mp4'); tmp = final + '.part.mp4'
cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-i', vid, '-i', os.path.join(wd, 'music.wav')]; flt = ''
for i, ln in enumerate(spec['lines']):
    cmd += ['-i', ln['audio']]; ms = int(ln['vstart'] * 1000); flt += f'[{i+2}:a]adelay={ms}|{ms},volume=1.5[a{i}];'
k = len(spec['lines'])
flt += '[1:a]volume=0.32[m];[m]' + ''.join(f'[a{i}]' for i in range(k)) + f'amix=inputs={k+1}:normalize=0,alimiter=limit=0.95[aout]'
cmd += ['-filter_complex', flt, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', tmp]
subprocess.run(cmd, check=True); os.replace(tmp, final)
print('OK', final, round(D, 2), 's')
