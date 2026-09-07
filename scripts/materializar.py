"""Fase B — descargar ficheros crudos y materializar el subconjunto en español.

Uso:  uv run python scripts/materializar.py 0 1 2

Por cada índice: descarga videos-XX.parquet a data/raw/ (si no está), extrae las filas con
language = 'es' a data/es/videos-XX.parquet (zstd) y apunta filas y positivos en
data/es/resumen.jsonl. Nada de data/ se versiona. Escala a los 27 ficheros sin cambios;
si el disco aprieta, borrar data/raw/ tras extraer (los crudos solo sirven para re-extraer).
"""
import json
import pathlib
import sys
import time

import duckdb
from huggingface_hub import hf_hub_download

REPO = "kuben-developer/tiktok-videos-4b"
RAW = pathlib.Path("data/raw")
ES = pathlib.Path("data/es")
COLS = ('content_id, create_time, "desc", mentions, duration, is_video, music_id, music_title, '
        'views, likes, comments, shares, saves, country, language, is_ad')


def conectar() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.sql("SET threads=6; SET memory_limit='10GB'; SET temp_directory='/tmp/duckdb_spill'")
    return con


def materializar(con, i: int) -> None:
    nombre = f"videos-{i:02d}.parquet"
    salida = ES / nombre
    if salida.exists():
        print(f"{nombre}: ya materializado, salto", flush=True)
        return

    t = time.perf_counter()
    ruta = hf_hub_download(REPO, nombre, repo_type="dataset", local_dir=str(RAW))
    t_dl = time.perf_counter() - t
    print(f"[{t_dl:7.0f}s] descargado {nombre}", flush=True)

    t = time.perf_counter()
    con.sql(f"COPY (SELECT {COLS} FROM '{ruta}' WHERE language = 'es') "
            f"TO '{salida}' (FORMAT parquet, COMPRESSION zstd)")
    n, ads = con.sql(f"SELECT count(*), sum(is_ad) FROM '{salida}'").fetchone()
    t_ex = time.perf_counter() - t
    mb = salida.stat().st_size / 1e6
    print(f"[{t_ex:7.0f}s] {nombre}: {n:,} filas es, {ads:,} is_ad=1 ({100 * ads / n:.2f} %) -> {mb:.0f} MB", flush=True)

    with open(ES / "resumen.jsonl", "a") as f:
        f.write(json.dumps({"fichero": nombre, "filas_es": n, "is_ad": ads,
                            "seg_descarga": round(t_dl), "seg_extraccion": round(t_ex), "mb": round(mb)}) + "\n")


def main(indices):
    RAW.mkdir(parents=True, exist_ok=True)
    ES.mkdir(parents=True, exist_ok=True)
    con = conectar()
    for i in indices:
        materializar(con, i)


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [0])
