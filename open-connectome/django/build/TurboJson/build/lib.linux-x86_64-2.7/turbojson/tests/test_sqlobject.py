from turbojson.jsonify import jsonify, encode, GenericJSON

try:
    try:
        import sqlite3
    except ImportError: # Python < 2.5
        import pysqlite2
    from sqlobject import sqlhub, connectionForURI, SQLObject, StringCol
    from sqlobject.inheritance import InheritableSQLObject

    sqlhub.processConnection = connectionForURI('sqlite:/:memory:')

    class Person(SQLObject):
        fname = StringCol()
        mi = StringCol(length=1, default=None)
        lname = StringCol()
    Person.createTable()

    class ExplicitPerson(SQLObject):
        fname = StringCol()
        def __json__(self):
            return {'customized': True}
    ExplicitPerson.createTable()

    class A(InheritableSQLObject):
        foo = StringCol()
    A.createTable()

    class B(A):
        bar = StringCol()
    B.createTable()

    class C(A):
        baz = StringCol()
        def __json__(self):
            return {'customized': True}
    C.createTable()

except ImportError:
    from warnings import warn
    warn('SQLObject or PySqlite not installed - cannot run these tests.')

else:

    def test_soobj():
        p = Person(fname="Peter", mi="P", lname="Pasulke")
        pj = jsonify(p)
        assert pj == {'fname': "Peter", 'mi': "P", 'lname': "Pasulke", 'id': 1}
        b = B(foo="foo", bar="bar")
        bj = jsonify(b)
        assert bj == {'foo': "foo", 'bar': "bar", 'id': b.id, 'childName': None}

    def test_customized_soobj():
        ep = ExplicitPerson(fname="Peter")
        epj = jsonify(ep)
        assert epj == {'customized': True}
        c = C(foo="foo", baz="baz")
        cj = jsonify(c)
        assert cj == {'customized': True}

    def test_so_select_result():
        p = Person(fname="Willy", mi="P", lname="Millowitsch")
        sr = Person.select(Person.q.fname == "Willy")
        srj = jsonify(sr)
        assert srj == [p]

    def test_descent_bases():
        b = B(foo="foo", bar="bar")
        bj = jsonify(b)
        assert 'foo' in bj and 'bar' in bj
        no_descent_encoder = GenericJSON(descent_bases=False)
        bj = no_descent_encoder.encode(b)
        assert 'foo' not in bj and 'bar' in bj

