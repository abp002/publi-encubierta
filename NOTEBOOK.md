# Bitácora — publi-encubierta

Proceso día a día, con decisiones y por qué. Lo que se descarta también se apunta.

## 2026-09-07 — Origen y fase A

**De dónde sale.** Post en r/MachineLearning: alguien scrapeó TikTok por ingeniería inversa
de la app Android y publicó 4,5B de vídeos en Hugging Face (`kuben-developer/tiktok-videos-4b`).
El titular decía 5,94B y 3,23B de perfiles; lo publicado son 27 de 32 particiones de vídeos,
**sin perfiles, sin identidad de creador, sin URLs de media**. 289 GB en Parquet zstd.

**Qué contiene.** `content_id`, `create_time`, `desc` (caption), `mentions`, `duration`,
`is_video`, `music_id`, `music_title`, `views/likes/comments/shares/saves`, `country`,
`language`, `is_ad`. Los contadores son un *snapshot* (no serie temporal). Filas agrupadas
por creador, no barajadas. `country` y `language` son inferidos por TikTok y poco fiables.

**Pregunta del proyecto.** ¿Qué fracción del contenido en español con marcadores comerciales
no declara la relación publicitaria? En España la publicidad encubierta es ilegal
(Ley de Competencia Desleal, Código de Conducta de influencers de AUTOCONTROL, LGCA 2022 →
CNMC). *Pendiente verificar la vigencia exacta antes de citarlo.*

**Decisiones de diseño tomadas hoy:**
1. Restringir a español e inglés. Abarata el modelo y afina el ángulo legal.
2. Marco: PU learning. `is_ad = 0` no significa "no es anuncio", significa "no está
   etiquetado". Lo que buscamos vive precisamente en los falsos negativos de la etiqueta.
3. Cascada: filtro léxico barato sobre todo → modelo caro solo sobre candidatos →
   validación manual sobre cientos. Inferir un encoder sobre 4,5B filas serían ~17 días
   de GPU: descartado.
4. Usar 3-5 ficheros de 27. Legítimo: las particiones son por hash de creador.
5. **Solo agregados.** Nunca lista de cuentas, ni captions íntegros, ni `content_id`
   en nada publicado. Es la diferencia entre un estudio y una acusación.
6. `.gitignore` en allowlist: todo ignorado salvo lo que se permite. `data/` ni existe
   para git.
7. Hardware: Mac M4 24 GB para datos (DuckDB con límites); PC RTX 4060 Ti 8 GB para
   embeddings/fine-tuning. Los datos ya reducidos viajan en ~500 MB.

**Riesgo detectado antes de empezar.** Aunque el autor eliminó a propósito la identidad del
creador, hay campos colaterales y propiedades del orden físico de las filas que permiten
recuperarla parcialmente. No es el objeto de este proyecto, y el detalle no se publica aquí
hasta comunicárselo al autor del dataset. Pero condiciona qué se publica: **nada que permita
reidentificar** — ni captions íntegros, ni `content_id`, ni cuentas.

**Fase A: dos números deciden si el proyecto vive.**
- Prevalencia de `is_ad`: si es < 0,1 % no hay positivos suficientes para PU learning.
- Distribución de `language`: en la vista previa las 100 filas eran `"un"`. Si domina,
  la columna es inútil y hay que detectar idioma sobre `desc` (fastText LID).
Se hace **sin descargar nada**: DuckDB + `httpfs` leyendo `videos-00.parquet` por rangos HTTP.

### Resultados de la fase A (mismo día, ~1 h desde cero)

`httpfs` contra Hugging Face funciona a la primera. `count(*)` de `videos-00.parquet`
(10,7 GB) en **1,8 s** leyendo solo el pie del Parquet: 166.423.554 filas en 166 row
groups de ~1M. Tamaño comprimido por columna, que es lo que decide qué cuesta cada
pregunta: `desc` 3,99 GB (37 %), `music_title` 1,34, `content_id` 1,21, `music_id` 1,12…
**`language` 30 MB e `is_ad` < 5 MB.** Las dos preguntas que deciden el proyecto
costaron ~35 MB de red y ~15 s cada una. Ni un byte descargado a disco.

