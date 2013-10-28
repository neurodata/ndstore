"""SQLObject-based version of gettext"""

import codecs
from gettext import translation

from sqlobject import SQLObjectNotFound

from turbogears import config
from turbogears.i18n.sogettext.model import TG_Message, TG_Domain
from turbogears.i18n.utils import get_locale


_catalogs = {}


def so_gettext(key, locale=None, domain=None):
    """SQLObject-based version of gettext.

    Messages are stored in database instead.

    """

    locale = get_locale(locale)

    messages = get_so_catalog(domain).get(locale)
    if not messages:
        messages = get_so_catalog(domain).get(locale[:2], {})

    return unicode(messages.get(key, key))


def get_so_catalog(domain):
    """Get catalog from database.

    Retrieves all translations for locale and domain from database
    and stores in thread data.

    """

    if domain is None:
        domain = config.get('i18n.domain', 'messages')

    catalog = _catalogs.get(domain)
    if not catalog:

        catalog = {}

        try:
            domain = TG_Domain.byName(domain)
        except SQLObjectNotFound:
            return catalog

        results = TG_Message.selectBy(domain=domain)
        for message in results:
            locale = message.locale
            messages = catalog.get(locale, {})
            messages[message.name] = message.text
            catalog[locale] = messages

        _catalogs[domain.name] = catalog

    return catalog


def create_so_catalog_tables():
    """Create the tables if needed."""
    TG_Message.dropTable(ifExists=True)
    TG_Domain.dropTable(ifExists=True)

    TG_Domain.createTable(ifNotExists=True)
    TG_Message.createTable(ifNotExists=True)


def create_so_catalog(locales, domain):
    """Create catalog from database.

    Creates a message catalog based on list of locales from existing
    GNU message catalog.

    """
    # first try to create the table if we need to...
    create_so_catalog_tables()

    localedir = config.get('i18n.locale_dir', 'locales')

    try:
        domain = TG_Domain.byName(domain)
        return
    except SQLObjectNotFound:
        domain = TG_Domain(name=domain)

    for locale in locales:
        translations = translation(domain=domain.name, localedir=localedir,
                languages=[locale])
        catalog = translations._catalog

        for k, v in catalog.items():
            TG_Message(domain=domain, locale=locale, name=k, text=v)


def dump_so_catalogs(locales):
    """Take all domains and messages and creates message catalogs."""
    localedir = config.get('i18n.locale_dir', 'locales')

    for locale in locales:

        messages_dir = os.path.join(localedir, locale, 'LC_MESSAGES')

        for domain in TG_Domain.select():
            pofile = os.path.join(messages_dir, '%s.po' % domain.name)
            f = codecs.open(pofile, 'w', 'UTF-8')
            f.write("""
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: CREATION_DATE\\n"
"PO-Revision-Date: REVISION_DATE\\n"
"Last-Translator: TRANSLATOR <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: turbogears\\n"

            """)

            for message in TG_Message.selectBy(domain=domain, locale=locale):

                if not message.name:
                    continue # descriptive text

                f.write(u"""
msgid "%s"
msgstr "%s"
                """%(message.name, message.text))

            f.close()
