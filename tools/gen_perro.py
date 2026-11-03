import json,random,math
random.seed(7)
W="stroke='#fff' stroke-width='7' fill='none' stroke-linecap='round' stroke-linejoin='round'"
w="stroke='#fff' stroke-width='4' fill='none' stroke-linecap='round'"
base=f"""
<path d='M300 1500 C 330 1380, 360 1250, 420 1150' {W}/>
<path d='M880 1500 C 880 1300, 860 1080, 820 900 C 790 770, 700 690, 590 690 C 500 690, 440 740, 410 790' {W}/>
<path d='M410 790 C 380 830, 330 850, 270 850 C 225 850, 195 870, 195 905' {W}/>
<path d='M200 935 C 230 975, 290 985, 350 985 C 400 985, 430 1000, 450 1030' {W}/>
<path d='M300 985 C 320 1030, 380 1060, 450 1040 C 520 1100, 560 1140, 600 1160 C 700 1200, 780 1220, 860 1250' {W}/>
<path d='M690 720 C 760 700, 830 760, 815 880 C 805 970, 760 1010, 730 980 C 700 950, 690 860, 690 720 Z' fill='url(#hatch)' {W.replace("fill='none' ","")}/>
<ellipse cx='520' cy='800' rx='26' ry='22' {W}/>
<circle cx='526' cy='802' r='9' fill='#fff' class='pop'/>
<path d='M480 770 C 500 755, 540 755, 556 770' {w}/>
<ellipse cx='215' cy='905' rx='44' ry='34' fill='url(#hatch)' {W.replace("fill='none' ","")}/>
<path d='M205 915 C 215 925, 230 925, 238 912' {w}/>
<path d='M300 985 C 300 960, 290 945, 270 940' {w}/>
<path d='M420 1150 C 520 1250, 700 1300, 880 1300' {w} opacity='.5'/>
<g opacity='.45'><path d='M560 1000 l 30 -12 M600 1030 l 30 -12 M640 1060 l 30 -12 M680 1090 l 30 -12' {w}/></g>
"""
# nose print lens around nose (215,905)
cells=[]
for i in range(70):
    a=random.uniform(0,2*math.pi);r=random.uniform(0,95)
    x=215+r*math.cos(a);y=905+r*math.sin(a)*0.85;s=random.uniform(8,14)
    pts=" ".join(f"{x+s*math.cos(k*math.pi/3+0.3):.1f},{y+s*math.sin(k*math.pi/3+0.3):.1f}" for k in range(6))
    cells.append(f"<polygon points='{pts}' stroke='#fff' stroke-width='2.2' fill='none'/>")
