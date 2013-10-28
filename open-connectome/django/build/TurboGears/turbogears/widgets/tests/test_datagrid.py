
from turbogears import testutil
from turbogears.widgets.datagrid import DataGrid


def setup_module():
    testutil.start_server()


class Foo:

    def __init__(self, name, subtype, text):
        self.name = name
        self.subtype = subtype
        self.text = text

    @property
    def excerpt(self):
        return self.text + '...'


class User:

    def __init__(self, ID, name, emailAddress):
        self.userId = ID
        self.name = name
        self.emailAddress = emailAddress

    @property
    def displayName(self):
        return self.name.capitalize()


class TestDataGrid:

    def test_column_declaration(self):
        """Test standard column declaration styles."""
        grid = DataGrid(name='grid', fields=[
            DataGrid.Column('name', options=dict(foobar=123)),
            ('Subtype', 'subtype'),
            DataGrid.Column('text', 'excerpt', 'TEXT')])
        d = dict(value='value')
        grid.update_params(d)
        get_field = d['get_field']
        assert d['columns'][0].get_option('foobar') == 123
        assert grid.get_column('name').options['foobar'] == 123
        row = Foo('spa1', 'fact', 'thetext')
        assert 'spa1' == get_field(row, 'name')
        assert 'fact' == get_field(row, 'column-1')
        assert 'thetext...' == get_field(row, 'text')

    def test_alternative_column_declaration(self):
        """Test alternative column declaration styles."""
        g = lambda: None
        grid = DataGrid(fields=[
            (g), ('t', g), ('t', g, dict(p=0)),
            DataGrid.Column('n', g, 't', dict(p=0))])
        for i in range(4):
            name = i == 3 and 'n' or 'column-%d' % i
            c = grid[name]
            assert c.name == name
            title = i == 0 and name.capitalize() or 't'
            assert c.title == title
            assert c.getter == g
            options = i > 1 and dict(p=0) or dict()
            assert c.options == options

    def test_empty_column_title(self):
        """Test automatic and empty column titles."""
        grid = DataGrid(fields=[
            (None, 'a'), ('', 'a'), ('title', 'a')])
        assert grid['column-0'].title == 'Column-0'
        assert grid['column-1'].title == ''
        assert grid['column-2'].title == 'title'

    def test_column_alignment(self):
        """Test controlling column alignment."""
        grid = DataGrid(fields=[
            ('left col', lambda d: d[0]),
            ('center col', lambda d: d[1], dict(align='center')),
            ('right col', lambda d: d[2], dict(align='right'))])
        output = grid.render([('left data', 'center data', 'right data')])
        assert '<td>left data</td><td align="center">center data</td>' \
            '<td align="right">right data</td>' in output

    def test_template_overridal(self):
        """Test overriding the template."""
        grid = DataGrid(fields=[
                ('Name', 'name'),
                ('Subtype', 'subtype'),
                ('TEXT', Foo.excerpt.fget)],
            template = "turbogears.fastdata.templates.datagrid")
        d = dict(value='value')
        grid.update_params(d)

    def test_wiki_samples(self):
        """Test that sample code on DataGridWidget wiki page actually works."""
        grid = DataGrid(fields=[
            ('ID', 'userId'),
            ('Name', 'displayName'),
            ('E-mail', 'emailAddress')])
        users = [User(1, 'john', 'john@foo.net'),
            User(2, 'fred', 'fred@foo.net')]
        output = grid.render(users)
        assert '<td>2</td><td>Fred</td><td>fred@foo.net</td>' in output
        grid = DataGrid(fields=[
            ('Name', lambda row: row[1]),
            ('Country', lambda row: row[2]),
            ('Age', lambda row: row[0])])
        data = [(33, "Anton Bykov", "Bulgaria"),
            (23, "Joe Doe", "Great Britain"),
            (44, "Pablo Martelli", "Brazil")]
        output = grid.render(data)
        assert '<td>Joe Doe</td><td>Great Britain</td><td>23</td>' in output

    def test_custom_attrwrapper(self):
        """Test custom attribute wrapper functions for DataGrid."""
        class TestDataGrid(DataGrid):
            class attrwrapper(object):
                def __init__(self, name):
                    self.name = 'custom%d' % name
        grid = TestDataGrid(fields=[
            ('Field 1', 1)
        ])
        assert grid.columns[0].getter.name == 'custom1'

    def test_attrwrapper_with_list(self):
        """Test accessing list elements with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 0),
            ('Field 2', 1),
            ('Field 3', 2)
        ])
        row = [4, 2]
        assert grid.columns[0].getter(row) == 4
        assert grid.columns[1].getter(row) == 2
        try:
            grid.columns[2].getter(row)
        except IndexError:
            pass
        else:
            assert False, "accessing the 3rd item should raise IndexError"

    def test_attrwrapper_with_tuple(self):
        """Test accessing tuple elements with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 0),
            ('Field 2', 1),
            ('Field 3', 2)
        ])
        row = (4, 2)
        assert grid.columns[0].getter(row) == 4
        assert grid.columns[1].getter(row) == 2
        try:
            grid.columns[2].getter(row)
        except IndexError:
            pass
        else:
            assert False, "accessing the 3rd item should raise IndexError"

    def test_attrwrapper_with_dict(self):
        """Test accessing dictionary values with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 'key1'),
            ('Field 2', 'key2'),
            ('Field 3', 'key3')
        ])
        row = dict(key1=4, key2=2)
        assert grid.columns[0].getter(row) == 4
        assert grid.columns[1].getter(row) == 2
        try:
            grid.columns[2].getter(row)
        except KeyError:
            pass
        else:
            assert False, "accessing key3 should raise KeyError"

    def test_attrwrapper_with_dict_and_dotted_key(self):
        """Test accessing dotted dictionary values with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 'key1.sub'),
            ('Field 2', 'key2.sub'),
            ('Field 3', 'key3.sub')
        ])
        row = {'key1.sub': 4, 'key2.sub': 2, 'key3': {'sub': 1}}
        assert grid.columns[0].getter(row) == 4
        assert grid.columns[1].getter(row) == 2
        try:
            grid.columns[2].getter(row)
        except KeyError:
            pass
        else:
            assert False, "accessing key3.sub should raise KeyError"

    def test_attrwrapper_with_obj(self):
        """Test accessing object attributes with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 'col1'),
            ('Field 2', 'col2'),
            ('Field 3', 'col3'),
        ])
        class row:
            col1 = 4
            col2 = 2
        assert grid.columns[0].getter(row) == 4
        assert grid.columns[1].getter(row) == 2
        try:
            grid.columns[2].getter(row)
        except AttributeError:
            pass
        else:
            assert False, "accessing col3 should raise AttributeError"

    def test_attrwrapper_with_nested_obj(self):
        """Test accessing nested object attributes using dots with DataGrid."""
        grid = DataGrid(fields=[
            ('Field 1', 'sub1.col'),
            ('Field 2', 'sub1.sub2.col'),
            ('Field 3', 'sub1.empty'),
            ('Field 4', 'sub1.empty.col'),
            ('Field 5', 'sub1.foobar'),
        ])
        class row:
            class sub1:
                class sub2:
                    col = 4
                col = 2
                empty = None
        assert grid.columns[0].getter(row) == 2
        assert grid.columns[1].getter(row) == 4
        assert grid.columns[2].getter(row) is None
        assert grid.columns[3].getter(row) is None
        try:
            grid.columns[4].getter(row)
        except AttributeError:
            pass
        else:
            assert False, "accessing foobar should raise AttributeError"

