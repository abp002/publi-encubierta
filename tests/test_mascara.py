from publi.mascara import enmascarar


def test_declarado_y_no_declarado_dan_el_mismo_texto():
    con = "Mi rutina de mañana con @marca #publi código ALE10"
    sin = "Mi rutina de mañana con @marca código ALE10"
    assert enmascarar(con) == enmascarar(sin)


def test_quita_todas_las_formas_de_declaracion_y_sus_raices():
    for frase in ["#publicidad", "#ad", "#Ad", "publicidad", "patrocinado", "Patrocinada", "publi",
                  "colaboración pagada", "colab pagada", "en colaboración con", "producto regalado",
                  "#fyp#publicidad", "publicitario", "#publicar", "anuncio", "PUBLI:", "sponsored"]:
        assert "publi" not in enmascarar(f"hola {frase} mundo").lower(), frase
        assert enmascarar(f"hola {frase} mundo").split()[0] == "hola", frase


def test_fuga_del_baseline_cerrada():
    """Los n-gramas que el primer baseline aprendió no deben sobrevivir al enmascarado."""
    for frase in ["Publicidad engañosa", "colab pagada", "aviso de publicidad", "#publi #fyp", "anuncios"]:
        t = enmascarar(frase).lower()
        for raiz in ["publi", "ubli", "anunc", "pagad"]:
            assert raiz not in t, (frase, t)


def test_residuos_de_frase_cerrados():
    assert enmascarar("Vídeo en colaboración con @marca") == "Vídeo @marca"
    assert enmascarar("patrocinado por @marca") == "@marca"


def test_no_toca_lo_que_no_es_declaracion():
    for frase in ["regalo de cumpleaños", "#paideia", "adiós", "#addicted", "prado"]:
        assert enmascarar(f"hola {frase} mundo") == f"hola {frase} mundo", frase


def test_idempotente_y_vacios():
    assert enmascarar("") == ""
    assert enmascarar(None) == ""
    t = enmascarar("  #publi   hola  ")
    assert enmascarar(t) == t == "hola"
