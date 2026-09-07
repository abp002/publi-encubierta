"""Corrección PU (positive-unlabeled) de Elkan & Noto (2008).

Supuesto SCAR: la probabilidad de que un positivo esté etiquetado es una constante c,
independiente del caption. Un clasificador g entrenado con "etiquetado vs no etiquetado"
estima P(s=1|x) = c · P(y=1|x). De ahí:
  - c se estima como la media de g(x) sobre positivos etiquetados NO vistos en el entrenamiento;
  - P(y=1|x) = g(x) / c;
  - para un no etiquetado, P(y=1|x, s=0) = ((1-c)/c) · g(x)/(1-g(x)).
"""
import numpy as np


def estimar_c(g_positivos_heldout: np.ndarray) -> float:
    """Estimador e1: media de g sobre positivos etiquetados de validación."""
    g = np.asarray(g_positivos_heldout, dtype=float)
    if g.size == 0:
        raise ValueError("hacen falta positivos etiquetados de validación para estimar c")
    c = float(g.mean())
    if not 0.0 < c <= 1.0:
        raise ValueError(f"c fuera de (0, 1]: {c}")
    return c


def corregir(g: np.ndarray, c: float) -> np.ndarray:
    """P(y=1|x) = g/c, acotado a [0, 1]."""
    return np.clip(np.asarray(g, dtype=float) / c, 0.0, 1.0)


def peso_positivo_no_etiquetado(g: np.ndarray, c: float) -> np.ndarray:
    """P(y=1 | x, s=0): probabilidad de que un no etiquetado sea en realidad positivo."""
    g = np.clip(np.asarray(g, dtype=float), 1e-9, 1 - 1e-9)
    return np.clip((1.0 - c) / c * g / (1.0 - g), 0.0, 1.0)


def prevalencia_en_no_etiquetados(g_no_etiquetados: np.ndarray, c: float) -> float:
    """Fracción estimada de positivos ocultos entre los no etiquetados."""
    return float(peso_positivo_no_etiquetado(g_no_etiquetados, c).mean())


def ajustar_prior(g: np.ndarray, pi_muestra: float, pi_real: float) -> np.ndarray:
    """Corrige P(s=1|x) cuando se entrenó con una proporción de etiquetados distinta de la real.
    Se entrena con P:U submuestreado (p. ej. 2 %) pero en el universo P es el 0,12 %: sin este
    ajuste g no es P(s=1|x) y la corrección de Elkan-Noto queda inflada. Ajuste de odds."""
    if not (0 < pi_muestra < 1 and 0 < pi_real < 1):
        raise ValueError("proporciones en (0, 1)")
    g = np.clip(np.asarray(g, dtype=float), 1e-12, 1 - 1e-12)
    r = (pi_real / (1 - pi_real)) / (pi_muestra / (1 - pi_muestra))
    odds = g / (1 - g) * r
    return odds / (1 + odds)
