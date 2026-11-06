# Curiosidades Animales — TikTok automático

Este repo guarda el motor y los videos del canal de TikTok **Curiosidades Animales** (@filarmonadeltarod).
Cada video: vertical 1080×1920, ilustrado (estilo plano, colores vivos, como `engine/logo.png`), texto grande arriba,
narración en español con voz gratis (edge-tts, `es-MX-JorgeNeural`), música sintetizada y cierre con el logo.
Se publica en TikTok con Buffer usando el enlace `raw.githubusercontent.com` del video.

## Datos fijos
- Buffer: organización `6ae8ff01f564b1c779db4f50`, canal TikTok `6ae8ff41e29c69a1713efa8f`, canal YouTube `6ae91564e29c69a171401081` (FunnyAnimalsJHLK)
- URL pública del video: `https://raw.githubusercontent.com/JohelGB/curiosidades-animales/main/videos/<slug>.mp4`
- Zona horaria del dueño: America/Guatemala (UTC-6). Franjas: `manana` (6 am), `mediodia` (12 md), `tarde` (6 pm).

## Procedimiento de una publicación (tarea programada)
1. `cd` al clon del repo y `git pull --rebase origin main`.
2. `bash engine/setup.sh` (instala edge-tts y confía en el proxy). Debe imprimir `setup ok`.
3. **Primero revisa la sección "SEMANA DE PERROS"**: si la fecha cae ahí, sigue esa sección. Si no: lee `publicados.md`. Desde el 5 nov 2026 **cada video lleva DOS animales** (ver "Formato dúo"). Elige **dos animales que no
   aparezcan ahí** (nunca repetir animal). Varía el hábitat y el tipo
   de animal respecto a los últimos 3 (mamífero, ave, insecto, pez, reptil, anfibio, marino, prehistórico…).
   **Animales prehistóricos**: también valen (dinosaurios, mamut, megalodón, tigre dientes de sable, pterosaurios,
   reptiles marinos, artrópodos gigantes, etc.). Incluye uno más o menos cada 4 videos (si en los últimos 4 de
   `publicados.md` no hay ninguno, toca uno). Usa lo que dice la ciencia actual (museos, universidades, revistas
   científicas) y di cuándo vivió ("hace 66 millones de años"); si un dato es estimado o debatido, dilo así
   ("se cree que…"). Dibújalo como en las reconstrucciones actuales (p. ej. velociraptor con plumas y del tamaño
   de un pavo), nunca como personajes de películas. En `publicados.md` escribe el nombre común (p. ej. `megalodón`).
4. Elige **una curiosidad sorprendente de cada animal** (que se contrasten o compitan) con una cadena de 3–4 datos que se encadenen (gancho → explicación → dato extra → remate).
   **Verifica cada dato con WebSearch** antes de escribirlo; si un dato no se confirma, cámbialo. Nada inventado.
5. Escribe `specs/<AAAA-MM-DD>-<franja>-<animal1>-vs-<animal2>.json` en **FORMATO HISTORIA + DÚO** (secciones "Formato historia"
   y "Formato dúo"; es el formato de TODOS los videos desde el 5 nov 2026). `slug` = mismo nombre sin `.json`.
   **NO uses el estilo canción** (Johel lo eliminó porque las vistas bajaron mucho).
6. `python3 engine/build.py specs/<slug>.json --frames` y **mira** `work/<slug>/sheet.jpg` con Read.
   Revisa: los dos animales se reconocen y se ve bonito, nada tapa el texto, ningún texto se sale, props bien ubicados. Corrige y repite.
