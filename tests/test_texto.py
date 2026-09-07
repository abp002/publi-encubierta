from publi.texto import preparar


def test_menciones_y_urls_a_token():
    assert preparar("Con @LaMarca.es mira https://x.co/abc #publi") == "con @usuario mira url"


def test_declarado_y_no_declarado_identicos_tras_preparar():
    assert preparar("Rutina con @m #publicidad código ALE10") == preparar("rutina con @otra código ALE10")


def test_conserva_hashtags_normales_y_minusculas():
    assert preparar("#SkinCare Rutina") == "#skincare rutina"