lens=f"""<circle cx='215' cy='905' r='118' fill='#1f4fc9' stroke='#ffd23f' stroke-width='6'/>{''.join(cells)}
<path d='M170 900 C 175 870, 200 865, 205 895 C 200 915, 180 920, 170 900 Z' fill='#0d2a7a' stroke='#fff' stroke-width='4'/>
<path d='M260 900 C 255 870, 230 865, 225 895 C 230 915, 250 920, 260 900 Z' fill='#0d2a7a' stroke='#fff' stroke-width='4'/>"""
# xray cavity with turbinates and receptors
turb=f"""<path d='M240 880 C 300 840, 380 830, 470 800 C 500 830, 490 880, 450 900 C 380 920, 300 930, 240 930 Z' stroke='#ffd23f' stroke-width='5' fill='rgba(255,210,63,.08)'/>
<path d='M270 900 c 15 -20 30 -20 40 0 c 10 -20 25 -20 40 0 c 10 -20 25 -20 40 0 c 10 -20 25 -20 40 0 c 10 -20 25 -20 35 -5' {w}/>
<path d='M300 875 c 12 -16 24 -16 34 0 c 10 -16 22 -16 34 0 c 10 -16 22 -16 34 0 c 10 -16 22 -16 30 -10' {w}/>"""
dots="".join(f"<circle cx='{random.uniform(255,470):.0f}' cy='{random.uniform(845,920):.0f}' r='4.5' fill='#ffd23f' class='pop'/>" for _ in range(90))
# compare grid top
dg="".join(f"<circle cx='{170+ (i%14)*24}' cy='{430+(i//14)*24}' r='7' fill='#ffd23f' class='pop'/>" for i in range(14*8))
hg="".join(f"<circle cx='{760+(i%3)*24}' cy='{430+(i//3)*24}' r='7' fill='#fff' class='pop'/>" for i in range(3))
cmp=f"""<rect x='140' y='330' width='380' height='300' rx='20' stroke='#ffd23f' stroke-width='5' fill='none'/>
<text x='330' y='395' font-family='Inter Display' font-weight='900' font-size='48' fill='#ffd23f' text-anchor='middle'>PERRO</text>{dg}
<rect x='690' y='330' width='230' height='300' rx='20' stroke='#fff' stroke-width='5' fill='none'/>
<text x='805' y='395' font-family='Inter Display' font-weight='900' font-size='48' fill='#fff' text-anchor='middle'>HUMANO</text>{hg}
<text x='330' y='700' font-family='Inter Display' font-weight='900' font-size='64' fill='#ffd23f' text-anchor='middle'>300 M</text>
<text x='805' y='700' font-family='Inter Display' font-weight='900' font-size='64' fill='#fff' text-anchor='middle'>5 M</text>"""
air=f"""{turb}
<path d='M180 905 C 260 890, 360 870, 470 800' class='flow' stroke='#ffd23f' stroke-width='12' fill='none' stroke-linecap='round'/>
<path d='M180 915 C 260 930, 330 960, 420 1100' class='flow' stroke='#fff' stroke-width='12' fill='none' stroke-linecap='round'/>
<text x='520' y='770' font-family='Inter Display' font-weight='900' font-size='44' fill='#ffd23f'>OLER</text>
<text x='440' y='1150' font-family='Inter Display' font-weight='900' font-size='44' fill='#fff'>RESPIRAR</text>"""
slits=f"""<path d='M232 925 C 240 945, 250 950, 262 948' stroke='#ffd23f' stroke-width='6' fill='none'/>
<path d='M250 940 C 290 960, 320 990, 330 1040' class='flow' stroke='#ff6b6b' stroke-width='10' fill='none' stroke-linecap='round'/>
<path d='M255 930 C 300 935, 340 950, 370 980' class='flow' stroke='#ff6b6b' stroke-width='10' fill='none' stroke-linecap='round'/>
<path d='M120 880 C 150 890, 165 900, 175 905' class='flow' stroke='#ffd23f' stroke-width='10' fill='none' stroke-linecap='round'/>
<path d='M110 930 C 140 925, 160 915, 175 910' class='flow' stroke='#ffd23f' stroke-width='10' fill='none' stroke-linecap='round'/>"""
wet="".join(f"<path d='M{x} {y} c 6 10 10 16 10 22 a10 10 0 0 1 -20 0 c 0 -6 4 -12 10 -22 z' fill='#9fd8ff' stroke='#fff' stroke-width='2' class='pop'/>" for x,y in [(190,870),(240,880),(215,930),(260,915),(175,915)])
wet+="".join(f"<circle cx='{random.uniform(60,180):.0f}' cy='{random.uniform(820,990):.0f}' r='5' fill='#ffd23f' class='pop'/>" for _ in range(18))
spec={
 "slug":"2026-11-03-noche-perro-nariz","animal":"perro","style":"blueprint",
 "caption":"La nariz de tu perro es única 🐶👃 ¿Lo sabías? #curiosidades #animales #perros #sabiasque #datoscuriosos #fyp",
 "title":"La nariz de tu perro es como una huella digital",
 "ytText":"Ningún perro tiene la misma nariz: sus líneas y bultos son únicos, como una huella digital. Por dentro tiene hasta 300 millones de receptores de olor (tú, unos 5 millones), separa el aire para respirar y para oler, y su nariz húmeda atrapa los olores.\n\nSíguenos para más curiosidades animales.\n\n#Shorts #curiosidades #animales #perros #sabiasque #datoscuriosos",
 "baseArt":base,
 "scenes":[
  {"narration":"¿Sabías que la nariz de tu perro es como una *huella digital*?","cam":{"x":520,"y":980,"z":1.0},"overlay":""},
  {"narration":"Sus líneas y bultos son *únicos*: no hay dos perros con la misma nariz.","cam":{"x":215,"y":905,"z":2.6},"overlay":lens},
  {"narration":"Por dentro, tiene hasta *trescientos millones* de receptores de olor.","cam":{"x":370,"y":880,"z":1.9},"overlay":turb+dots,"baseOpacity":0.6},
  {"narration":"Tú tienes apenas unos *cinco millones*.","cam":{"x":540,"y":620,"z":1.15},"overlay":cmp,"baseOpacity":0.25,"screenY":820},
  {"narration":"Al respirar, el aire se divide en dos caminos: uno para *respirar* y otro solo para *oler*.","cam":{"x":360,"y":930,"z":1.5},"overlay":air,"baseOpacity":0.6},
  {"narration":"Y suelta el aire por unas *rendijas* a los lados, para seguir oliendo sin parar.","cam":{"x":220,"y":920,"z":2.6},"overlay":slits},
  {"narration":"Además, su nariz *húmeda* atrapa las partículas de olor.","cam":{"x":190,"y":905,"z":2.4},"overlay":wet},
  {"narration":"Síguenos para más *curiosidades animales*.","cta":True}
 ]}
json.dump(spec,open('specs/2026-11-03-noche-perro-nariz.json','w'),ensure_ascii=False,indent=1)
print('ok')
