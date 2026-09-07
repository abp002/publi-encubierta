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
