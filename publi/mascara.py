"""Enmascarado de los tokens de declaración.

Si los positivos se definen por "#publi", un clasificador aprende "#publi" y nada más.
Antes de vectorizar se elimina cualquier coincidencia de MASCARA (raíces: publi*, patrocin*,
anunci*, sponsor*, colab*, regalad*, pagada, ad/ads), superconjunto amplio del léxico que
define P. Un caption declarado y su gemelo sin declarar producen el mismo texto de entrada.
Se elimina (no se sustituye por un token): un token también filtraría la etiqueta.
"""
import re

from publi.lexico import RE_MASCARA

_ESPACIOS = re.compile(r"\s+")


def enmascarar(texto: str) -> str:
    """Quita las declaraciones y normaliza espacios. Idempotente."""
    sin = RE_MASCARA.sub(" ", texto or "")
    return _ESPACIOS.sub(" ", sin).strip()
