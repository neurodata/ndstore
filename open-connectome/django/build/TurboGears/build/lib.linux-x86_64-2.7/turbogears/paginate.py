
import types
from math import ceil
import logging

import cherrypy
try:
    import sqlobject
except ImportError:
    sqlobject = None

try:
    import sqlalchemy
    try:
        from sqlalchemy.exc import InvalidRequestError
        sqlalchemy_before_0_5 = False
    except ImportError: # SQLAlchemy < 0.5
        from sqlalchemy.exceptions import InvalidRequestError
        sqlalchemy_before_0_5 = True
except ImportError:
    sqlalchemy = None

import turbogears
from turbogears.controllers import redirect
from turbogears.decorator import weak_signature_decorator
from turbogears.view import variable_providers
from formencode.variabledecode import variable_encode
from turbogears.util import add_tg_args

log = logging.getLogger('turbogears.paginate')


# lists of databases that lack support for OFFSET
# this will need to be updated periodically as modules change
_so_no_offset = 'mssql maxdb sybase'.split()
_sa_no_offset = 'mssql maxdb access'.split()

# this is a global that is set the first time paginate() is called
_simulate_offset = None

# these are helper classes for getting data that has no table column
class attrwrapper:
    """Helper class for accessing object attributes."""
    def __init__(self, name):
        self.name = name
    def __call__(self, obj):
        for name in self.name.split('.'):
            obj = getattr(obj, name)
        return obj

class itemwrapper:
    """Helper class for dictionary access."""
    def __init__(self, name):
        self.name = name
    def __call__(self, obj):
        return obj[self.name]


