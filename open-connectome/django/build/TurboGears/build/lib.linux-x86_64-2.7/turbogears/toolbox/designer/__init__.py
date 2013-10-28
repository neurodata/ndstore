"""Graphical user interface for SQLObject's model design"""

import os
import string
import shutil

import pkg_resources

import cherrypy

try:
    import sqlobject
except ImportError:
    sqlobject = None

import turbogears
from turbogears import controllers, expose
from turbogears.util import get_model, get_package_name, get_project_name


model_template = """from datetime import datetime
from turbogears.database import PackageHub
from sqlobject import *
from turbogears import identity

hub = PackageHub('%s')
__connection__ = hub

%s
"""

session_file_name = 'model_designer.tmp'


def version_file(file_spec, vtype='copy'):
    """By Robin Parmar & Martin Miller from Python Cookbook 2. edition"""

    if os.path.isfile(file_spec):
        # check the 'vtype' parameter
        if vtype not in ('copy', 'rename'):
            raise ValueError('Unknown vtype %r' % (vtype,))

        # determine root file name so the extension doesn't get longer and longer...
        n, e = os.path.splitext(file_spec)

        # is e a three-digets integer preceded by a dot?
        if len(e) == 4 and e[1:].isdigit():
            num = 1 + int(e[1:])
            root = n
        else:
            num = 0
            root = file_spec

        # Find next available file version
        for i in xrange(num, 1000):
            new_file = '%s.%03d' % (root, i)
            if not os.path.exists(new_file):
                if vtype == 'copy':
                    shutil.copy(file_spec, new_file)
                else:
                    os.rename(file_spec, new_file)
                return True
        raise RuntimeError("Can't %s %r, all names taken" % (vtype, file_spec))
    return False


