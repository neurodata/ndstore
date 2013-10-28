
from datetime import datetime

from turbogears.i18n.format import *

dt = datetime(2005, 2, 5) # Saturday, 5rd Feb 2005


def test_get_countries():
    print get_countries()
    print get_countries("eo")
    print get_countries("en_US")


def test_get_languages():
    print get_languages()
    print get_languages("eo")
    print get_countries("en_US")


def test_get_month_names():
    print get_month_names()
    print get_abbr_month_names()

    print get_month_names("eo")
    print get_abbr_month_names("eo")

    print get_month_names("en_US")
    print get_abbr_month_names("en_US")


def test_get_weekday_names():
    print get_weekday_names()
    print get_abbr_weekday_names()

    print get_weekday_names("eo")
    print get_abbr_weekday_names("eo")

    print get_weekday_names("en_US")
    print get_abbr_weekday_names("en_US")


def test_format_numbers():
    assert format_decimal(4.9, 0, "en") == "5"
    assert format_decimal(4.9, 1, "en") == "4.9"
    assert format_decimal(5.0, 1, "en") == "5.0"
    assert format_decimal(5.1, 1, "de") == "5,1"

    assert format_number(50, "en_US") == "50"
    assert format_number(50, "de") == "50"

    assert format_number(500, "en_US") == "500"
    assert format_number(500, "de") == "500"

    assert format_number(5000, "en_US") == "5,000"
    assert format_number(5000, "de") == "5.000"

    assert format_number(50000, "en_US") == "50,000"
    assert format_number(50000, "de") == "50.000"

    assert format_number(500000, "en_US") == "500,000"
    assert format_number(500000, "de") == "500.000"

    assert format_number(5000000, "en_US") == "5,000,000"
    assert format_number(5000000, "de") == "5.000.000"

    assert format_decimal(5000000.78781, 5, "en_US") == "5,000,000.78781"
    assert format_decimal(5000000.78781, 5, "de") == "5.000.000,78781"

    assert format_currency(5000000.78781, "en_US") == "5,000,000.79"
    assert format_currency(5000000.78781, "de") == "5.000.000,79"


def test_format_date():
    assert format_date(dt, "long", "eo") == u"2005-februaro-05"
    assert format_date(dt, "medium", "eo") == u"2005-feb-05"
    assert format_date(dt, "short", "eo") == u"05-02-05"
    assert format_date(dt, "full", "eo") == u"sabato, 05-a de februaro 2005"

    assert format_date(dt, "long", "de") == u"05. Februar 2005"
    assert format_date(dt, "medium", "de") == u"05.02.2005"
    assert format_date(dt, "short", "de") == u"05.02.05"
    assert format_date(dt, "full", "de") == u"Samstag, 05. Februar 2005"

    assert format_date(dt, "short", "en",
            date_format='day %d of %%(monthname)s') == u"day 05 of February"


def test_parse_numbers():
    assert parse_number("5,000,000", "en_US") == 5000000
    assert parse_number("5.000.000", "de") == 5000000
    assert parse_decimal("5,000,000.78781", "en_US") == 5000000.78781
    assert parse_decimal("5.000.000,78781", "de") == 5000000.78781
    assert parse_decimal("5,000,000.78781", "xx") == 5000000.78781

    try:
        parse_number("5.000.000", "en_US")
        parse_number("5.000.000,78781", "en_US")
        assert False
    except ValueError:
        assert True


def test_diff_locale_format_date():
    assert format_date(dt, "short", "en_US") == "02/05/05"
    assert format_date(dt, "short", "en_GB") == "05/02/2005"


def test_invalid_locale_format():
    assert get_abbr_weekday_names("fubar")==[]