7. `python3 engine/build.py specs/<slug>.json` → `videos/<slug>.mp4` (debe durar 30–45 s; si pasa de 45 s, acorta narraciones y repite).
8. Agrega una línea a `publicados.md`, luego `git add specs videos publicados.md && git commit && git push origin main`.
9. Publica con Buffer `create_post` en **los dos canales** (dos llamadas), ambos con `schedulingType: "automatic"`, `mode: "shareNow"`
   y `assets: [{video:{url:<URL raw>, metadata:{title, thumbnailOffset:1500}}}]`:
   - **TikTok** (`6ae8ff41e29c69a1713efa8f`): `text` = `caption` del spec; `metadata: {tiktok: {title, isAiGenerated: true}}`.
   - **YouTube Shorts** (`6ae91564e29c69a171401081`): `text` = 2–3 frases que resuman la curiosidad + línea "Síguenos para más
     curiosidades animales." + hashtags empezando por `#Shorts`; `metadata: {youtube: {title: "<title> <emoji> #Shorts" (máx. 100 caracteres),
     categoryId: "15", privacy: "public", madeForKids: false, isAiGenerated: true, notifySubscribers: true}}`.
10. Espera ~1–2 min y verifica con `get_post` que ambos queden `sent`; anota los dos `externalLink` en la línea de `publicados.md`
    (commit + push). Si uno queda en `error`, reporta el mensaje; no reintentes más de una vez. Que falle uno no impide el otro.

## Objetivo: crecer en seguidores y vistas (curioso + educativo)
Cada video debe enganchar en 1–2 segundos y dejar algo aprendido. Al elegir tema y escribir el spec:
- **Elegir el tema**: prefiere curiosidades con efecto "¡no puede ser!" que la gente quiera compartir (récords, superpoderes,
  cuerpos raros, comparaciones con humanos), mezclando animales famosos (más búsquedas) con raros (más sorpresa).
  Que sea **educativo**: explica el *por qué* o el *para qué* (adaptación, evolución, ecosistema), no solo el dato.
- **Gancho (escena 1)**: pregunta o afirmación imposible con cifra o comparación concreta ("tiene 3 corazones", "más rápido que
  un auto"). Nada de introducciones; el dato fuerte va en la primera frase.
- **Comparaciones humanas**: traduce cifras a algo cotidiano ("como levantar 10 autos", "del tamaño de un autobús").
- **Remate**: el dato más sorprendente va al final, antes del CTA, para que la gente vea el video completo.
- **Comentarios**: en la escena previa al CTA o en el `caption`, cierra con una pregunta corta para el público
  ("¿Cuál te sorprendió más?", "¿Lo sabías? 👇").
- **Títulos**: cortos, con número o pregunta y el nombre del animal ("¿Por qué el pulpo tiene 3 corazones?").
  En YouTube, el título y la descripción deben incluir el nombre del animal y palabras que la gente busca
  (curiosidades, datos, sabías que).
- **Hashtags**: 1–2 del animal y su grupo (#pulpo #animalesmarinos) además de los generales. Para prehistóricos agrega #dinosaurios o #prehistoria.
- **Duración**: apunta a 25–35 s (mejor retención); escenas ágiles, sin relleno.
- Siempre exacto y verificado: nada de exageraciones que no sean ciertas.

## ⚠️ SEMANA DE PERROS: del 2026-11-06 (mediodía) al 2026-11-09 (tarde) inclusive — tiene prioridad sobre todo lo demás
Pedido de Johel: en esas fechas **TODOS los videos son de perros**, con temas que **enseñan algo importante para cuidar al perro**
(referencia que le gustó: TikTok de @laperritopedia sobre "¿es suficiente sacar a pasear a tu perro 10 minutos?").
Durante esas fechas se ignoran la regla de "nunca repetir animal", la de prehistóricos y el formato dúo obligatorio.
Desde el 2026-11-10 se vuelve al formato normal (historia + dúo de animales distintos).
- **Tema**: un consejo útil y verificado para dueños de perros, que no se repita entre videos (revisa la columna tema de
  `publicados.md`). Ideas: el paseo y el olfato (oler = leer las noticias del barrio), alimentos tóxicos (chocolate, uvas/pasas,
  xilitol, cebolla/ajo), golpe de calor y perro encerrado en el carro, pavimento caliente (prueba del dorso de la mano 7 s),
  huesos cocidos que se astillan, garrapatas y ehrlichiosis, vacunas y rabia, desparasitación, dientes y sarro, señales de calma
  (bostezo, lamerse el hocico), la cola que se mueve no siempre es alegría, el mito de "1 año = 7 años humanos", agua fresca
  siempre, perro amarrado todo el día, castración, por qué come pasto, edad en que se separa a un cachorro, etc.
- **Fuentes**: verifica con WebSearch en fuentes veterinarias serias (AVMA, ASPCA, AKC, WSAVA, universidades, colegios de
  veterinarios). Nunca des dosis de medicamentos ni diagnósticos; cuando aplique, termina con "ante la duda, consulta a tu veterinario".
- **Guion (estilo de la referencia)**, 7–9 escenas, 30–45 s, narrador que le habla AL DUEÑO:
  1. Gancho con pregunta directa al dueño ("¿Es suficiente sacar a tu perro diez minutos?").
  2. Contraste "para ti… / para él…" (lo que el dueño cree vs lo que vive el perro).
  3–5. El porqué científico, con una comparación humana cotidiana ("como tú cuando revisas el celular") y una cifra si existe.
  6. Qué hacer: 1–2 consejos concretos y fáciles.
  7. Cierre que invite a compartir: "Envíaselo a alguien que…" + pregunta para comentarios ("¿Cuánto dura el paseo de tu perro?").
  8. CTA: "Síguenos para más curiosidades animales."
- **Dibujos**: un perro protagonista tierno (cambia raza/color en cada video: zaguate/criollo, labrador, chihuahua, pastor alemán,
  salchicha…). Puedes usar el formato dúo con un segundo perro (p. ej. cachorro vs adulto, perro grande vs chico) o con un
  `prop` (comida tóxica, correa, termómetro, sol…) cuando ayude a contar la historia. Hábitat: `farm` (barrio/patio), `savanna`
  (calor), `night`, etc.
- `publicados.md`: animal = `perro` (o `perro y cachorro`); en tema pon el consejo (p. ej. "paseo y olfato").
- Caption TikTok (estilo referencia): "<pregunta gancho> <emoji> <1–2 frases con el dato> ➡️ Envíaselo a alguien que <…>. <pregunta> 👇"
  + #perros #perro #cuidadoanimal #mascotas #consejosparaperros #sabiasque #fyp. Título TikTok y YouTube con la pregunta gancho
  (YouTube: "<pregunta> 🐶 #Shorts", máx. 100 caracteres). `madeForKids: false`.

## Formato historia (desde el 5 nov 2026; reemplaza a la canción)
El video **cuenta una historia** sobre la curiosidad con un narrador (voz normal, sin rimas ni canto, sin estribillos ni aplausos).
Motor: `engine/build.py` con `template.html` (spec con `scenes`, ver "Formato del spec (estilo clásico)"). Usa `"rate": "+15%"`.
- **Arco narrativo**: gancho que crea misterio (1 frase) → presenta al animal 1 y su rasgo → giro/dato fuerte → presenta al animal 2
  y su contraste → dato que los enfrenta → resolución que responde el gancho + pregunta al público → CTA. 8–9 escenas.
- Narración en segunda persona y presente ("Fíjate en…", "Ahora mira al…"), **una oración corta por escena** (máx. ~14 palabras);
  el texto en pantalla resume la idea en ≤ 7 palabras. Duración total 30–45 s.
- El gancho debe prometer algo que se resuelve al final ("…pero uno te enseña los dientes con la boca cerrada" → al final se dice cuál).
- Ejemplo aprobado: `specs/2026-11-05-mediodia-cocodrilo-vs-caiman-historia.json`.

## Formato dúo: dos animales por video (pedido de Johel, desde el 5 nov 2026)
Todos los videos nuevos muestran **dos animales** en plan "duelo" o comparación. El motor lo activa si el spec trae `animalSvg2`:
- Campos extra: `"animal2": "<nombre común>"` y `"animalSvg2": "<SVG del segundo animal, mismas reglas que animalSvg>"`.
  Si el animal mira hacia un lado, dibuja el 1 mirando a la derecha y el 2 a la izquierda (puedes envolver el 2 en
  `<g transform='translate(600 0) scale(-1 1)'>`).
- Cada escena puede llevar `"focus": 1` o `"focus": 2`: ese animal ocupa el centro con su `anim` y el otro queda pequeño en una
  esquina. Sin `focus`, los dos aparecen lado a lado (úsalo en el gancho, el dato que los enfrenta y la resolución).
- **Cómo elegir la pareja**: que tenga sentido y dé juego: rivales del mismo hábitat (león vs hiena), extremos opuestos (el más
  rápido vs el más lento), parecidos que se confunden (cocodrilo vs caimán, foca vs lobo marino), o un actual vs su pariente
  prehistórico (elefante vs mamut). Ambos del mismo `habitat` o uno que sirva para los dos.
- La regla de prehistóricos (≈1 de cada 4 videos) se cumple si al menos uno de los dos lo es.
- `publicados.md`: en la columna animal escribe los dos: `cocodrilo y caimán`. Ninguno de los dos puede repetirse.
- Caption TikTok: "<emoji> <gancho> <Animal 1> vs <animal 2>: <resumen>. ¿Cuál te sorprendió más? 👇" + hashtags de ambos y los generales.
  Título TikTok: "<Animal 1> vs <animal 2>: <pregunta corta> <emoji>". Título YouTube: "<Animal 1> vs <animal 2>: <pregunta o dato> <emoji> #Shorts"
  (máx. 100 caracteres); descripción YouTube: 2–3 frases que resuman la historia + "Síguenos para más curiosidades animales." + `#Shorts` y hashtags.
