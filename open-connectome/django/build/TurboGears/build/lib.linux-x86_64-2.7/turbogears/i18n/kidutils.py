"""Functions supporting translation of strings in Kid templates
"""

from kid.parser import START, TEXT, END
from turbogears import config
# use plain_gettext because Kid's template strings are always evaluated
# immediately
from turbogears.i18n.tg_gettext import plain_gettext as gettext


def translate(item, attr=None):
    """Translates the text of element plus the text of all child elements.

    If 'attr' is present this is used to provide the locale name; if not then the
    value provided by 'get_locale' is used. For example::

        <div lang="">
            this is a test
            <a href="de">testing</a>
        </div>

    The string 'this is a test' is rendered by the locale provided by
    'get_locale', the string 'testing' by the German locale.

    Possible use in Kid template::

        <?python
        from turbogears.i18n import translate
        ?>
        <translate xmlns:py="http://purl.org/kid/ns#"
            py:match="'lang' in item.attrib"
            py:replace="translate(item)" />
        <h1 lang="">Welcome!</h1>

    @param item: element to be translated
    @type item: ElementTree element

    @param attr: attribute name used to store locale, if any
    @type attr: str

    """
    if attr is None:
        attr = config.get('i18n.templateLocaleAttribute', 'lang')

    translate_all(item, item.get(attr), attr)
    return item

def __translate_text(text, lang):
    prefix = ''
    postfix = ''
    if len(text) > 0 and text[0].isspace():
        prefix = text[0]

    if len(text) > 1 and text[-1].isspace():
        postfix = text[-1]

    return prefix + gettext(text.strip(), lang) + postfix

def translate_all(tree, lang, attr, inroot=True):
    """Recursive function to translate all text in child elements.

    @param tree: parent ElementTree element
    @param lang: language setting
    @param attr: attribute name used to store locale

    """
    if tree.text:
        tree.text = __translate_text(tree.text, lang)

    if tree.tail and not inroot:
        # Don't translate tail of root. It is beyond the scope of the lang attr
        tree.tail = __translate_text(tree.tail, lang)

    for element in tree:
        # check overriding lang attribute
        if element.get(attr):lang = element.get(attr)
        translate_all(element, lang, attr, False)

def i18n_filter(stream, template, locale=None):
    """Kid template filter translating all elements matching lang attribute.

    The name of of the attribute is set in the configuration as
    'i18n.templateLocaleAttribute' and defaults to 'lang'.

    """
    lang_attr = config.get('i18n.templateLocaleAttribute', 'lang')
    locales = [locale]

    for ev, item in stream:

        if ev == START:
            l = item.get(lang_attr)
            if l:
                locale = l
                locales.append(l)

        elif ev == TEXT:
            prefix = ''
            postfix = ''
            if len(item) > 0 and item[0] == ' ':
                prefix = ' '

            if len(item) > 1 and item[-1] == ' ':
                postfix = ' '

            text = item.strip()
            if text:
                item = gettext(text, locale)
                item = prefix + item + postfix

        elif ev == END:
            if item.get(lang_attr):
                locales.pop()
                locale = locales[-1]

        yield (ev, item)