| Pregunta | Resultado | Veredicto |
|---|---|---|
| Prevalencia `is_ad` | **1,32 %** → 2.199.443 positivos en un solo fichero | Vive. Estimaba 0,5 %; hay más del doble |
| `language` | `un` 54,15 % · `en` 35,94 % · **`es` 3,12 %** (5,19M) · ru 1,0 · hi 0,9 · id 0,7 · pt 0,4 | La columna sirve a medias: la mitad es desconocido |

Tasa de `is_ad` por idioma: **es 3,27 %**, en 2,15 %, pt 1,82 %, **un 0,55 %**.

Extrapolando ×27 ficheros: ~140M de filas en español con ~4,6M de positivos; ~1,6B en
inglés con ~35M. Para PU learning sobra por un orden de magnitud. Con 3-5 ficheros basta.

**Observación que orienta el siguiente paso.** El `un` tiene una tasa de anuncio seis veces
menor que `es`. Hipótesis: `un` no es "idioma que TikTok no supo detectar", es "caption sin
texto" (vacío, solo hashtags, solo emojis). Si es así, la columna `language` **sí** sirve
para nuestro propósito — un detector de captions no puede hacer nada con un caption sin
texto — y nos ahorramos el paso de detección de idioma. Se comprueba con una muestra.

### Fase A bis — qué es el `un` (mismo día)

Muestra de 400.000 filas en 4 ventanas repartidas por `videos-00` (`file_row_number`
entre 0, 40M, 80M y 120M; DuckDB poda los row groups que no toca: **5,6 s** con `desc`
incluida). Clasificación del caption:

| idioma | vacío | solo hashtags/emoji | texto < 8 letras | con texto |
|---|---|---|---|---|
| **un** | **56,1 %** | **39,2 %** | 1,6 % | 3,0 % |
| en | 0,8 % | 0,3 % | 10,6 % | 88,3 % |
| es | 0,4 % | 0,3 % | 5,8 % | **93,5 %** |

**Conclusión: el `un` es "caption sin texto" en un 95 %.** TikTok no falla al detectar el
idioma; es que no hay nada que detectar. Consecuencias:

1. **La columna `language` sirve.** Nos quedamos con `es` (y `en` como contraste) y nos
   ahorramos la detección de idioma sobre 4,5B captions. El 3 % de `un` con texto (~2,7M
   por fichero) podría esconder algo de castellano; se puede rescatar más adelante con
   fastText LID solo sobre ese residuo, que es barato. Queda como opcional.
2. **Limitación a declarar desde ya:** un detector basado en captions es ciego a los
   anuncios sin caption. Hay `is_ad = 1` en captions vacíos (0,42 %). El estudio habla del
   contenido *con texto*, y así hay que escribirlo.
3. En `es` con texto la tasa de `is_ad` es 2,55 %. En una muestra pequeña y sesgada por
   creador, pero coherente con el 3,27 % del fichero entero.

**Estado al cerrar el día:** el proyecto vive. Positivos de sobra, columna de idioma
útil, coste de exploración ≈ 60 MB de red y cero disco. Siguiente: descargar 3 ficheros
(~32 GB) y materializar el subconjunto `es` + `en` en Parquet local.

## 2026-09-07 (tarde) — Solo español. Arranca la fase B

**Decisión: el estudio se restringe al español.** Tres razones, en orden de peso:

1. **Metodológica.** En PU learning la constante central es `c = P(etiquetado | anuncio)`:
   qué fracción de los anuncios reales lleva la etiqueta. Depende de las normas de
   declaración de cada mercado. Mezclar inglés y español obliga a estimar dos `c` o a
   aceptar una media que no describe a nadie. Un idioma = un estimador limpio.
2. **El contraste que importa no es el idioma, es el país.** La ley que motiva el estudio es
   española; el español de TikTok es mayoritariamente latinoamericano. La comparación
   útil es ES frente a MX/AR/CO *dentro* del español. `country` es poco fiable fila a
   fila, pero como agregado sobre millones de filas es usable.
