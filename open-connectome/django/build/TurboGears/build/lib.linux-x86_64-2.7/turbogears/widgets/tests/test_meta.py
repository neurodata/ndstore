
from turbogears import  widgets


def test_determine_template_engine():
    """Test that the engine name can be properly determined."""
    test_templates = (
        ("<p>${doh}</p>", None),
        ('<html>xmlns:py="http://purl.org/kid/ns#"</html>', None),
        ('<html xmlfoo:py="http://purl.org/kid/ns#">bar</html>', None),
        ('<html xmlns:py="http://purp.org/kid/ns#"/>', None),
        ('<html xmlns:py="http://purl.org/kid/ns#"/>', 'kid'),
        ('<foo xmlns:py="http://purl.org/kid/ns#" bar="test"/>', 'kid'),
        ("<bar xmlns:py='http://purl.org/kid/ns#' foo='test'/>", 'kid'),
        ("<html xmlns='test' lang='en'"
            " xmlns:py='http://purl.org/kid/ns#'/>", 'kid'),
        ("""
        <?xml version="1.0" encoding="UTF-8" ?>
        <form xmlns:py="http://purl.org/kid/ns#" name="test">
        bla
        </form>
        """, 'kid'),
        ("""
            <span xmlns:py="http://purl.org/kid/ns#" class="${field_class}">
            <input type="text" /></span>
        """, 'kid'),
        ("""<?python
                x = 0
            ?>
            <html xmlns:py="http://purl.org/kid/ns#">
            <?python
                x = 1
            ?>
            </html>""", 'kid'),
        ("""<?xml version='1.0' encoding='utf-8'?>
            <?python
            import time
            title = "A Kid Template"
            ?>
            <html xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://purl.org/kid/ns#">
            <head/></body>
            </html>""", 'kid'),
        ("""
        <html xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://genshi.edgewall.org/"
                lang="en">
          <h1>Hello, World</h1>
        </html>
        """, 'genshi'),
        ("""<?python
          title = "A Genshi Template"
        ?>
        <html xmlns:py="http://genshi.edgewall.org/">
          <head>
            <title py:content="title">This is replaced.</title>
          </head>
          <body>
            <p>My favorite fruits.</p>
          </body>
        </html>""", 'genshi'),
        ("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
                "http://www.w3.org/TR/html4/loose.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://genshi.edgewall.org/"
                xmlns:xi="http://www.w3.org/2001/XInclude"
                lang="en">
                <xi:include href="site.html" />
            <p xmlns:py="foo">doh</p>
            </html>
        """, 'genshi'))
    determine_template = widgets.meta.determine_template_engine
    for template, expected_engine in test_templates:
        derived_engine = determine_template(template)
        assert derived_engine == expected_engine, (
            "Derived engine from the following template is not as expected\n"
            "(it should be %r, but it is %r):\n%s"
            % (expected_engine, derived_engine, template))
