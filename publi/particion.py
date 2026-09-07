"""Partición train/test por bloques contiguos.

No hay author_id, pero las filas conservan el orden de almacenamiento, que agrupa por
creador. Un split aleatorio por fila mete al mismo creador a ambos lados y el modelo
memoriza estilos en vez de aprender señal. Se parte por bloques contiguos: alguna cuenta
quedará cortada en la frontera de un bloque, pero es una fuga marginal frente a la otra.
"""
import numpy as np


def bloques_test(n_filas: int, tam_bloque: int, frac_test: float, semilla: int = 0) -> np.ndarray:
    """Máscara booleana de longitud n_filas: True = test. Bloques enteros, elegidos al azar."""
    if n_filas <= 0 or tam_bloque <= 0 or not 0.0 < frac_test < 1.0:
        raise ValueError("n_filas y tam_bloque > 0; frac_test en (0, 1)")
    n_bloques = -(-n_filas // tam_bloque)
    rng = np.random.default_rng(semilla)
    en_test = rng.random(n_bloques) < frac_test
    return np.repeat(en_test, tam_bloque)[:n_filas]


def test_por_clave(claves, frac_test: float, semilla: int = 0) -> np.ndarray:
    """Máscara True = test, con todas las filas de una misma clave en el mismo lado.
    claves: array de enteros (p. ej. bloque = file_row_number // 2000 por fichero)."""
    if not 0.0 < frac_test < 1.0:
        raise ValueError("frac_test en (0, 1)")
    claves = np.asarray(claves)
    unicas, inversa = np.unique(claves, return_inverse=True)
    rng = np.random.default_rng(semilla)
    en_test = rng.random(unicas.size) < frac_test
    return en_test[inversa]
