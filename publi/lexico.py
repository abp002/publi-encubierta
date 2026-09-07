"""Única fuente de verdad de los patrones léxicos.

Las LISTAS son una; el patrón se genera por motor, porque el límite de hashtag difiere:
RE2 (DuckDB) no tiene lookahead y consume el separador; `re` (Python) usa lookahead para
no comerse el espacio o el `#` siguiente al enmascarar.

Por qué cada exclusión, en NOTEBOOK.md (2026-09-07):
- #paidpartnership: programa LIVE de TikTok, no marcas.   - #pr: Puerto Rico.
- #colab, "regalo de": colaboraciones entre creadores, cumpleaños.
- #ad se queda con cautela: en US lo usan afiliados de TikTok Shop, que salen por is_ad.
"""
import re

HASHTAGS_DECL = "ad|ads|publi|publicidad|anuncio|patrocinado|sponsored|colaboracionpagada"
PALABRAS_DECL = r"publicidad|patrocinad[oa]s?|colaboraci[oó]n pagada|contenido pagado|en colaboraci[oó]n con|producto regalado"
HASHTAGS_LIVE = "liveincentiveprogram|paidpartnership"

# Marcador comercial sin declaración: candidatos de la cascada (sin lookahead: vale en ambos motores)
COMER = (r"link en (la |mi )?bio|\bc[oó]digo\b|\bdescuento|\benv[ií]o gratis|\bcup[oó]n|\boferta|\bpromo"
         r"|\bcompra|\btienda|\bdisponible en|\bpedidos?\b|\bwhatsapp|€|\d+\s?%")


def _hashtags(tags: str, motor: str) -> str:
    fin = r"(?=\s|$|#)" if motor == "py" else r"(\s|$|#)"
    return rf"(^|\s)#({tags}){fin}"


def decl(motor: str = "re2") -> str:
    """Declaración de colaboración con marca: define los positivos P."""
    return _hashtags(HASHTAGS_DECL, motor) + rf"|\b({PALABRAS_DECL})\b"


def live(motor: str = "re2") -> str:
    """Programa LIVE de TikTok: fuera del universo."""
    return _hashtags(HASHTAGS_LIVE, motor)


RE_DECL = re.compile(decl("py"), re.IGNORECASE)
RE_LIVE = re.compile(live("py"), re.IGNORECASE)
RE_COMER = re.compile(COMER, re.IGNORECASE)
