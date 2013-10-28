
import kid
from turbogears.i18n.kidutils import *
from turbogears.i18n.tests import setup_module


def test_match_template():

    template = """
    <?python
    from turbogears.i18n.kidutils import translate
    ?>
    <html xmlns:py="http://purl.org/kid/ns#">
        <translate py:match="'lang' in item.attrib" py:replace="translate(item, 'lang')"/>
        <body lang="">
            Welcome
            <p>Welcome</p>
            <p lang="en">Welcome</p>
            <p lang="fi">Welcome</p>
        </body>
    </html>
    """

    t = kid.Template(source = template)
    output = t.serialize()
    assert '<p lang="en">Welcome</p>' in output
    assert '<p lang="fi">Tervetuloa</p>' in output


def test_i18n_filter():

    template = """
    <html xmlns:py="http://purl.org/kid/ns#">
        <body>
            Welcome, <em>guest</em>!
            <p>Welcome</p>
            <p lang="en">Welcome</p>
            <p lang="fi">Welcome<a href="" lang="de">Welcome</a></p>
        </body>
    </html>"""

    t = kid.Template(source = template)
    t._filters+=[i18n_filter]
    output = t.serialize()
    print output
