import re

from publi.lexico import RE_DECL, RE_MARKETING, RE_SHOP, decl


def test_hashtags_de_declaracion_con_limites():
    assert RE_DECL.search("verano #publi #fyp")
    assert RE_DECL.search("#PUBLICIDAD")
    assert RE_DECL.search("look #ad#fyp")
    assert not RE_DECL.search("verano#publi")          # pegado a la palabra anterior no es hashtag
    assert not RE_DECL.search("#publicar mañana")
    assert not RE_DECL.search("odio la publicidad")    # la palabra suelta ya no define P
    assert RE_DECL.search("colab pagada con la marca")
    assert RE_DECL.search("en colaboración con @marca")


def test_re2_no_lleva_lookahead():
    assert "(?=" not in decl("re2")
    assert "(?=" in decl("py")


def test_exclusiones():
    assert RE_SHOP.search("mis favoritos de #TikTokShop")
    assert RE_SHOP.search("#dealsforyoudays")
    assert RE_MARKETING.search("agencia de publicidad en Sevilla")
    assert RE_MARKETING.search("imprenta y rótulos")
    assert not RE_MARKETING.search("mi rutina de skincare con @marca")
