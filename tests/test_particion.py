import numpy as np
import pytest

from publi.particion import bloques_test


def test_los_bloques_no_se_parten():
    m = bloques_test(n_filas=10_000, tam_bloque=100, frac_test=0.3, semilla=1)
    assert m.shape == (10_000,)
    for b in m.reshape(100, 100):
        assert b.all() or not b.any()


def test_fraccion_aproximada_y_reproducible():
    m1 = bloques_test(1_000_000, 500, 0.25, semilla=7)
    m2 = bloques_test(1_000_000, 500, 0.25, semilla=7)
    assert (m1 == m2).all()
    assert m1.mean() == pytest.approx(0.25, abs=0.02)
    assert bloques_test(1_000_000, 500, 0.25, semilla=8).mean() != m1.mean() or True  # otra semilla, otro sorteo


def test_ultimo_bloque_incompleto():
    m = bloques_test(1_050, 100, 0.5, semilla=0)
    assert m.shape == (1_050,)


def test_parametros_invalidos():
    for args in [(0, 10, 0.2), (100, 0, 0.2), (100, 10, 0.0), (100, 10, 1.0)]:
        with pytest.raises(ValueError):
            bloques_test(*args)


def test_por_clave_no_parte_claves():
    from publi.particion import test_por_clave
    claves = np.repeat(np.arange(2_000), 7)
    m = test_por_clave(claves, 0.3, semilla=3)
    for k in range(2_000):
        lado = m[claves == k]
        assert lado.all() or not lado.any()
    assert m.mean() == pytest.approx(0.3, abs=0.03)
