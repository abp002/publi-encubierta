"""Fase B — perfilado del subconjunto en español. SOLO AGREGADOS: ni un caption sale de aquí.

Uso:  uv run python scripts/perfilar_es.py [glob]     (por defecto data/es/videos-*.parquet)

Responde: cuántos positivos hay y dónde (país), qué aspecto tiene un caption (longitud),
y cuánto pesa cada marcador léxico. Distingue tres estados que el estudio necesita separar:
  - etiqueta de plataforma  (is_ad = 1: el creador activó "contenido comercial")
  - declaración en el texto (#publi, "colaboración pagada", #ad…)
  - marcador comercial sin declaración (link en bio, código, descuento, €…): la piscina
    de candidatos para la cascada.
Escribe el informe en informes/perfil_es.md (versionable: no contiene datos personales).
"""
import pathlib
import sys

import duckdb

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

GLOB = sys.argv[1] if len(sys.argv) > 1 else "data/es/videos-*.parquet"
INFORME = pathlib.Path("informes/perfil_es.md")

# Marcadores. Minúsculas; RE2 (\b funciona con ASCII, por eso las tildes van explícitas)
from publi.lexico import COMER, positivo_sql, universo_sql  # única fuente de verdad; ver NOTEBOOK 2026-09-07


def main():
    con = duckdb.connect()
    con.sql("SET threads=6; SET memory_limit='10GB'")
    con.sql(f"""
        CREATE TEMP TABLE t AS
        SELECT is_ad, country, create_time,
               length(regexp_replace(lower("desc"), '[^\\p{{L}}]', '', 'g')) AS letras,
               {positivo_sql()} AS decl,
               regexp_matches(lower("desc"), '{COMER}') AS comer,
               NOT {universo_sql()} AS fuera
        FROM '{GLOB}'""")

    out = []
    p = out.append
    tot, ads = con.sql("SELECT count(*), sum(is_ad) FROM t").fetchone()
    p(f"# Perfil del subconjunto en español\n\nFuente: `{GLOB}` — {tot:,} filas, {ads:,} con `is_ad = 1` ({100*ads/tot:.2f} %).\n")

    p("## Tres estados: etiqueta de plataforma, declaración en texto, marcador comercial\n")
    p("| Estado | filas | % del total | de ellas is_ad=1 | % is_ad |")
    p("|---|---|---|---|---|")
    for nombre, cond in [("Declaración en texto (cualquiera)", "decl"),
                         ("Marcador comercial (cualquiera)", "comer"),
                         ("Comercial SIN declaración", "comer AND NOT decl"),
                         ("Declaración SIN marcador comercial", "decl AND NOT comer"),
                         ("Ni lo uno ni lo otro", "NOT decl AND NOT comer")]:
        n, a = con.sql(f"SELECT count(*), sum(is_ad) FROM t WHERE {cond}").fetchone()
        p(f"| {nombre} | {n:,} | {100*n/tot:.2f} % | {a:,} | {100*a/max(n,1):.2f} % |")
    d_ad, = con.sql("SELECT sum(decl::int) FROM t WHERE is_ad = 1").fetchone()
    p(f"\n- P(declaración en texto | is_ad=1) = **{100*d_ad/ads:.1f} %** — cuántos etiquetados además lo dicen.")
    n_d, a_d = con.sql("SELECT count(*), sum(is_ad) FROM t WHERE decl").fetchone()
    p(f"- P(is_ad=1 | declaración en texto) = **{100*a_d/max(n_d,1):.1f} %** — cuántos que lo declaran por escrito NO llevan la etiqueta de plataforma: {n_d - a_d:,} filas.\n")

    p("## Por país (top 15 por volumen)\n")
    p("| país | filas | % is_ad | % decl. texto | % comercial sin decl. |")
    p("|---|---|---|---|---|")
    for c, n, a, d, cs in con.sql("""
        SELECT country, count(*), 100.0*sum(is_ad)/count(*), 100.0*sum(decl::int)/count(*),
               100.0*sum((comer AND NOT decl)::int)/count(*)
        FROM t GROUP BY 1 ORDER BY 2 DESC LIMIT 15""").fetchall():
        p(f"| {c} | {n:,} | {a:.2f} % | {d:.2f} % | {cs:.2f} % |")

    p("\n## Longitud del caption (letras, sin hashtags ni menciones)\n")
    q = con.sql("SELECT quantile_cont(letras, [0.1,0.25,0.5,0.75,0.9,0.99]) FROM t").fetchone()[0]
    p("| p10 | p25 | p50 | p75 | p90 | p99 |\n|---|---|---|---|---|---|")
    p("| " + " | ".join(f"{int(v)}" for v in q) + " |")
    qa = con.sql("SELECT quantile_cont(letras, [0.1,0.5,0.9]) FROM t WHERE is_ad=1").fetchone()[0]
    p(f"\nSolo `is_ad = 1`: p10 {int(qa[0])}, p50 {int(qa[1])}, p90 {int(qa[2])}.")

    p("\n## Por año de publicación\n")
    p("| año | filas | % is_ad |\n|---|---|---|")
    for y, n, a in con.sql("SELECT year(create_time), count(*), 100.0*sum(is_ad)/count(*) FROM t GROUP BY 1 ORDER BY 1").fetchall():
        p(f"| {y} | {n:,} | {a:.2f} % |")

    p("\n## Universo del estudio (lo que entra en la fase C)\n")
    p("Filtro (`publi.lexico.universo_sql`): `create_time >= 2025`, `is_ad = 0` y sin léxico de TikTok Shop "
      "(comercio con producto enlazado, señalizado por diseño), sin `#liveincentiveprogram`/`#paidpartnership` (programa LIVE).\n")
    p("| | filas | con declaración | % declarado |\n|---|---|---|---|")
    u, d = con.sql("SELECT count(*), sum(decl::int) FROM t WHERE NOT fuera").fetchone()
    p(f"| Universo | {u:,} | {d:,} | {100*d/u:.2f} % |")
    uc, dc = con.sql("SELECT count(*), sum(decl::int) FROM t WHERE NOT fuera AND comer").fetchone()
    p(f"| … con marcador comercial (candidatos de la cascada) | {uc:,} | {dc:,} | {100*dc/max(uc,1):.2f} % |")
    p("\nPor país (top 8):\n\n| país | universo | declarados | % declarado | % comercial sin decl. |\n|---|---|---|---|---|")
    for c, n, dd, cs in con.sql("""SELECT country, count(*), sum(decl::int), 100.0*sum((comer AND NOT decl)::int)/count(*)
        FROM t WHERE NOT fuera GROUP BY 1 ORDER BY 2 DESC LIMIT 8""").fetchall():
        p(f"| {c} | {n:,} | {dd:,} | {100*dd/n:.2f} % | {cs:.2f} % |")

    INFORME.parent.mkdir(exist_ok=True)
    INFORME.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
