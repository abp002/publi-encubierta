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
