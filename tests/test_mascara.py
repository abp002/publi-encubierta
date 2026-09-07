from publi.mascara import enmascarar


def test_declarado_y_no_declarado_dan_el_mismo_texto():
    con = "Mi rutina de mañana con @marca #publi código ALE10"
    sin = "Mi rutina de mañana con @marca código ALE10"
    assert enmascarar(con) == enmascarar(sin)


def test_quita_todas_las_formas_de_declaracion():
    for frase in ["#publicidad", "#ad", "#Ad", "publicidad", "patrocinado", "Patrocinada",
                  "colaboración pagada", "colaboracion pagada", "en colaboración con", "producto regalado"]:
        assert enmascarar(f"hola {frase} mundo") == "hola mundo", frase


def test_no_toca_palabras_parecidas_ni_exclusiones():
    for frase in ["#publicar", "#pr", "#colab", "regalo de cumpleaños", "#paidpartnership", "publicitario"]:
        assert enmascarar(f"hola {frase} mundo") == f"hola {frase} mundo", frase


def test_hashtags_pegados():
    assert enmascarar("verano#publi#fyp") == "verano#publi#fyp"  # sin espacio delante no es hashtag
    assert enmascarar("verano #publi#fyp") == "verano #fyp"


def test_idempotente_y_vacios():
    assert enmascarar("") == ""
    assert enmascarar(None) == ""
    t = enmascarar("  #publi   hola  ")
    assert enmascarar(t) == t == "hola"