3. **Escala.** El inglés era el 36 % del dataset, el español el 3 %. El subconjunto se
   reduce diez veces: 3 ficheros ≈ 15,6M filas y ~500k positivos, `desc` ≈ 400 MB.
   Tan pequeño que escalar a los 27 ficheros (todo el español del dataset, ~140M filas,
   ~4,6M positivos, ~7 GB en Parquet) es viable con descarga-extrae-borra y 11 GB de
   disco constante. Queda como opción.

Se pierde la frase "el español declara peor que el inglés". Vistosa, pero compara
mercados distintos: estaba mal planteada de origen.

**Fase B en marcha.** `scripts/materializar.py 0 1 2`: descarga `videos-00/01/02` (32 GB)
a `data/raw/`, extrae `language = 'es'` con todas las columnas a `data/es/`, y apunta
filas y positivos por fichero. Los crudos se conservan de momento: permiten re-extraer
(p. ej. rescatar el 3 % de `un` con texto). Corre en segundo plano con DuckDB limitado.

## 2026-09-07 (noche) — Fase B cerrada: `is_ad` no era lo que buscábamos

**Materialización.** `videos-00/01/02` (32 GB) bajaron a ~80 MB/s: 135 s por fichero, 7 s de
extracción cada uno. Subconjunto `es`: **15.575.722 filas, 506.909 con `is_ad = 1` (3,25 %)**,
1,2 GB en tres Parquet. Los tres ficheros dan 3,27 / 3,30 / 3,19 %: particiones por hash,
como prometía la tarjeta. Perfil completo en `informes/perfil_es.md` (solo agregados).

### Tres columnas que parecían datos y eran procesos

**1. `is_ad` tiene fecha de nacimiento.** 0,00 % en 2019–2022, 0,14 % en 2023, 0,64 % en 2024,
**4,2 % en 2025 y 5,4 % en 2026**. No es que antes no hubiera anuncios: es que lo que mide
no existía. Consecuencia inmediata para PU learning: `c = P(etiquetado | positivo)` no es
constante, es ~0 hasta 2024. Cualquier modelo que mezcle años aprende "vídeo viejo = no
anuncio". **El estudio se restringe a 2025+.**

**2. `country` mide otra cosa.** El 76 % del contenido en español lleva `US`. No es TikTok
hispano de EE. UU.: es probablemente la región del dispositivo anónimo con que se recolectó.
Los países de LATAM y España aparecen, pero la columna solo vale como agregado y con
cautela. España: 311.628 filas en 3 ficheros (2 % del español).

**3. `is_ad` es TikTok Shop, no una colaboración declarada.** La tarjeta dice "marked as
sponsored". El diagnóstico (`scripts/diagnostico_is_ad.py`) dice otra cosa:

| grupo (2025+) | n | likes/views | coment./views | menciones | sonidos distintos/fila |
|---|---|---|---|---|---|
| `is_ad = 1` | 492.309 | **0,011** | **0,00000** | 17 % | **0,10** |
| `#publi` / `#publicidad` | 7.201 | 0,040 | 0,00117 | **57 %** | 0,54 |
| `#paidpartnership` | 68.229 | 0,061 | 0,00306 | 11 % | 0,50 |
| orgánico | 9,78M | 0,050 | 0,00149 | 10 % | 0,13 |

`is_ad = 1` tiene cinco veces menos likes por view que lo orgánico, cero comentarios, y una
décima parte de sonidos distintos (pocas cuentas muy prolíficas). Sus co-hashtags:
`#tiktokshop` (67k), `#tiktokshopcreatorpicks` (64k), `#tiktokshopblackfriday`,
`#dealsforyoudays`. **El 40 % de sus captions dice literalmente "tiktokshop"** (×23 frente al
resto). Es comercio con producto enlazado: catálogo, no influencer. Encaja con el resto:
nace cuando Shop llega a MX/LATAM/ES (2024–25) y se concentra en US, su mayor mercado.

