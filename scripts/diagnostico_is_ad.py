"""¿Qué significa de verdad `is_ad`? SOLO AGREGADOS.

La tarjeta del dataset dice "marked as sponsored". El perfil contradice que sea "el creador
declaró una colaboración": nace en 2024-25, se concentra en US, casi nunca coincide con
#publi/#ad, y su engagement es el de un catálogo, no el de un creador. Hipótesis: es
contenido de TikTok Shop (vídeo con producto enlazado). Este script reúne la evidencia.
"""
import duckdb

con = duckdb.connect()
con.sql("SET threads=6; SET memory_limit='10GB'")
con.sql("""CREATE TEMP TABLE t AS
    SELECT is_ad, views, likes, comments, mentions, music_title, country, create_time, lower("desc") AS d
    FROM 'data/es/videos-*.parquet' WHERE year(create_time) >= 2025""")

H = lambda tags: f"regexp_matches(d, '(^|\\s)#({tags})(\\s|$|#)')"
grupos = {
    "is_ad = 1": "is_ad = 1",
    "#ad / #ads": H("ad|ads"),
    "#publi / #publicidad": H("publi|publicidad"),
    "#paidpartnership": H("paidpartnership"),
    "orgánico (is_ad=0, sin hashtags de declaración)": f"is_ad = 0 AND NOT {H('ad|ads|publi|publicidad|paidpartnership')}",
}

print("== Firma de engagement por grupo (2025+) ==")
print(f"{'grupo':<50}{'n':>10}{'views p50':>11}{'likes/views':>13}{'coment/views':>14}{'%menciones':>12}{'sonidos/fila':>14}")
for k, c in grupos.items():
    r = con.sql(f"""SELECT count(*), coalesce(median(views),0),
        coalesce(median(CASE WHEN views>0 THEN likes/views END),0),
        coalesce(median(CASE WHEN views>0 THEN comments/views END),0),
        100.0*sum((len(mentions)>0)::int)/count(*),
        count(DISTINCT music_title)::double/count(*)
        FROM t WHERE {c}""").fetchone()
    print(f"{k:<50}{r[0]:>10,}{int(r[1]):>11,}{r[2]:>13.4f}{r[3]:>14.5f}{r[4]:>11.1f}%{r[5]:>14.3f}")
print("  (sonidos/fila: proporción de music_title distintos; bajo = pocas cuentas muy prolíficas)")

print("\n== #paidpartnership: ¿spam o creadores? país y co-hashtags ==")
for c, n in con.sql(f"SELECT country, count(*) FROM t WHERE {H('paidpartnership')} GROUP BY 1 ORDER BY 2 DESC LIMIT 6").fetchall():
    print(f"  {c}  {n:,}")
print("  co-hashtags más frecuentes:")
for tag, n in con.sql(f"""
    SELECT tag, count(*) FROM (SELECT unnest(regexp_extract_all(d, '#([a-z0-9_áéíóúñ]+)', 1)) AS tag FROM t WHERE {H('paidpartnership')})
    WHERE tag <> 'paidpartnership' GROUP BY 1 ORDER BY 2 DESC LIMIT 12""").fetchall():
    print(f"    #{tag:<24}{n:>7,}")

print("\n== is_ad=1: co-hashtags más frecuentes (¿léxico de tienda?) ==")
for tag, n in con.sql("""
    SELECT tag, count(*) FROM (SELECT unnest(regexp_extract_all(d, '#([a-z0-9_áéíóúñ]+)', 1)) AS tag FROM t WHERE is_ad = 1)
    GROUP BY 1 ORDER BY 2 DESC LIMIT 15""").fetchall():
    print(f"    #{tag:<24}{n:>7,}")

print("\n== is_ad=1: léxico de tienda en el caption ==")
for k, p in {"tiktokshop / tiktok shop": r"tiktok ?shop", "envío/envio gratis": r"env[ií]o gratis", "carrito / cesta": r"\b(carrito|cesta)\b",
             "oferta/descuento/promo": r"\b(oferta|descuento|promo)", "link en bio": r"link en (la |mi )?bio"}.items():
    a, o = con.sql(f"""SELECT 100.0*sum(CASE WHEN is_ad=1 THEN regexp_matches(d,'{p}')::int END)/sum(is_ad),
                              100.0*sum(CASE WHEN is_ad=0 THEN regexp_matches(d,'{p}')::int END)/sum(1-is_ad) FROM t""").fetchone()
    print(f"  {k:<26} is_ad=1: {a:5.2f} %   is_ad=0: {o:5.2f} %   ratio ×{a/max(o,1e-9):.1f}")
