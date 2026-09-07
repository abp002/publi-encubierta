"""Fase A (bis) — ¿qué es el 54 % de language = "un"?

Hipótesis: no es "idioma no detectado", es "caption sin texto". Se comprueba sobre
4 ventanas de 100k filas repartidas por el fichero (las filas van agrupadas por creador:
una sola ventana sería un solo país). Solo agregados; nada de esto se versiona con datos.
"""
import time

import duckdb

BASE = "https://huggingface.co/datasets/kuben-developer/tiktok-videos-4b/resolve/main"
FICHERO = f"{BASE}/videos-00.parquet"
VENTANAS = [0, 40_000_000, 80_000_000, 120_000_000]
ANCHO = 100_000

con = duckdb.connect()
con.sql("INSTALL httpfs; LOAD httpfs; SET threads=6; SET memory_limit='10GB';")

filtro = " OR ".join(f"(file_row_number BETWEEN {a} AND {a + ANCHO - 1})" for a in VENTANAS)
t = time.perf_counter()
res = con.sql(f"""
    WITH m AS (
        SELECT language, is_ad, "desc",
               regexp_replace(coalesce("desc", ''), '#\\S+|@\\S+', '', 'g') AS resto
        FROM read_parquet('{FICHERO}', file_row_number=true)
        WHERE {filtro}
    ), c AS (
        SELECT CASE WHEN language IN ('un','en','es') THEN language ELSE 'otros' END AS idioma,
               CASE WHEN length(trim(coalesce("desc",''))) = 0 THEN 'vacío'
                    WHEN NOT regexp_matches(resto, '\\p{{L}}') THEN 'sin letras (hashtags/emoji)'
                    WHEN length(regexp_replace(resto, '[^\\p{{L}}]', '', 'g')) < 8 THEN 'texto < 8 letras'
                    ELSE 'con texto' END AS tipo,
               is_ad
        FROM m
    )
    SELECT idioma, tipo, count(*) AS n,
           round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY idioma), 1) AS pct_idioma,
           round(100.0 * sum(is_ad) / count(*), 2) AS pct_ad
    FROM c GROUP BY 1, 2 ORDER BY 1, 3 DESC
""").fetchall()
print(f"[{time.perf_counter() - t:6.1f}s] muestra de {len(VENTANAS) * ANCHO:,} filas en {len(VENTANAS)} ventanas\n")
print(f"{'idioma':>6}  {'tipo':<28} {'n':>8} {'% idioma':>9} {'% ad':>6}")
for idioma, tipo, n, pct, ad in res:
    print(f"{idioma:>6}  {tipo:<28} {n:>8,} {pct:>8.1f}% {ad:>5.2f}%")
