"""Fase A — sondeo remoto del dataset sin descargar nada.

Lee videos-00.parquet directamente de Hugging Face por HTTP (range requests)
y responde las dos preguntas que deciden si el proyecto vive:
  1. prevalencia de is_ad          -> ¿hay positivos suficientes?
  2. distribución de language      -> ¿cuánto es "un"? ¿sirve la columna o hay que detectar idioma?
"""
import argparse
import time

import duckdb

BASE = "https://huggingface.co/datasets/kuben-developer/tiktok-videos-4b/resolve/main"
FICHERO = f"{BASE}/videos-00.parquet"


def conectar() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs;")
    # Límites para que el Mac siga usable (24 GB RAM, 10 cores)
    con.sql("SET threads=6")
    con.sql("SET memory_limit='10GB'")
    con.sql("SET temp_directory='/tmp/duckdb_spill'")
    return con


def cronometrar(nombre, fn):
    t = time.perf_counter()
    r = fn()
    print(f"[{time.perf_counter() - t:7.1f}s] {nombre}", flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-metadatos", action="store_true", help="no escanea columnas, solo lee el pie del Parquet")
    a = ap.parse_args()
    con = conectar()

    n = cronometrar("count(*) — solo metadatos", lambda: con.sql(f"SELECT count(*) FROM '{FICHERO}'").fetchone()[0])
    print(f"   filas: {n:,}")

    rg = cronometrar("row groups", lambda: con.sql(
        f"SELECT count(DISTINCT row_group_id), min(row_group_num_rows), max(row_group_num_rows) "
        f"FROM parquet_metadata('{FICHERO}')").fetchone())
    print(f"   row groups: {rg[0]:,}   filas/rg: {rg[1]:,} – {rg[2]:,}")

    tam = cronometrar("tamaño comprimido por columna", lambda: con.sql(f"""
        SELECT path_in_schema AS col, round(sum(total_compressed_size)/1e9, 2) AS gb
        FROM parquet_metadata('{FICHERO}') GROUP BY 1 ORDER BY 2 DESC""").fetchall())
    for col, gb in tam:
        print(f"   {gb:6.2f} GB  {col}")

    if a.solo_metadatos:
        return

    ad = cronometrar("prevalencia is_ad", lambda: con.sql(f"""
        SELECT is_ad, count(*) AS n, round(100.0*count(*)/sum(count(*)) OVER (), 3) AS pct
        FROM '{FICHERO}' GROUP BY 1 ORDER BY 1""").fetchall())
    for r in ad:
        print(f"   is_ad={r[0]}  {r[1]:>13,}  {r[2]:6.3f}%")

    lang = cronometrar("distribución language (top 25)", lambda: con.sql(f"""
        SELECT language, count(*) AS n, round(100.0*count(*)/sum(count(*)) OVER (), 2) AS pct
        FROM '{FICHERO}' GROUP BY 1 ORDER BY 2 DESC LIMIT 25""").fetchall())
    for r in lang:
        print(f"   {str(r[0]):>4}  {r[1]:>13,}  {r[2]:6.2f}%")

    cruce = cronometrar("is_ad por idioma (es, en, pt, un)", lambda: con.sql(f"""
        SELECT language, count(*) AS n, sum(is_ad) AS ads, round(100.0*sum(is_ad)/count(*), 3) AS pct_ad
        FROM '{FICHERO}' WHERE language IN ('es','en','pt','un') GROUP BY 1 ORDER BY 2 DESC""").fetchall())
    for r in cruce:
        print(f"   {r[0]:>4}  n={r[1]:>13,}  ads={r[2]:>10,}  {r[3]:6.3f}%")


if __name__ == "__main__":
    main()