- YouTube: `madeForKids: false` (canal para todo público).

## Estilo canción (ELIMINADO el 5 nov 2026: no usar; se deja solo como referencia)
Canción corta y pegajosa con datos REALES y verificados: rima, estribillo que se repite, aplausos, una adivinanza y karaoke.
Muestra aprobada por Johel: `specs/_muestra-cancion-pulpo.json` (úsala de modelo). El motor es `engine/build_cancion.py`
(cada frase empieza en un compás; la voz dice la frase normal, NO palabra por palabra).
```json
{
  "slug": "2026-11-05-manana-koala", "style": "cancion", "animal": "koala",
  "habitat": "ocean | jungle | savanna | arctic | desert | sky | night | farm", "bpm": 104,
  "songTitle": "La canción del <span class='hl'>koala</span> 🐨",
  "caption": "...", "title": "...",
  "animalSvg": "<SVG para viewBox 0 0 600 600: tierno, plano, ojos grandes; partes 'wiggle'/'tail'/'flap'/'blink'>",
  "lines": [
    {"text": "Frase 1 con rima", "kind": "verse"},
    {"text": "¡Frase 2 con el *dato fuerte*!", "kind": "verse", "badge": "opcional: cifra corta"},
    {"text": "¡Estribillo corto y repetible!", "kind": "chorus"},
    {"text": "¡Uno, dos y tres, *aplaude* conmigo!", "kind": "chorus"},
    {"text": "Dato 2 que explica el porqué,", "kind": "verse"},
    {"text": "y dato 3 que rima.", "kind": "verse"},
    {"text": "¿Pregunta para adivinar? ¡Adivina!", "kind": "quiz"},
    {"text": "¡*Respuesta*! ¡Frase que rima!", "kind": "answer", "bigText": "RESPUESTA EN 1-2 PALABRAS", "bigColor": "#ffe066"},
    {"text": "(estribillo otra vez, idéntico)", "kind": "chorus"},
    {"text": "(segunda línea del estribillo, idéntica)", "kind": "chorus"},
    {"text": "¡Síguenos para más *curiosidades animales*!", "kind": "cta", "cta": true}
  ]
}
```
- **El canal es para TODO PÚBLICO (no infantil)**: canción divertida y curiosa que disfruten adultos y niños; humor ingenioso,
  nada de lenguaje de bebé ni frases tipo "amiguitos". 9–12 líneas; cada línea **máx. ~8 palabras** (cabe en un compás). Rima simple.