**Y `#paidpartnership` tampoco.** De sus 68.229 filas, **65.018 llevan `#liveincentiveprogram`**:
el programa con el que TikTok paga a creadores por hacer directos. El "socio pagador" es
TikTok. Engagement de creador real, pero no es una marca. Fuera.

Al quitar ambos, de las "declaraciones en texto" quedan **23.500 filas en 3 ficheros**, y
el vocabulario que las define es español: `#publi`, `publicidad`, `patrocinado`,
`colaboración pagada`, `en colaboración con`. Su firma es el 57 % de menciones: la marca
etiquetada. `#ad` se queda con cautela (en US lo usan sobre todo afiliados de Shop, que ya
salen por `is_ad`).

### Universo del estudio, redefinido

Filtro: `create_time >= 2025`, `is_ad = 0`, sin `#liveincentiveprogram` ni `#paidpartnership`.

| | filas | declarados | % |
|---|---|---|---|
| Universo (3 ficheros) | 9.775.882 | 11.938 | 0,12 % |
| … con marcador comercial (candidatos de la cascada) | 418.255 | 2.678 | 0,64 % |
| España | 221.206 | 1.797 | **0,81 %** |

España declara **el doble que México o Colombia (0,35 %) y cuatro veces más que Argentina**.
Es el país con más declaración de la tabla — consistente con que aquí hay AUTOCONTROL y la
CNMC — y a la vez el que más contenido comercial sin declarar tiene (11 %). Ese contraste
es el estudio.

### Lo que cambia en el diseño de la fase C

1. **Positivos = declaración textual en español**, no `is_ad`. ~12k en 3 ficheros, ~1,8k de
   España. Pocos: **hay que escalar a los 27 ficheros** (~107k positivos, ~16k de ES).
   Es barato: descarga-extrae-borra, 11 GB de disco constante, ~1 h.
2. **Fuga obligatoria de arreglar:** si los positivos se definen por `#publi`, el modelo
   aprende `#publi`. Los tokens de declaración se enmascaran antes de vectorizar. Lo que
   debe aprender es *lo demás* que caracteriza una colaboración: la marca mencionada, el
   código de descuento, el léxico de producto.
3. `is_ad` pasa de etiqueta a **criterio de exclusión**. TikTok Shop es comercial y está
   señalizado por diseño (tarjeta de producto); no es publicidad encubierta.
4. El contraste por país se mantiene, con la cautela del punto 2 sobre `country`.

**Descartado hoy:** usar `is_ad` como verdad; usar `#paidpartnership` como señal; comparar
español con inglés. **Aprendido:** una columna que se llama `is_ad` no te dice qué anuncio
es. Perfilar antes de modelar ha cambiado el diseño en tres sitios sin escribir un modelo.

## 2026-09-07 (noche, II) — ¿Vale `country`? Sí, como agregado. Arranca ALE-115

La duda que podía tumbar el ángulo España: si `country` es un artefacto (76 % `US`), el
contraste por país no se puede defender. Comprobación (`scripts/validar_country.py`): léxico
peninsular (*vosotros, vuestro, €, coche, móvil, ordenador…*) frente a léxico LATAM
(*ustedes, $, carro, celular, voseo, güey, parce…*) en captions de 2025+ con ≥ 20 caracteres.

| país | filas | % peninsular | % LATAM | ratio |
|---|---|---|---|---|
| **ES** | 222.578 | **14,2 %** | **1,1 %** | **13,2** |
| PE | 181.415 | 8,6 % | 2,2 % | 3,9 |
| MX | 581.594 | 5,4 % | 3,6 % | 1,5 |
| AR | 138.678 | 7,5 % | **8,6 %** | 0,9 |
| US | 7.449.686 | 4,4 % | 2,4 % | 1,8 |

`ES` se separa de todo lo demás por un orden de magnitud; Argentina invierte el signo con
el voseo, como debe. El ~4-8 % de "peninsular" que aparece en todos los países es el ruido
de palabras compartidas (*tío, os…*): la señal está en la diferencia, no en el nivel.
`US` se comporta como la media: **es el cajón de "región desconocida"**, no TikTok hispano
de EE. UU. Consecuencia: `country` vale para agregar por país; `US` se reporta como
"sin región". El contraste ES vs LATAM está justificado.

