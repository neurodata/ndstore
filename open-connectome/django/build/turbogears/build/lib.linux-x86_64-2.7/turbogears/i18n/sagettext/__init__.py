"""SQLAlchemy-based version of gettext"""

import codecs
from gettext import translation

from turbogears import config
from turbogears.database import metadata, session
from turbogears.i18n.sagettext.model import TG_Message, TG_Domain
from turbogears.i18n.utils import get_locale


_catalogs = {}


def sa_gettext(key, locale=None, domain=None):
    """SQLAlchemy-based version of gettext.

    Messages are stored in database instead.

    """

    locale = get_locale(locale)

    messages = get_sa_catalog(domain).get(locale)
    if not messages:
        messages = get_sa_catalog(domain).get(locale[:2], {})

    return unicode(messages.get(key, key))


def get_sa_catalog(domain):
    """Get catalog from database.

    Retrieves all translations for locale and domain from database
    and stores in thread data.

    """

    if domain is None:
        domain = config.get('i18n.domain', 'messages')

    catalog = _catalogs.get(domain)
    if not catalog:

        catalog = {}

        query = session.query(TG_Domain)
        domain = query.filter(TG_Domain.name == domain).first()

        if not domain:
            return catalog

        query = session.query(TG_Message)
        query = query.filter(TG_Message.domain == domain)

        for message in query:
            locale = message.locale
            messages = catalog.get(locale, {})
            messages[message.name] = message.text
            catalog[locale] = messages

        _catalogs[domain.name] = catalog

    return catalog


def create_sa_catalog(locales, domain):
    """Create message catalog from database.

    Creates a message catalog based on list of locales from existing
    GNU message catalog.

    """

    tg_message_table.drop(checkfirst=True)
    tg_domain_table.drop(checkfirst=True)

    tg_domain_table.create(checkfirst=True)
    tg_message_table.create(checkfirst=True)

    localedir = config.get('i18n.locale_dir', 'locales')

    query = session.query(TG_Domain)
    domain = query.filter(TG_Domain.name == domain).first()
    if domain:
        return
    else:
        domain = TG_Domain()
        domain.name = domain
        session.add(domain)
        session.flush()

    for locale in locales:
        translations = translation(
                domain=domain.name,
                localedir=localedir,
                languages=[locale])
        catalog = translations._catalog

        for k, v in catalog.items():
            mess = TG_Message()
            mess.domain = domain
            mess.locale = locale
            mess.name = k
            mess.text = v
            session.add(mess)

        session.flush()


def dump_sa_catalogs(locales):
    """Take all domains and messages and creates message catalogs."""
    localedir = config.get('i18n.locale_dir', 'locales')

    for locale in locales:

        messages_dir = os.path.join(localedir, locale, 'LC_MESSAGES')

        for domain in session.query(TG_Domain):
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

            query = session.query(TG_Message)
            query = query.filter(TG_Message.domain==domain)
            query = query.filter(TG_Message.locale==locale)

            for message in query:
                if not message.name:
                    continue # descriptive text

                f.write(u"""
msgid "%s"
msgstr "%s"
                """%(message.name, message.text))

            f.close()
