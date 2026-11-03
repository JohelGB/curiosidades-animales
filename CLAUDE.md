# Curiosidades Animales — TikTok automático

Este repo guarda el motor y los videos del canal de TikTok **Curiosidades Animales** (@filarmonadeltarod).
Cada video: vertical 1080×1920, ilustrado (estilo plano, colores vivos, como `engine/logo.png`), texto grande arriba,
narración en español con voz gratis (edge-tts, `es-MX-JorgeNeural`), música sintetizada y cierre con el logo.
Se publica en TikTok con Buffer usando el enlace `raw.githubusercontent.com` del video.

## Datos fijos
- Buffer: organización `6ae8ff01f564b1c779db4f50`, canal TikTok `6ae8ff41e29c69a1713efa8f`, canal YouTube `6ae91564e29c69a171401081` (FunnyAnimalsJHLK)
- URL pública del video: `https://raw.githubusercontent.com/JohelGB/curiosidades-animales/main/videos/<slug>.mp4`
- Zona horaria del dueño: America/Guatemala (UTC-6). Franjas: `manana` (7 am), `mediodia` (12 md), `tarde` (6 pm).

## Procedimiento de una publicación (tarea programada)
1. `cd` al clon del repo y `git pull --rebase origin main`.
2. `bash engine/setup.sh` (instala edge-tts y confía en el proxy). Debe imprimir `setup ok`.
3. Lee `publicados.md`. Elige un **animal que no aparezca ahí** (nunca repetir animal). Varía el hábitat y el tipo
   de animal respecto a los últimos 3 (mamífero, ave, insecto, pez, reptil, anfibio, marino…).
4. Elige **una curiosidad sorprendente** con una cadena de 3–4 datos que se encadenen (gancho → explicación → dato extra → remate).
   **Verifica cada dato con WebSearch** antes de escribirlo; si un dato no se confirma, cámbialo. Nada inventado.
5. Escribe `specs/<AAAA-MM-DD>-<franja>-<animal>.json` (formato abajo). `slug` = mismo nombre sin `.json`.
6. `python3 engine/build.py specs/<slug>.json --frames` y **mira** `work/<slug>/sheet.jpg` con Read.
   Revisa: el animal se reconoce y se ve bonito, nada tapa el texto, ningún texto se sale, props bien ubicados. Corrige y repite.
7. `python3 engine/build.py specs/<slug>.json` → `videos/<slug>.mp4` (debe durar 20–45 s).
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
- **Hashtags**: 1–2 del animal y su grupo (#pulpo #animalesmarinos) además de los generales.
- **Duración**: apunta a 25–35 s (mejor retención); escenas ágiles, sin relleno.
- Siempre exacto y verificado: nada de exageraciones que no sean ciertas.

## Formato del spec
```json
{
  "slug": "2026-11-03-manana-ajolote",
  "animal": "ajolote",
  "habitat": "ocean | jungle | savanna | arctic | desert | sky | night | farm",
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