def paginate(var_name, default_order='', limit=10,
            max_limit=0, max_pages=5, max_sort=1000, dynamic_limit=None):
    """The famous TurboGears paginate decorator.

    @param var_name: the variable name that the paginate decorator will try
    to control. This key must be present in the dictionary returned from your
    controller in order for the paginate decorator to be able to handle it.
    @type var_name: string

    @param default_order: The column name(s) that will be used to order
    pagination results. Due to the way pagination is implemented specifying a
    default_order will override any result ordering performed in the controller.
    @type default_order: string or a list of strings. Any string starting with
    "-" (minus sign) indicates a reverse order for that field/column.

    @param limit: The hard-coded limit that the paginate decorator will impose
    on the number of "var_name" to display at the same time. This value can be
    overridden by the use of the dynamic_limit keyword argument.
    @type limit: integer

    @param max_limit: The maximum number to which the imposed limit can be
    increased using the "var_name"_tgp_limit keyword argument in the URL.
    If this is set to 0, no dynamic change at all will be allowed;
    if it is set to None, any change will be allowed.
    @type max_limit: int

    @param max_pages: Used to generate the tg.paginate.pages variable. If the
    page count is larger than max_pages, tg.paginate.pages will only contain
    the page numbers surrounding the current page at a distance of max_pages/2.
    A zero value means that all pages will be shown, no matter how much.
    @type max_pages: integer

    @param max_sort: The maximum number of records that will be sorted in
    memory if the data cannot be sorted using SQL. If set to 0, sorting in
    memory will never be performed; if set to None, no limit will be imposed.
    @type max_sort: integer

    @param dynamic_limit: If specified, this parameter must be the name
    of a key present in the dictionary returned by your decorated
    controller. The value found for this key will be used as the limit
    for our pagination and will override the other settings, the hard-coded
    one declared in the decorator itself AND the URL parameter one.
    This enables the programmer to store a limit settings inside the
    application preferences and then let the user manage it.
    @type dynamic_limit: string

    """

    def entangle(func):

        get = turbogears.config.get

        def decorated(func, *args, **kw):

            def kwpop(name, default=None):
                return kw.pop(var_name + '_tgp_' + name, default)

            page = kwpop('no')
            if page is None:
                page = 1
            elif page == 'last':
                page = None
            else:
                try:
                    page = int(page)
                    if page < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    page = 1
                    if get('paginate.redirect_on_out_of_range'):
                        cherrypy.request.params[var_name + '_tgp_no'] = page
                        redirect(cherrypy.request.path_info, cherrypy.request.params)

            try:
                limit_ = int(kwpop('limit'))
                if max_limit is not None:
                    if max_limit <= 0:
                        raise ValueError
                    limit_ = min(limit_, max_limit)
            except (TypeError, ValueError):
                limit_ = limit
            order = kwpop('order')
            ordering = kwpop('ordering')

            log.debug("paginate params: page=%s, limit=%s, order=%s",
                page, limit_, order)

            # get the output from the decorated function
            output = func(*args, **kw)
            if not isinstance(output, dict):
                return output

            try:
                var_data = output[var_name]
            except KeyError:
                raise KeyError("paginate: var_name"
                    " (%s) not found in output dict" % var_name)
            if not hasattr(var_data, '__getitem__') and callable(var_data):
                # e.g. SQLAlchemy query class
                var_data = var_data()
                if not hasattr(var_data, '__getitem__'):
                    raise TypeError('Paginate variable is not a sequence')

            if dynamic_limit:
                try:
                    dyn_limit = output[dynamic_limit]
                except KeyError:
                    raise KeyError("paginate: dynamic_limit"
                        " (%s) not found in output dict" % dynamic_limit)
                limit_ = dyn_limit

            if ordering:
                ordering = str(ordering).split(',')
            else:
                ordering = default_order or []
                if isinstance(ordering, basestring):
                    ordering = [ordering]

            if order:
                order = str(order)
                log.debug('paginate: ordering was %s, sort is %s',
                    ordering, order)
                sort_ordering(ordering, order)
            log.debug('paginate: ordering is %s', ordering)

            try:
                row_count = len(var_data)
            except TypeError:
                try: # SQL query
                    row_count = var_data.count() or 0
                except AttributeError: # other iterator
                    var_data = list(var_data)
                    row_count = len(var_data)

            if ordering:
                var_data = sort_data(var_data, ordering,
                    max_sort is None or 0 < row_count <= max_sort)

            # If limit is zero then return all our rows
            if not limit_:
                limit_ = row_count or 1

            page_count = int(ceil(float(row_count)/limit_))

            if page is None:
                page = max(page_count, 1)
                if get('paginate.redirect_on_last_page'):
                    cherrypy.request.params[var_name + '_tgp_no'] = page
                    redirect(cherrypy.request.path_info, cherrypy.request.params)
            elif page > page_count:
                page = max(page_count, 1)
                if get('paginate.redirect_on_out_of_range'):
                    cherrypy.request.params[var_name + '_tgp_no'] = page
                    redirect(cherrypy.request.path_info, cherrypy.request.params)

            offset = (page-1) * limit_

            pages_to_show = _select_pages_to_show(page, page_count, max_pages)

            # remove pagination parameters from request
            input_values =  variable_encode(cherrypy.request.params.copy())
            input_values.pop('self', None)
            for input_key in input_values.keys():
                if input_key.startswith(var_name + '_tgp_'):
                    del input_values[input_key]

            paginate_instance = Paginate(
                current_page=page,
                limit=limit_,
                pages=pages_to_show,
                page_count=page_count,
                input_values=input_values,
                order=order,
                ordering=ordering,
                row_count=row_count,
                var_name=var_name)

            cherrypy.request.paginate = paginate_instance
            if not hasattr(cherrypy.request, 'paginates'):
                cherrypy.request.paginates = dict()
            cherrypy.request.paginates[var_name] = paginate_instance

            # we replace the var with the sliced one
            endpoint = offset + limit_
            log.debug("paginate: slicing data between %d and %d",
                offset, endpoint)

            global _simulate_offset
            if _simulate_offset is None:
                _simulate_offset = get('paginate.simulate_offset', None)
                if _simulate_offset is None:
                    _simulate_offset = False
                    so_db = get('sqlobject.dburi', 'NOMATCH:').split(':', 1)[0]
                    sa_db = get('sqlalchemy.dburi', 'NOMATCH:').split(':', 1)[0]
                    if so_db in _so_no_offset or sa_db in _sa_no_offset:
                        _simulate_offset = True
                        log.warning("paginate: simulating OFFSET,"
                            " paginate may be slow"
                            " (disable with paginate.simulate_offset=False)")

            if _simulate_offset:
                var_data = iter(var_data[:endpoint])
                # skip over the number of records specified by offset
                for i in xrange(offset):
                    var_data.next()
                # return the records that remain
                output[var_name] = list(var_data)
            else:
                try:
                    output[var_name] = var_data[offset:endpoint]
                except TypeError:
                    for i in xrange(offset):
                        var_data.next()
                    output[var_name] = [var_data.next()
                        for i in xrange(offset, endpoint)]

            return output

        if not get('tg.strict_parameters', False):
            # add hint that paginate parameters shall be left intact
            add_tg_args(func, (var_name + '_tgp_' + arg
                for arg in ('no', 'limit', 'order', 'ordering')))
        return decorated

    return weak_signature_decorator(entangle)


