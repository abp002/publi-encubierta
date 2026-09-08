# publi-encubierta

Detector de publicidad no declarada en captions de TikTok (español e inglés), sobre el
dataset público `kuben-developer/tiktok-videos-4b` (Hugging Face: 4,5B filas, 27 Parquet
de 10,7 GB, licencia research-use, recolectado contra los ToS de TikTok; datos personales
bajo RGPD). Enfoque: PU learning (los `is_ad = 0` son *no etiquetados*, no negativos).

## QA
Nivel: activo
Bitácora: Alejandro

## Cómo se levanta
    uv sync
    uv run python scripts/sondeo_remoto.py --solo-metadatos   # sonda sin descargar nada
    uv run python scripts/sondeo_remoto.py                    # + escaneo de is_ad y language

## Reglas del repo (no negociables)
- `data/` y `*.parquet` jamás se commitean: `.gitignore` es allowlist.
- Ningún caption íntegro ni `content_id` en ficheros versionados, informes ni blog.
  Solo agregados. El resultado es estadístico, nunca un señalamiento de cuentas.
- DuckDB siempre con `threads=6` y `memory_limit='10GB'` para que el Mac siga usable.
- No usar `datasets.load_dataset()` sin `streaming=True`: duplica el disco en Arrow.
- Subconjunto legítimo: las 27 particiones van por hash de creador, así que usar 3-5
  ficheros es muestreo aleatorio insesgado del conjunto recolectado.

## Bitácora pública
El proceso, con fecha y decisiones, va en `NOTEBOOK.md`. El porqué de las decisiones
que sirven fuera de este repo va al vault con `/apuntar`.

## Estado y cómo retomar (actualizado 2026-09-08)

**Dónde está todo**
- `data/es/videos-00..26.parquet` — todo el español del dataset (140,5M filas, 11 GB). `data/raw/videos-00..02` — tres crudos (30 GB) por si hay que re-extraer. `data/es/resumen.jsonl` — filas y tiempos por fichero. Nada de esto se versiona.
- `publi/lexico.py` — **única fuente de verdad** de qué es positivo (`positivo_sql`), qué entra en el universo (`universo_sql`), qué se enmascara (`MASCARA`). Cualquier cambio de criterio se hace aquí y se propaga solo.
- `publi/mascara.py`, `publi/texto.py`, `publi/particion.py`, `publi/pu.py` — lógica con tests (`uv run pytest`, 24).
- `scripts/` — `sondeo_remoto.py` (fase A, sin descargar), `materializar.py` (descarga+extrae), `perfilar_es.py` → `informes/perfil_es.md`, `diagnostico_is_ad.py`, `validar_country.py`, `baseline.py` → `informes/baseline.md`.
- `NOTEBOOK.md` — la bitácora: leerla entera antes de tocar nada (8 entradas, 2026-09-07).

**Lo que hay que saber para no repetir errores**
- `is_ad` = TikTok Shop, no colaboración declarada. `#paidpartnership` = programa LIVE de TikTok. `country = US` = región desconocida. Todo demostrado en la bitácora; no volver a discutirlo.
- Los positivos son léxico español (`#publi`, patrocinado, colaboración pagada…). La palabra suelta "publicidad" NO (agencias). El tema-marketing se excluye de P.
- El enmascarado es por raíces y frases, superconjunto del léxico de etiquetar. Si se añade una forma a `PALABRAS_DECL`/`HASHTAGS_DECL`, hay que cubrirla en `MASCARA` y añadir el n-grama a `tests/test_mascara.py::test_fuga_del_baseline_cerrada`.
- Comprobación de fuga obligatoria tras cualquier cambio del modelo: la lista de 40 n-gramas al final de `informes/baseline.md`. Si aparece un trozo de "publi"/"anunc"/"pagad", hay fuga.

**Números de referencia (27 ficheros, universo v2)**: 85,4M filas; P 63.760 (ES 13.763); baseline AUC 0,945, c 0,143, ocultos 0,30 % (1,30 % entre los con marcador comercial). Son cota superior: ver limitaciones en la bitácora (noche, V).

**Siguiente paso (ALE-116)**: 7) `c` por país; 8) estimador de `c` más robusto que `e1`; 9) rúbrica de validación manual **con el usuario, antes de mirar candidatos**. Después, la cascada sobre los 3,5M candidatos y la validación.

**Comandos**
    uv run pytest -q                                   # 24 tests
    uv run python scripts/perfilar_es.py               # ~2 min, 27 ficheros
    uv run python scripts/baseline.py --u 1500000      # ~10 min en el M4; --u 500000 para iterar
    uv run python scripts/baseline.py "data/es/videos-0[0-2].parquet"   # 3 ficheros, ~2 min
