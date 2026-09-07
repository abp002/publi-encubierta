"""Única fuente de verdad de los patrones léxicos. Los usan DuckDB (RE2) y Python (re):
solo se emplea sintaxis común a ambos (nada de \\p{..} aquí).

Por qué cada exclusión, en NOTEBOOK.md (2026-09-07):
- #paidpartnership: programa LIVE de TikTok, no marcas.  - #pr: Puerto Rico.
- #colab, "regalo de": colaboraciones entre creadores, cumpleaños.
- #ad se queda con cautela: en US lo usan afiliados de TikTok Shop, que salen por is_ad.
"""
import re

# Declaración de colaboración con marca (define los positivos P)
DECL = (r"(^|\s)#(ad|ads|publi|publicidad|anuncio|patrocinado|sponsored|colaboracionpagada)(?=\s|$|#)"
        r"|\b(publicidad|patrocinad[oa]s?|colaboraci[oó]n pagada|contenido pagado|en colaboraci[oó]n con|producto regalado)\b")

# Programa LIVE de TikTok: fuera del universo
LIVE = r"(^|\s)#(liveincentiveprogram|paidpartnership)(?=\s|$|#)"

# Marcador comercial sin declaración: candidatos de la cascada
COMER = (r"link en (la |mi )?bio|\bc[oó]digo\b|\bdescuento|\benv[ií]o gratis|\bcup[oó]n|\boferta|\bpromo"
         r"|\bcompra|\btienda|\bdisponible en|\bpedidos?\b|\bwhatsapp|€|\d+\s?%")

RE_DECL = re.compile(DECL, re.IGNORECASE)
RE_LIVE = re.compile(LIVE, re.IGNORECASE)
RE_COMER = re.compile(COMER, re.IGNORECASE)