def _paginate_var_provider(d):
    """Auxiliary function for providing the paginate variable."""
    paginate = getattr(cherrypy.request, 'paginate', None)
    if paginate:
        d.update(dict(paginate=paginate))
    paginates = getattr(cherrypy.request, 'paginates', None)
    if paginates:
        d.update(dict(paginates=paginates))
variable_providers.append(_paginate_var_provider)


class Paginate:
    """Class for paginate variable provider."""

    def __init__(self, current_page, pages, page_count, input_values,
                 limit, order, ordering, row_count, var_name):

        self.var_name = var_name
        self.pages = pages
        self.limit = limit
        self.page_count = page_count
        self.current_page = current_page
        self.input_values = input_values
        self.order = order
        self.ordering = ordering
        self.row_count = row_count
        self.first_item = page_count and ((current_page - 1) * limit + 1) or 0
        self.last_item = min(current_page * limit, row_count)

        self.reversed = ordering and ordering[0][0] == '-'

        # If ordering is empty, don't add it.
        input_values = {var_name + '_tgp_limit': limit}
        if ordering:
            input_values[var_name + '_tgp_ordering'] = ','.join(ordering)
        self.input_values.update(input_values)

        if current_page < page_count:
            self.input_values.update({
                var_name + '_tgp_no': current_page + 1,
                var_name + '_tgp_limit': limit
            })
            self.href_next = turbogears.url(
                cherrypy.request.path_info, self.input_values)
            self.input_values.update({
                var_name + '_tgp_no': 'last',
                var_name + '_tgp_limit': limit
            })
            self.href_last = turbogears.url(
                cherrypy.request.path_info, self.input_values)
        else:
            self.href_next = None
            self.href_last = None

        if current_page > 1:
            self.input_values.update({
                var_name + '_tgp_no': current_page - 1,
                var_name + '_tgp_limit': limit
            })
            self.href_prev = turbogears.url(
                cherrypy.request.path_info, self.input_values)
            self.input_values.update({
                var_name + '_tgp_no': 1,
                var_name + '_tgp_limit': limit
            })
            self.href_first = turbogears.url(
                cherrypy.request.path_info, self.input_values)
        else:
            self.href_prev = None
            self.href_first = None

    def get_href(self, page, order=None, reverse_order=None):
        # Note that reverse_order is not used.  It should be cleaned up here
        # and in the template.  I'm not removing it now because I don't want
        # to break the API.
        order = order or None
        input_values = self.input_values.copy()
        input_values[self.var_name + '_tgp_no'] = page
        if order:
            input_values[ self.var_name + '_tgp_order'] = order
        return turbogears.url('', input_values)


