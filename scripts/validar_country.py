"""¿Significa algo la columna `country`? SOLO AGREGADOS.

El 76 % del contenido en español lleva US, lo que huele a artefacto de la recolección.
Antes de hacer contraste por país hay que saber si la etiqueta vale al menos como agregado:
las filas ES deberían mostrar léxico peninsular (vosotros, vuestro, €, coche, móvil…) y las
de LATAM el suyo (ustedes, $, carro, celular, voseo…). Si no hay separación, el contraste
por país no se puede defender.
"""
import duckdb

con = duckdb.connect()
con.sql("SET threads=6; SET memory_limit='10GB'")

PENINSULAR = (r"\b(vosotros|vosotras|vuestr[oa]s?|os\b|euros?|coche|m[oó]vil|ordenador|zumo|curro|chaval(es|a|as)?|"
              r"mola|molan|guay|flipo|flipa|apetece|vale tío|tío|tía)\b|€")
LATAM = (r"\b(ustedes|pesos|carro|celular|computadora|jugo|plata|ch[eé]vere|g[üu]ey|wey|vos|ahorita|platicar|"
         r"che|boludo|parcero|parce|chido|padre|neta|bacano|pana)\b|\$")

con.sql(f"""CREATE TEMP TABLE t AS
    SELECT country,
           regexp_matches(lower("desc"), '{PENINSULAR}') AS pen,
           regexp_matches(lower("desc"), '{LATAM}') AS lat
    FROM 'data/es/videos-*.parquet'
    WHERE year(create_time) >= 2025 AND length("desc") >= 20""")

print("Filas 2025+ con caption de ≥ 20 caracteres. pen = léxico peninsular; lat = léxico LATAM.\n")
print(f"{'país':>5} {'filas':>10} {'% pen':>7} {'% lat':>7} {'pen/lat':>8}   {'solo pen':>9} {'solo lat':>9}")
for c, n, p, l, sp, sl in con.sql("""
    SELECT country, count(*), 100.0*sum(pen::int)/count(*), 100.0*sum(lat::int)/count(*),
           100.0*sum((pen AND NOT lat)::int)/count(*), 100.0*sum((lat AND NOT pen)::int)/count(*)
    FROM t GROUP BY 1 HAVING count(*) > 20000 ORDER BY 2 DESC""").fetchall():
    print(f"{c:>5} {n:>10,} {p:>6.2f}% {l:>6.2f}% {p/max(l,1e-9):>8.2f}   {sp:>8.2f}% {sl:>8.2f}%")
