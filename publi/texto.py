"""Preparación del caption antes de vectorizar.

1. Quita las declaraciones (fuga de etiqueta): publi.mascara.
2. Sustituye @handles por un token: que haya una mención es señal (la marca etiquetada,
   57 % en positivos); *cuál* es identifica al creador o a la marca y el modelo la memoriza.
3. Sustituye URLs por un token por la misma razón.
"""
import re

from publi.mascara import enmascarar

_MENCION = re.compile(r"@[\w.]+")
_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def preparar(texto: str) -> str:
    t = enmascarar(texto)
    t = _URL.sub(" URL ", t)
    t = _MENCION.sub(" @usuario ", t)
    return re.sub(r"\s+", " ", t).strip().lower()
