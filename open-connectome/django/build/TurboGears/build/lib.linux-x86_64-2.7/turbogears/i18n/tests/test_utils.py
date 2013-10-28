# -*- coding: utf-8 -*-

from turbogears.i18n.utils import *


def test_get_accept_languages():
    assert get_accept_languages("da, en-gb;q=0.8, en;q=0.7") == [
        "da", "en_GB", "en"]
    assert get_accept_languages("da;q=0.6, en-gb;q=1.0, en;q=0.7") == [
        "en_GB", "en", "da"]
