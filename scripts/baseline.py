"""Baseline PU: TF-IDF (palabras + caracteres) + regresión logística. SOLO AGREGADOS.

Uso:  uv run python scripts/baseline.py [glob] [--u N] [--semilla S]

P = declaración textual (publi.lexico.decl), U = muestra del resto del universo
(2025+, sin Shop, sin LIVE). Texto preparado (sin declaraciones, sin handles, sin URLs).
Split por bloques de 2.000 filas del fichero crudo (proxy de creador). El modelo estima
P(s=1|x); tras ajustar el prior al universo real, Elkan-Noto da c y la prevalencia de
positivos ocultos. Escribe informes/baseline.md. Los n-gramas con más peso se listan para
comprobar que no queda fuga de etiqueta.
"""
import argparse
import pathlib
import sys
import time

import duckdb
import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from publi.lexico import COMER, positivo_sql, universo_sql  # noqa: E402
from publi.particion import test_por_clave  # noqa: E402
from publi.pu import ajustar_prior, estimar_c, peso_positivo_no_etiquetado  # noqa: E402
from publi.texto import preparar  # noqa: E402

TAM_BLOQUE = 2_000


def cargar(glob: str, n_u: int, semilla: int):
    con = duckdb.connect()
    con.sql("SET threads=4; SET memory_limit='8GB'")
    con.sql(f"""CREATE TEMP TABLE u AS
        SELECT filename[-10:-8]::int * 1000000 + file_row_number // {TAM_BLOQUE} AS bloque,
               "desc" AS texto, country,
               {positivo_sql()} AS decl,
               regexp_matches(lower("desc"), '{COMER}') AS comer
        FROM read_parquet('{glob}', filename=true, file_row_number=true)
        WHERE {universo_sql()} AND length("desc") >= 10""")
    n_univ, n_pos = con.sql("SELECT count(*), sum(decl::int) FROM u").fetchone()
    pos = con.sql("SELECT bloque, texto, country, comer FROM u WHERE decl").df()
    neg = con.sql(f"SELECT bloque, texto, country, comer FROM u WHERE NOT decl USING SAMPLE {n_u} ROWS (reservoir, {semilla})").df()
    return n_univ, n_pos, pos, neg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glob", nargs="?", default="data/es/videos-*.parquet")
    ap.add_argument("--u", type=int, default=500_000)
    ap.add_argument("--semilla", type=int, default=0)
    a = ap.parse_args()
    t0 = time.perf_counter()

    n_univ, n_pos, pos, neg = cargar(a.glob, a.u, a.semilla)
    pos["s"] = 1
    neg["s"] = 0
    df = np.random.default_rng(a.semilla).permutation(len(pos) + len(neg))
    import pandas as pd
    df = pd.concat([pos, neg], ignore_index=True).iloc[df].reset_index(drop=True)
    df["texto_prep"] = df["texto"].map(preparar)
    es_test = test_por_clave(df["bloque"].to_numpy(), 0.25, a.semilla)
    print(f"[{time.perf_counter()-t0:5.0f}s] universo {n_univ:,} · P {n_pos:,} · U muestreado {len(neg):,} · test {es_test.mean():.0%}", flush=True)

    tr, te = df[~es_test], df[es_test]
    vw = TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_features=200_000, sublinear_tf=True)
    vc = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_features=200_000, sublinear_tf=True)
    Xtr = sp.hstack([vw.fit_transform(tr["texto_prep"]), vc.fit_transform(tr["texto_prep"])]).tocsr()
    Xte = sp.hstack([vw.transform(te["texto_prep"]), vc.transform(te["texto_prep"])]).tocsr()
    print(f"[{time.perf_counter()-t0:5.0f}s] vectorizado: {Xtr.shape[1]:,} rasgos", flush=True)

    clf = LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)
    clf.fit(Xtr, tr["s"])
    g_te = clf.predict_proba(Xte)[:, 1]
    auc, apv = roc_auc_score(te["s"], g_te), average_precision_score(te["s"], g_te)
    print(f"[{time.perf_counter()-t0:5.0f}s] entrenado · AUC(s) {auc:.3f} · AP(s) {apv:.3f}", flush=True)

    # Ajuste de prior: en la muestra P es pi_m; en el universo, pi_r
    pi_m, pi_r = tr["s"].mean(), n_pos / n_univ
    g = ajustar_prior(g_te, pi_m, pi_r)
    s_te = te["s"].to_numpy()
    c = estimar_c(g[s_te == 1])
    w = peso_positivo_no_etiquetado(g[s_te == 0], c)
    u_te = te[s_te == 0].assign(w=w)

    out = [f"# Baseline PU — {a.glob}\n",
           f"Universo {n_univ:,} filas · P {n_pos:,} ({100*pi_r:.3f} %) · U muestreado {len(neg):,} · test por bloques {es_test.mean():.0%}\n",
           "## Discriminación etiquetado vs no etiquetado (test)\n",
           f"| AUC | AP | rasgos |\n|---|---|---|\n| {auc:.3f} | {apv:.3f} | {Xtr.shape[1]:,} |\n",
           "## Elkan-Noto (tras ajuste de prior al universo)\n",
           f"- c = P(etiquetado | positivo) = **{c:.4f}**",
           f"- Positivos ocultos estimados entre los no etiquetados: **{100*u_te['w'].mean():.3f} %**",
           f"- … entre los no etiquetados **con marcador comercial**: **{100*u_te.loc[u_te['comer'], 'w'].mean():.2f} %** (n={int(u_te['comer'].sum()):,})",
           f"- Prevalencia total estimada de colaboraciones (declaradas + ocultas): **{100*(pi_r + (1-pi_r)*u_te['w'].mean()):.3f} %**\n",
           "## Por país (no etiquetados de test)\n",
           "| país | n | % ocultos est. | % ocultos entre comerciales |\n|---|---|---|---|"]
    for pais, grp in u_te.groupby("country"):
        if len(grp) >= 2_000:
            gc = grp[grp["comer"]]
            out.append(f"| {pais} | {len(grp):,} | {100*grp['w'].mean():.3f} % | {100*gc['w'].mean() if len(gc) else float('nan'):.2f} % |")
    nombres = np.concatenate([vw.get_feature_names_out(), vc.get_feature_names_out()])
    top = np.argsort(clf.coef_[0])[::-1][:40]
    out.append("\n## 40 n-gramas con más peso positivo (comprobación de fuga)\n")
    out.append(", ".join(f"`{nombres[i]}`" for i in top))
    out.append(f"\n\n_{time.perf_counter()-t0:.0f} s en total._\n")
    pathlib.Path("informes").mkdir(exist_ok=True)
    pathlib.Path("informes/baseline.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