def _select_pages_to_show(current_page, page_count, max_pages=None):
    """Auxiliary function for getting the range of pages to show."""
    if max_pages is not None and max_pages > 0:
        start = current_page - (max_pages // 2) - (max_pages % 2) + 1
        end = start + max_pages - 1
        if start < 1:
            start, end = 1, min(page_count, max_pages)
        elif end > page_count:
            start, end = max(1, page_count - max_pages + 1), page_count
    else:
        start, end = 1, page_count
    return xrange(start, end + 1)


# Auxiliary functions for dealing with columns and SQL

def sort_ordering(ordering, sort_name):
    """Rearrange ordering based on sort_name."""
    try:
        index = ordering.index(sort_name)
    except ValueError:
        try:
            index = ordering.index('-' + sort_name)
        except ValueError:
            ordering.insert(0, sort_name)
        else:
            del ordering[index]
            ordering.insert(0, (index and '-' or '') + sort_name)
    else:
        del ordering[index]
        ordering.insert(0, (not index and '-' or '') + sort_name)

def sqlalchemy_get_column(colname, var_data, join_props=None):
    """Return a column from SQLAlchemy var_data based on colname."""
    if sqlalchemy_before_0_5:
        mapper = var_data.mapper
    else:
        mapper = var_data._mapper_zero()
    propnames = colname.split('.')
    colname = propnames.pop()
    props = []
    for propname in propnames:
        try:
            prop = mapper.get_property(propname)
        except InvalidRequestError:
            prop = None
        if not prop:
            break
        if join_props is not None:
            props.append(prop)
        mapper = prop.mapper
    col = getattr(mapper.c, colname, None)
    if col is not None and props:
        join_props.extend(props)
    return col

def sqlobject_get_column(colname, var_data, join_props=None):
    """Return a column from SQLObject var_data based on colname."""
    return getattr(var_data.sourceClass.q, colname, None)

def sql_get_column(colname, var_data):
    """Return a column from var_data based on colname."""
    if sqlalchemy:
        try:
            return sqlalchemy_get_column(colname, var_data)
        except AttributeError:
            pass
    if sqlobject:
        try:
            return sqlobject_get_column(colname, var_data)
        except AttributeError:
            pass
    raise TypeError('Cannot find columns of paginate variable')

def sqlalchemy_order_col(col, descending=False):
    """Return an SQLAlchemy ordered column for col."""
    if descending:
        return sqlalchemy.sql.desc(col)
    else:
        return sqlalchemy.sql.asc(col)

def sqlobject_order_col(col, descending=False):
    """Return an SQLObject ordered column for col."""
    if descending:
        return sqlobject.DESC(col)
    else:
        return col

def sql_order_col(col, ascending=True):
    """Return an ordered column for col."""
    if sqlalchemy and isinstance(col, sqlalchemy.sql.ColumnElement):
        return sqlalchemy_order_col(col, ascending)
    elif sqlobject and isinstance(col, types.InstanceType):
        # Sadly, there is no better way to check for SQLObject col type
        return sqlobject_order_col(col, ascending)
    raise TypeError("Expected Column, but got %s" % type(col))

def sqlalchemy_join_props(var_data, join_props):
    """Return a query where all tables for properties are joined."""
    if join_props:
        attrs = []
        for prop in join_props:
            try:
                attrs.append(prop.class_attribute)
            except AttributeError: # SQLAlchemy < 0.6
                try:
                    attrs.append(getattr(prop.parent.class_, prop.key))
                except AttributeError:
                    pass
        if attrs:
            log.debug("paginate: need to join some attributes")
            if sqlalchemy_before_0_5: # old version, gets single argument
                var_data = var_data.outerjoin(attrs)
            else:
                var_data = var_data.outerjoin(*attrs)
    return var_data

def sort_data(data, ordering, in_memory=True):
    """Sort data based on ordering.

    Tries to sort the data using SQL whenever possible,
    otherwise sorts the data as list in memory unless in_memory is false.

    """
    try:
        order_by = data.order_by # SQLAlchemy, gets variable argument list
        if sqlalchemy_before_0_5:
            old_order_by = order_by # old version, gets single argument
            order_by = lambda *cols: old_order_by(cols)
        get_column, order_col = sqlalchemy_get_column, sqlalchemy_order_col
    except AttributeError:
        try:
            orderBy = data.orderBy  # SQLObject, gets single argument
            order_by = lambda *cols: orderBy(cols)
            get_column, order_col = sqlobject_get_column, sqlobject_order_col
        except AttributeError:
            order_by = None
    order_cols = []
    key_cols = []
    num_ascending = num_descending = 0
    join_props = []
    for order in ordering:
        if order[0] == '-':
            order = order[1:]
            descending = True
        else:
            descending = False
        if order_by:
            col = get_column(order, data, join_props)
            if col is not None:
                order_cols.append(order_col(col, descending))
                continue
        if not order_cols:
            key_cols.append((order, descending))
            if descending:
                num_descending += 1
            else:
                num_ascending += 1
    if order_by and order_cols:
        data = order_by(*order_cols)
        if join_props:
            data = sqlalchemy_join_props(data, join_props)
    if key_cols:
        if in_memory:
            data = list(data)
            if not data:
                return data
            wrapper = isinstance(data[0], dict) and itemwrapper or attrwrapper
            keys = [(wrapper(col[0]), col[1]) for col in key_cols]
            if num_ascending == 0 or num_descending == 0:
                reverse = num_ascending == 0
                keys = [key[0] for key in keys]
                if len(key_cols) == 1:
                    key = keys[0]
                else:
                    key = lambda row: [key(row) for key in keys]
            else:
                reverse = num_descending > num_ascending
                def reverse_key(key, descending):
                    if reverse == descending:
                        return key
                    else:
                        keys = map(key, data)
                        try:
                            keys = list(set(keys))
                        except TypeError: # unhashable
                            keys.sort()
                            return lambda row: -keys.index(key(row))
                        else:
                            keys.sort()
                            keys = dict((k, -n) for n, k in enumerate(keys))
                            return lambda row: keys[key(row)]
                keys = [reverse_key(*key) for key in keys]
                key = lambda row: [key(row) for key in keys]
            log.debug("paginate: sorting in memory")
            data.sort(key=key, reverse=reverse)
        else:
            log.debug("paginate: sorting in memory not allowed")
    return data
