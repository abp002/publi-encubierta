import numpy as np
import pytest

from publi.pu import corregir, estimar_c, peso_positivo_no_etiquetado, prevalencia_en_no_etiquetados


def test_c_es_la_media_de_g_en_positivos_heldout():
    assert estimar_c(np.array([0.2, 0.4, 0.6])) == pytest.approx(0.4)


def test_c_invalido():
    with pytest.raises(ValueError):
        estimar_c(np.array([]))
    with pytest.raises(ValueError):
        estimar_c(np.array([0.0, 0.0]))


def test_con_c_igual_a_uno_no_cambia_nada():
    g = np.array([0.1, 0.5, 0.9])
    assert corregir(g, 1.0) == pytest.approx(g)
    assert peso_positivo_no_etiquetado(g, 1.0) == pytest.approx(np.zeros(3))


def test_corregir_escala_y_acota():
    assert corregir(np.array([0.2, 0.6]), 0.5) == pytest.approx([0.4, 1.0])


def test_estima_c_cuando_las_clases_son_separables():
    """Elkan-Noto: e1 = media de g en positivos etiquetados es exacto si P(y=1|x)=1 para ellos.
    Escenario separable: g = c·P(y=1|x) con P(y=1|x) ∈ {0, 1}."""
    rng = np.random.default_rng(0)
    n, c = 100_000, 0.4
    y = rng.random(n) < 0.30
    s = y & (rng.random(n) < c)
    g = np.where(y, c, 0.0)
    assert estimar_c(g[s]) == pytest.approx(c)
    ocultos_reales = (y & ~s).sum() / (~s).sum()
    assert prevalencia_en_no_etiquetados(g[~s], estimar_c(g[s])) == pytest.approx(ocultos_reales, abs=1e-6)


def test_recupera_la_prevalencia_oculta_con_posterior_calibrada():
    """Escenario no separable pero calibrado: p = P(y=1|x) verdadera, y ~ Bernoulli(p),
    etiquetado SCAR con c. Con g = c·p y la c verdadera, la fórmula
    P(y=1|x,s=0) = (1-c)/c · g/(1-g) recupera la fracción de positivos ocultos."""
    rng = np.random.default_rng(1)
    n, c = 300_000, 0.4
    p = rng.beta(2, 5, n)                 # posterior verdadera, media ≈ 0,29
    y = rng.random(n) < p
    s = y & (rng.random(n) < c)
    g = c * p
    ocultos_reales = (y & ~s).sum() / (~s).sum()
    assert prevalencia_en_no_etiquetados(g[~s], c) == pytest.approx(ocultos_reales, abs=0.005)
    # y en este escenario e1 subestima c (P(y=1|x)<1 en los etiquetados): hay que saberlo
    assert estimar_c(g[s]) < c


def test_ajustar_prior_identidad_y_direccion():
    from publi.pu import ajustar_prior
    g = np.array([0.1, 0.5, 0.9])
    assert ajustar_prior(g, 0.02, 0.02) == pytest.approx(g)
    menos = ajustar_prior(g, 0.02, 0.001)
    assert (menos < g).all()
    # con odds: g=0.5 (odds 1) y r = (0.001/0.999)/(0.02/0.98) → odds r
    r = (0.001 / 0.999) / (0.02 / 0.98)
    assert menos[1] == pytest.approx(r / (1 + r))
