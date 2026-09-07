"""Enmascarado de los tokens de declaración.

Si los positivos se definen por "#publi", un clasificador aprende "#publi" y nada más.
Antes de vectorizar se elimina cualquier coincidencia de DECL, de modo que un caption
declarado y su gemelo sin declarar produzcan exactamente el mismo texto de entrada.
Se elimina (no se sustituye por un token): un token también filtraría la etiqueta.
"""
import re

from publi.lexico import RE_DECL

_ESPACIOS = re.compile(r"\s+")


def enmascarar(texto: str) -> str:
    """Quita las declaraciones y normaliza espacios. Idempotente."""
    sin = RE_DECL.sub(" ", texto or "")
    return _ESPACIOS.sub(" ", sin).strip()
