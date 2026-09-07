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
# Sin la palabra suelta "publicidad": 34 % de sus filas hablan DE publicidad (agencias,
# locutores, "publicidad engañosa") y solo 20 % etiquetan una marca. Ver NOTEBOOK 2026-09-07.
PALABRAS_DECL = r"patrocinad[oa]s?|colab(oraci[oó]n)? pagada|contenido pagado|en colaboraci[oó]n con|productos? regalados?|regalo de la marca"
HASHTAGS_LIVE = "liveincentiveprogram|paidpartnership"

# Cuentas cuyo tema es la publicidad (agencias, locutores, cursos): no son creadores declarando.
# Se excluyen de P (precisión), no del universo.
MARKETING = (r"\b(agencia|marketing|mercadeo|locuci[oó]n|locutor|ventas|tu marca|tu negocio|tu empresa|"
             r"emprendedor|clientes|engañosa|curso|estrategia|branding|community manager|dise[ñn]o gr[aá]fico|spot|jingle)\b")

# Enmascarado para los RASGOS: superconjunto por raíces del léxico de etiquetar. Sobre-enmascarar
# es seguro (se pierde un poco de señal); sub-enmascarar es fuga. El baseline del 2026-09-07
# aprendió `blici`, `ubli`, `anunc`, `pagada` con el enmascarado estrecho.
MASCARA = (r"\ben colab\w* con\b|\bpatrocin\w* por\b|\bgracias a\b"        # frases enteras primero (residuos "en con", "por")
           r"|#?\w*(publi|patrocin|anunci|sponsor|colab|regalad|partnership)\w*|\bpagad[oa]s?\b|\bads?\b|\bpr\b")

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


def positivo_sql(col: str = 'lower("desc")') -> str:
    """Expresión SQL (RE2) que define P: declaración y no tema-marketing."""
    return f"(regexp_matches({col}, '{decl()}') AND NOT regexp_matches({col}, '{MARKETING}'))"


RE_DECL = re.compile(decl("py"), re.IGNORECASE)
RE_MARKETING = re.compile(MARKETING, re.IGNORECASE)
RE_MASCARA = re.compile(MASCARA, re.IGNORECASE)
RE_LIVE = re.compile(live("py"), re.IGNORECASE)
RE_COMER = re.compile(COMER, re.IGNORECASE)