class Designer(controllers.RootController):
    """Designer for SQLObject models.

    Create your classes, define your fields and manage your relations.
    Visualize and generate code for SQLObject models.

    """

    __label__ = 'ModelDesigner'
    __version__ = '0.1'
    __author__ = 'Ronald Jaramillo'
    __email__ = 'ronald@checkandshare.com'
    __copyright__ = 'Copyright 2005 Ronald Jaramillo'
    __license__ = 'MIT'

    baseTemplate = 'turbogears.toolbox.designer'
    model = None
    icon = "/tg_static/images/designer.png"

    def __init__(self):
        if not sqlobject:
            raise ImportError("Cannot run the Model Designer.\n"
                "The SQLObject package is not installed.")
        self.register_static_directory()
        self.model = self.get_model_name()

    def set_model(self, model):
        self.model = model

    def get_model_name(self):
        if not get_project_name():
            return False
        return get_model()

    def register_static_directory(self):
        static_directory = pkg_resources.resource_filename(__name__, 'static')
        turbogears.config.update({'/tg_toolbox/designer': {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir': static_directory}})

    def column_type(self, column):
        """Given a column representation return the column type."""
        column_type = '%r' % column
        return column_type.split()[0][1:].split('.')[-1]

    def column_default(self, column, column_type):
        try:
            default = column.default
        except AttributeError:
            return ''
        if default == sqlobject.sqlbuilder.NoDefault:
            return ''
        if column_type in ('SOIntCol', 'SOFloatCol', 'SOStringCol',
             'SODecimalCol', 'SOCurrencyCol'):
            return default
        elif column_type == 'SODateTimeCol':
            d = '%s' % default
            return ':'.join(d.split(':')[:-1])
        elif column_type == 'SODateCol':
            d = '%s' % default
            return d.split(None, 1)[0]
        return ''

    def load_column(self, column_name, column, model_object):
        props = {}
        props['type'] = self.column_type(column)
        props['column_name'] = column_name
        props['name'] = column_name
        props['column_default'] = self.column_default(column, props['type'])
        try:
            props['title'] = getattr(column, 'title') or ''
        except AttributeError:
            props['title'] = ''
        if props['type'] == 'SOStringCol':
            props['length'] = column.length
            props['varchar'] = column.varchar
        if props['type'] == 'SOEnumCol':
            props['enum_values'] = column.enumValues
        if props['type'] == 'SOForeignKey':
            props['join_type'] = 'MultipleJoin'
            props['other_class_name'] = column.foreignKey
            props['other_method_name'] = self.other_method_name(
                column, model_object.__name__)
        if props['type'] in ('SOMultipleJoin','SORelatedJoin'):
            props['other_class_name'] = column.otherClassName
            props['join_type'] = props['type'].replace('SO', '')
            props['other_method_name'] = self.other_method_join_name(
                column, model_object.__name__)

        props['type'] = props['type'].replace('SO','')
        return props

    def other_method_join_name(self, column, model_object_name):
        for col in column.otherClass.sqlmeta.columnList:
            if type(col) == sqlobject.SOForeignKey:
                if col.foreignKey == model_object_name:
                    return col.origName
        return 'id'

    def other_method_name(self, column, model_object_name):
        other_class_name = column.foreignKey
        model_object = getattr(self.get_model_name(), other_class_name)
        for col in model_object.sqlmeta.joins:
            if col.otherClassName == model_object_name:
                return col.joinMethodName
        return 'id'

    def is_inheritable_base_class(self, obj):
        """Check if the object is  a direct subclass of InheritableSQLObject"""
        return 'sqlobject.inheritance.InheritableSQLObject' in str(obj.__bases__)

    def load_columns(self, model_object):
        columns = {}
        # get normal columns
        for column_name in model_object.sqlmeta.columns:
            column = model_object.sqlmeta.columns[column_name]
            origname = column.origName
            if model_object._inheritable and column_name == 'childName':
                continue
            columns[origname] = self.load_column(origname, column, model_object)
        # get join columns
        for column in model_object.sqlmeta.joins:
            columns[column.joinMethodName] = self.load_column(
                column.joinMethodName, column, model_object)
        return columns

    @expose('json')
    def load_current_model(self):
        model = self.get_model_name()
        current_model = {}
        current_model['name'] = get_package_name()
        current_model['models'] = {}
        current_model['ordered_models'] = []

        for m in dir(model):
            if m in ('SQLObject', 'InheritableSQLObject'):
                continue
            model_object = getattr(model, m)
            if isinstance(model_object, type) and issubclass(
                    model_object, sqlobject.SQLObject):
                parent_class = 'SQLObject'
                if model_object._inheritable:
                    parent_class = model_object._parentClass.__name__
                columns = self.load_columns(model_object)
                current_model['ordered_models'].append(m)
                current_model['models'][m] = {
                    'name': m,
                    'parent_class': parent_class,
                    'table_name': model_object.sqlmeta.table,
                    'id_name': model_object.sqlmeta.idName,
                    'columns': columns,
                    'relations': {}}
        return dict(model=current_model)

    def save_session_as_name(self, name):
        # remove non-ascii
        if isinstance(name, unicode):
            name = name.encode('ascii', 'replace')
        # remove punctuation
        name = name.translate(string.maketrans('', ''), string.punctuation)
        # camelcase to remove spaces
        name =  ''.join([x.title() for x in name.split()])
        sessions_directory = pkg_resources.resource_filename(__name__,
            os.path.join('static', 'sessions'))
        for idx in range(100):
            postfix = idx and '_%d' % idx or ''
            test_name = '%s%s.js' % (name, postfix)
            full_name = os.path.join(sessions_directory, test_name)
            if not os.path.exists(full_name):
                return full_name

    @expose('json')
    def save_state(self, state, name=session_file_name):
        if name != session_file_name:
            name = self.save_session_as_name(name)
        if not name:
            return dict(state=False)
        f = open(name,'w')
        f.write(state)
        f.close()
        return dict(state=True)

    def model_path(self):
        return os.path.abspath(
            os.path.join(get_package_name(), 'model.py'))

    def save_model(self, code):
        project_name = get_package_name()
        model_text = model_template % (project_name, code)
        model_path = self.model_path()
        if os.path.exists(model_path):
            version_file(model_path)
            f = open(model_path,'w')
            f.write(model_text)
            f.close()
            return True, 'Saved %s' % model_path
        else:
            return False, 'Failed to save %s' % model_path

    def save_and_create_(self, code, order):
        model_path = os.path.join(get_project_name(), 'tmp2_model.py')
        model_path = os.path.abspath(model_path)
        open(model_path, 'w').write(str)
        package = __import__(get_package_name(), {}, {}, ['tmp2_model'])
        package.tmp2_model.Persona.createTable(ifNotExists=True)
        model = self.get_model_name()
        model.Persona = package.tmp2_model.Persona
        # pk = package.model
        # import tmp_model as pk
        # pk.Persona.createTable(ifNotExists=True)
        return dict(status='Tables ok')

    @expose('json')
    def save_and_create(self, code, order):
        status_code, status = self.save_model(code)
        if not status_code:
            return dict(status=status)
        tmp_name = 'tmp_model'

        # copy the model file
        model_path = self.model_path()
        tmp_model_path = model_path.replace('model.py','%s.py' % tmp_name)
        try:
            shutil.copy(model_path, tmp_model_path)
        except IOError, e:
            return dict(status='Failed to create a temporary model file: %s' % e)

        model = self.get_model_name()
        package = __import__(get_package_name(), {}, {}, [tmp_name])
        tmp_model = getattr(package, tmp_name)

        ok = []
        fail = []
        classes = order.split(',')
        for class_name in classes:
            try:
                obj = getattr(tmp_model, class_name)
                obj.createTable(ifNotExists=True)
                setattr(model, class_name, obj)
                ok.append('Table created for class %s' % class_name)
            except Exception, e:
                fail.append('Failed to create table for class %s: %s'
                    % (class_name,e))

        if len(ok):
            status += '\nTables Created: \n%s' % '\n'.join(ok)
        if len(fail):
            status += '\nFailed to create Tables:\n%s' % '\n'.join(fail)

        try:
            os.remove(tmp_model_path)
        except IOError, e:
            print "Fail to remove temporary model file: %s" % e

        return dict(status=status)

    def load_session_list(self):
        sessions_directory = pkg_resources.resource_filename(
            __name__, os.path.join('static', 'sessions'))
        return [x.replace('.js','')
            for x in os.listdir(sessions_directory) if x.endswith('.js')]

    def session_exists(self):
        return os.path.exists(session_file_name)

    @expose('json')
    def retrieve_sample(self, name):
        sessions_directory = pkg_resources.resource_filename(
            __name__, os.path.join('static', 'sessions'))
        full_path = os.path.join(sessions_directory,'%s.js' % name)
        if not os.path.exists(full_path):
            return dict()
        return dict(session=open(full_path,'r').read())

    @expose('json')
    def current_session_model(self):
        if not self.session_exists():
            return dict()
        return dict(session=open(session_file_name, 'r').read())

    @expose('json')
    def save(self, code):
        status = self.save_model(code)[1]
        return dict(status=status)

    @expose('json')
    def session_list(self):
        return dict(models=self.load_session_list())

    @expose('%s.modelDesigner' % baseTemplate)
    def index(self):
        return dict(model_exists=bool(self.model),
            session_file_exists=self.session_exists(),
            session_list=self.load_session_list(),
            model_name=get_project_name())