- El **estribillo** (2 líneas `chorus`) aparece 2 veces, idéntico; debe nombrar al animal o su superpoder y pedir una acción
  ("aplaude", "salta", "di ¡guau!"). Las palabras entre `*asteriscos*` salen resaltadas.
- La **adivinanza** (`quiz` + `answer`) es sobre un dato real del video; `bigText` muestra la respuesta grande con confeti.
- Todo dato debe ser verdadero y verificado (paso 4); la rima nunca justifica exagerar.
- YouTube: `madeForKids: false` (canal para todo público, decisión de Johel). Título YouTube: "<dato sorprendente del animal> 🎵 #Shorts" (debe incluir el nombre del animal).
- TikTok caption: "🎵 <dato sorprendente> ¿Adivinaste? 👇" + hashtags (#curiosidades #animales #<animal> #sabiasque #datoscuriosos #fyp).



## Formato del spec (estilo clásico, engine/build.py)
```json
{
  "slug": "2026-11-03-manana-ajolote",
  "animal": "ajolote",
  "habitat": "ocean | jungle | savanna | arctic | desert | sky | night | farm" (prehistóricos: el que más se parezca a su ambiente),
  "caption": "Texto del post con 1-2 emojis + 5-6 hashtags (#curiosidades #animales #<animal> #sabiasque #datoscuriosos #fyp)",
  "title": "Gancho corto para TikTok",
  "animalSvg": "<SVG interno para viewBox 0 0 600 600>",
  "scenes": [
    {"text": "Texto en pantalla (HTML, <span class='hl'>resaltado</span>)", "narration": "Lo que dice la voz", "anim": "bob",
     "badge": "opcional: cifra grande p.ej. '80 por segundo'", "sub": "opcional: texto chico debajo",
     "prop": "opcional: SVG interno para viewBox 0 0 300 300", "propPos": "right|left|top|center|bottomright|bottomleft"},
    {"text": "Síguenos para más <span class='hl'>curiosidades animales</span>", "narration": "Síguenos para más curiosidades animales.", "cta": true}
  ]
}
```
- 5–7 escenas; la primera es el gancho "¿Sabías que…?"; la última SIEMPRE es la de `cta: true` (muestra el logo).
- Texto en pantalla: máx. ~10 palabras. Narración: 1 oración corta por escena (la escena dura lo que dura la voz).
  Escribe los números en palabras en `narration` ("mil doscientas") y en cifra en `text`/`badge`.
- `anim` del animal: `bob, pop, zoom, tiny, shake, walk, walkback, jump, flip, fly, hover, sleep, spin, color, ghost, left`.
  Usa `left` cuando hay `prop` a la derecha; `walk` para desplazarse; `sleep` cierra los ojos y muestra "z z".
- **animalSvg**: dibujo propio, plano y tierno (ojos grandes con brillo, mejillas rosadas, contornos limpios, sin texto),
  centrado en (300,300), ocupando ~400–500 px. Partes animables: agrega `class='flap'` (alas, aletas), `'tail'` (cola),
  `'wiggle'` (orejas, tentáculos), `'blink'` (grupo del ojo) con `data-cx`/`data-cy` = punto de giro / centro del ojo.
  Usa comillas simples dentro del SVG para no romper el JSON. Nunca dibujes personajes con marca o copyright.

## publicados.md
Una línea por video: `| fecha | franja | animal | tema | link TikTok | link YouTube |`.