Con eso, escalar a 27 ficheros tiene sentido: ALE-115 en marcha, descarga-extrae-borra con
`--borrar-crudo`, disco constante.

## 2026-09-07 (noche, III) — Primer baseline PU, y lo que enseñó la lista de n-gramas

Mientras ALE-115 descarga, el paquete `publi/` (léxico único por motor, enmascarado,
partición por bloques, Elkan-Noto con ajuste de prior; 21 tests) y `scripts/baseline.py`:
TF-IDF palabras (1-2) + caracteres (3-5), regresión logística, P = declaración textual,
U = 500k de muestra, split por bloques de 2.000 filas del crudo. Sobre los 3 ficheros.

**v1 — AUC 0,926, y mentira.** La lista de n-gramas con más peso lo delataba: `blici`,
`ubli`, `publ`, `anunc`, `pagada`. El enmascarado usaba el mismo regex que la etiqueta, y
la etiqueta es precisa a propósito: "publi" como palabra suelta, `#fyp#publicidad` pegado
o "colab pagada" no la activan, pero el modelo los ve. **El regex de enmascarar tiene que
ser un superconjunto amplio (por raíces) del de etiquetar, no el mismo.** Ahora `MASCARA`
quita `publi*`, `patrocin*`, `anunci*`, `sponsor*`, `colab*`, `regalad*`, `pagada`, `ad/ads`
y las frases enteras ("en colaboración con", "patrocinado por"), porque de "en colaboración
con @marca" sobrevivía `en con`. Test de regresión con los n-gramas que se colaron.

**También P estaba sucio.** Segundo hallazgo de la lista: `marketing`, `engañosa`, `aviso
de`, `locución`, `fm`, `tu marca`, `ventas`. La palabra suelta "publicidad" capturaba a
gente que habla *de* publicidad. Cuantificado: de sus 3.287 filas, el 34 % tiene tema
marketing (el universo, 1,2 %) y solo el 20 % etiqueta una marca; los hashtags `#publi`/
`#publicidad`/`#ad`, en cambio, etiquetan marca en el 54 % y "colaboración pagada" en el
72 %. **Fuera "publicidad" suelta; y P excluye el tema marketing** (`MARKETING`). P baja
de 11.938 a 7.816 (0,081 % del universo). Menos, pero son colaboraciones.

**v3 — AUC 0,921, sin fuga.** Lo que pesa ahora: `usuario méxico`, `usuario chile`,
`usuario españa` (marcas con cuenta por país), `lorealistarspain`, `maybelline`,
`activacionesdemarca`, `compartetuintensidad` (campañas). Es decir: **una colaboración se
reconoce por la marca etiquetada y el hashtag de campaña**, y eso es lo que un vídeo sin
declarar también tiene. Residuo B2B menor (`imprenta`, `pvc`, `diseñografico`): rotulistas
que usan `#publicidad` para anunciar sus servicios. Pendiente ampliar `MARKETING`.

| Elkan-Noto (test, 3 ficheros) | valor |
|---|---|
| c = P(etiquetado \| positivo) | 0,077 |
| positivos ocultos entre no etiquetados | 0,66 % |
| … entre los que tienen marcador comercial | 2,3 % |
| prevalencia total estimada (declaradas + ocultas) | 0,74 % |

**Cautela obligatoria:** el estimador `e1` de `c` (media de `g` en positivos de validación)
solo es exacto si las clases son separables; cuando no lo son, **subestima `c` y por tanto
sobreestima los ocultos** (hay test que lo demuestra en `tests/test_pu.py`). Estos números
son una **cota superior**, no una estimación. El siguiente paso es un estimador de `c` más
robusto (top-k de positivos, o TIcE) y, sobre todo, la validación manual: el resultado del
estudio será esa validación, no este número.

Por país, la cota de ocultos entre contenido con marcador comercial: MX 3,7 %, CO 2,0 %,
US 1,7 %. España aún no aparece: con 3 ficheros no llega a las 3.000 filas de test. ALE-115.
