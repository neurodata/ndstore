"""Generic widget to present and manipulate data in a grid (tabular) form."""

__all__ = ['DataGrid', 'PaginateDataGrid']

from turbogears.widgets import Widget, CSSLink, static
from turbogears.widgets.base import CoreWD

NoDefault = object()


class DataGrid(Widget):
    """Generic widget to present and manipulate data in a grid (tabular) form.

    The columns to build the grid from are specified with fields ctor argument
    which is a list. Currently an element can be either a two-element tuple or
    instance of DataGrid.Column class. If tuple is used it a Column is then
    build out of it, first element is assumed to be a title and second element -
    field accessor.

    You can specify columns' data statically, via fields ctor parameter, or
    dynamically, by via 'fields' key.

    """

    css = [CSSLink(static, "grid.css")]
    template = "turbogears.widgets.templates.datagrid"
    fields = None

    class Column:
        """Simple struct that describes single DataGrid column.

        Column has:
          - a name, which allows to uniquely identify column in a DataGrid
          - getter, which is used to extract field's value
          - title, which is displayed in the table's header
          - options, which is a way to carry arbitrary user-defined data
          - attrwrapper, which is a function returning an object's attribute

        """

        def __init__(self, name,
                getter=None, title=None, options=None, attrwrapper=None):
            if name is None:
                raise ValueError('column name is required')
            if attrwrapper is None:
                attrwrapper = DataGrid.attrwrapper
            if getter is None:
                self.getter = attrwrapper(name)
            else:
                if callable(getter):
                    self.getter = getter
                else: # assume it's an attribute name
                    self.getter = attrwrapper(getter)
            self.name = name
            self.title = title is None and name.capitalize() or title
            self.options = options or {}

        def get_option(self, name, default=NoDefault):
            if name in self.options:
                return self.options[name]
            if default is NoDefault: # no such key and no default is given
                raise KeyError(name)
            return default

        def get_field(self, row):
            return self.getter(row)

        def __str__(self):
            return "<DataGrid.Column %s>" % self.name

    class attrwrapper:
        """Helper class that returns an object's attribute when called.

        This allows to access 'dynamic' attributes (properties) as well as
        simple static ones, and also allows nested access.

        """

        def __init__(self, name):
            if not isinstance(name, (int, str)):
                raise ValueError('attribute name must be'
                    ' an integer index or a string attribute')
            self.name = name

        def __call__(self, obj):
            if isinstance(obj, (dict, list, tuple)):
                return obj[self.name]
            for name in self.name.split('.'):
                obj = getattr(obj, name)
                if obj is None:
                    break
            return obj

    def __init__(self, fields=None, **kw):
        super(DataGrid, self).__init__(**kw)
        if fields:
            self.fields = fields
        if self.fields is None:
            self.fields = []
        self.columns = self._parse(self.fields)

    def get_column(self, name):
        """Return DataGrid.Column with specified name.

        Raises KeyError if no such column exists.

        """
        for col in self.columns:
            if col.name == name:
                return col
        raise KeyError(name)

    def __getitem__(self, name):
        """Shortcut to get_column."""
        return self.get_column(name)

    @staticmethod
    def get_field_getter(columns):
        """Return a function to access the fields of table by row, col."""
        idx = {} # index columns by name
        for col in columns:
            idx[col.name] = col
        def _get_field(row, col):
            return idx[col].get_field(row)
        return _get_field

    def update_params(self, d):
        super(DataGrid, self).update_params(d)
        if d.get('fields'):
            fields = d.pop('fields')
            columns = self._parse(fields)
        else:
            columns = self.columns[:]
        d['columns'] = columns
        d['get_field'] = self.get_field_getter(columns)

    def _parse(self, fields):
        """Parse field specifications into a list of Columns.

        A specification can be a DataGrid.Column, an accessor
        (attribute name or function), a tuple (title, accessor)
        or a tuple (title, accessor, options).

        """
        columns = []
        names = set() # keep track of names to ensure there are no dups
        for n, col in enumerate(fields):
            if not isinstance(col, self.Column):
                if isinstance(col, (str, int)) or callable(col):
                    name_or_f = col
                    title = options = None
                else:
                    title, name_or_f = col[:2]
                    try:
                        options = col[2]
                    except IndexError:
                        options = None
                name = 'column-' + str(n)
                col = self.Column(name,
                    name_or_f, title, options, self.attrwrapper)
            if col.name in names:
                raise ValueError('Duplicate column name: %s' % name)
            columns.append(col)
            names.add(col.name)
        return columns


class DataGridDesc(CoreWD):

    name = "DataGrid"

    for_widget = DataGrid(fields=[('Name', lambda row: row[1]),
                                  ('Country', lambda row: row[2]),
                                  ('Age', lambda row: row[0])],
                          default=[(33, "Anton Bykov", "Bulgaria"),
                                   (23, "Joe Doe", "Great Britain"),
                                   (44, "Pablo Martelli", "Brazil")])


class PaginateDataGrid(DataGrid):
    """A data grid widget that supports the paginate decorator."""

    template = "turbogears.widgets.templates.paginate_datagrid"


class PaginateDataGridDesc(CoreWD):

    name = "PaginateDataGrid"

    for_widget = DataGridDesc.for_widget

    class Paginate(object):
        # paginate var mock-up
        page_count = 5
        pages = range(1, page_count + 1)
        limit = 3
        current_page = page_count // 2
        href_first = "javascript:alert('This is only a mock-up.')"
        href_prev = href_next = href_last = href_first
        get_href = lambda self, page, **kw: self.href_first

    def display(self, *args, **kw):
        # activate paginate var provider
        import turbogears.paginate
        from cherrypy import request
        request.paginate = self.Paginate()
        return super(PaginateDataGridDesc, self).display(*args, **kw)

    def render(self, *args, **kw):
        # activate paginate var provider
        import turbogears.paginate
        from cherrypy import request
        request.paginate = self.Paginate()
        return super(PaginateDataGridDesc, self).render(*args, **kw)
