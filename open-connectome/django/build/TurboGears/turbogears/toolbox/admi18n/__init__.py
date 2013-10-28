"""Graphical user interface for i18n administration"""

import os
import sys
import time
import shutil
import codecs

import turbogears
from turbogears import controllers, expose, i18n
from turbogears.i18n.pygettext import pygettext
from turbogears.i18n.pygettext import msgfmt
from turbogears.i18n.pygettext import catalog

import cherrypy
from cherrypy.lib import static

# this is a list of supported file extensions.
supported_exts = ['.py', '.kid', '.tmpl', '.html', '.mak']


class Internationalization(controllers.RootController):
    """I18N administration tool.

    Collect your strings, add and manage locales,
    edit and compile your catalogs.

    """

    __label__ = 'admi18n'
    __version__ = '0.1'
    __author__ = 'Ronald Jaramillo'
    __email__ = 'ronald@checkandshare.com'
    __copyright__ = 'Copyright 2005 Ronald Jaramillo'
    __license__ = 'MIT'

    baseTemplate = 'turbogears.toolbox.admi18n'
    languages = None
    icon = "/tg_static/images/admi18n.png"
    need_project = True

    def __init__(self, currentProject=None):
        self.currentProject = currentProject
        if not self.currentProject:
            self.currentProject = os.getcwd()

    def get_languages(self):
        if not self.languages:
            self.languages = i18n.get_languages()

        return self.languages

    def remove_locale(self, code):
        locales = self.locales_directory()
        if type(code) != type([]):
            code = [code]

        for c in code:
            path = os.path.join(locales, c)
            try:
                shutil.rmtree(path)
            except OSError,e:
                print e
                return

    def compile_catalogs(self, codes):
        locales = self.locales_directory()
        for code in codes.split(','):
            path = os.path.join(locales, code, 'LC_MESSAGES', 'messages.po')
            if not os.path.exists(path):
                continue

            dest = path.replace('.po', '.mo')
            #run msgfmt on file...
            msgfmt.make(path, dest)

    def merge_catalogs(self, codes):
        locales = self.locales_directory()
        src = os.path.join(locales, 'messages.pot')
        paths = []
        for code in codes.split(','):
            path = os.path.join(locales, code, 'LC_MESSAGES', 'messages.po')
            if not os.path.exists(path):
                continue

            paths.append(path)
        catalog.merge(src, paths)

    def add_locale(self, code):
        locales = self.locales_directory()
        path = os.path.join(locales, code)
        try:
            os.mkdir(path)
        except OSError, e:
            print e
            return

        path = os.path.join(path, 'LC_MESSAGES')
        try:
            os.mkdir(path)
        except OSError, e:
            print e
            return

        src = os.path.join(locales, 'messages.pot')
        dest = os.path.join(path, 'messages.po')
        shutil.copy(src, dest)

    @expose('json')
    def po_upload(self, myFile, code):
        path = os.path.join(self.locales_directory(),
                code, 'LC_MESSAGES', 'messages.po')
        f = codecs.open(path, 'wb', 'utf-8')
        f.write(unicode(myFile.file.read(), 'utf-8', errors='replace'))
        f.close()
        raise cherrypy.HTTPRedirect(turbogears.url('language', code=code))

    def google_translate(self, code, from_lang, to_lang, args):
        path = os.path.join(self.locales_directory(),
            code, 'LC_MESSAGES', 'messages.po')
        for arg in args:
            if not 'text_' in arg:
                continue
            msg_id = args[arg].strip()
            if '\r' in msg_id:
                msg_id = '\n'.join(msg_id.splitlines())
            translated = i18n.utils.google_translate(
                    from_lang, to_lang, msg_id)
            catalog.update(path, msg_id, translated)

    @expose('json')
    def update_catalog(self, code, msg_id, msg_text):
        path = os.path.join(self.locales_directory(),
                code, 'LC_MESSAGES', 'messages.po')
        catalog.update(path, msg_id, msg_text)
        return 'ok'

    @expose('%s.po_view' % baseTemplate)
    def po_view(self, code, sort_by=None, dir=None,
            from_lang=None, to_lang=None, **kargs):
        visible_checkbox = False
        if from_lang and to_lang:
            visible_checkbox = True
            self.google_translate(code, from_lang, to_lang, kargs)
        path = os.path.join(self.locales_directory(),
                code, 'LC_MESSAGES', 'messages.po')
        return dict(code=code, catalog=catalog.items(path, sort_by, dir),
                visible_checkbox=visible_checkbox)

    @expose('%s.language' % baseTemplate)
    def language(self, code):
        path = os.path.join(self.locales_directory(),
            code, 'LC_MESSAGES', 'messages.po')
        po_message_file = dict(path=path,
            modified=time.ctime(os.path.getmtime(path)),
            size=os.path.getsize(path))
        return dict(code=code,
            language=self.language_for_code(code),
            po_message_file=po_message_file)

    @expose('json')
    def language_list(self):
        return dict(languages=self.get_languages())

    @expose('%s.languageManagement' % baseTemplate)
    def language_management(self, add=None, rem=None, compile=None, merge=None):
        if add:
            self.add_locale(add)
        if rem:
            self.remove_locale(rem)
        if compile:
            self.compile_catalogs(compile)
        if merge:
            self.merge_catalogs(merge)
        return dict(languages=list(),
            locales=self.project_locales())

    def language_for_code(self, code):
        for c, language in self.get_languages():
            if c == code:
                return language

    def locales_directory(self):
        locales_dir = os.path.join(self.currentProject, 'locales')
        if not os.path.isdir(locales_dir):
            try:
                os.mkdir(locales_dir)
            except OSError, e:
                print e
                return
        return locales_dir

    def project_locales(self):
        locales = []
        locales_dir = self.locales_directory()
        if not locales_dir:
            return locales

        for item in os.listdir(locales_dir):
            path = os.path.join(locales_dir, item)
            if not os.path.isdir(path):
                continue

            language = self.language_for_code(item)
            if not language:
                continue

            modified = '-'
            compiled = '-'
            po = os.path.join(path, 'LC_MESSAGES', 'messages.po')
            mo = os.path.join(path, 'LC_MESSAGES', 'messages.mo')
            if os.path.exists(po):
                modified = time.ctime(os.path.getmtime(po))

            if os.path.exists(mo):
                compiled = time.ctime(os.path.getmtime(mo))

            locales.append(dict(
                             code=item,
                             language=language,
                             coverage=0,
                             status=0,
                             modified=modified,
                             compiled=compiled
                           ))
        return locales

    def project_files(self):
        p = turbogears.util.get_package_name()
        base_level = len([x for x in p.split(os.sep) if x])
        fl, dct, visibility = [], {}, {}

        def collect_files(file_list, dirpath, namelist):
            level = len([x for x in dirpath.split(os.sep) if x]) - base_level
            slot0 = dict( # directory info
                dir=os.path.dirname(dirpath),
                file_name=os.path.basename(dirpath),
                path=dirpath, isdir=True, level=level)
            slot1 = list() # children directories info
            slot2 = list() # children files info
            slots = (slot0, slot1, slot2)
            dct[dirpath] = slots
            if level:
                dct[os.path.dirname(dirpath)][1].append(slots)
            else:
                file_list.append(slots)

            namelist.sort()
            for name in namelist[:]:
                if (name.startswith('.')
                        or name in ['static', 'sqlobject-history']):
                    namelist.remove(name)
                    continue

                p = os.path.join(dirpath, name)
                if (os.path.isfile(p)
                        and os.path.splitext(name)[-1] in supported_exts):
                    slot2.append(dict(dir=dirpath, file_name=name,
                        path=p, isdir=os.path.isdir(p), level=level+1))

            # decide if current directory (and ancestors) should be visible
            visibility[dirpath] = bool(slot2)
            if slot2:
                while not visibility.get(os.path.dirname(dirpath), True):
                    dirpath = os.path.dirname(dirpath)
                    visibility[dirpath] = True

        os.path.walk(p, collect_files, fl)
        return [x for x in turbogears.util.flatten_sequence(fl)
                if not x['isdir'] or visibility[x['path']]]

    def collect_string_for_files(self, files):
        if not files:
            return

        params = ['', '-v']
        for file in files:
            params.append(file)

        pygettext.sys.argv = params
        pygettext.main()

        pot = os.path.join(self.currentProject, 'messages.pot')
        if not os.path.exists(pot):
            return

        locales = self.locales_directory()
        filename = os.path.join(locales, 'messages.pot')
        try:
            shutil.copyfile(pot, filename)
        except IOError, e:
            print e

    def pot_message_file(self):
        locales = self.locales_directory()
        pot = os.path.join(locales, 'messages.pot')
        if not os.path.exists(pot):
            return

        return dict(name='messages.pot', path=pot,
            modified=time.ctime(os.path.getmtime(pot)),
            size=os.path.getsize(pot))

    @expose()
    def lang_file(self, code):
        # serve static file, the code can be pot or a lang code
        locales = self.locales_directory()
        if code == 'pot':
            path = os.path.join(locales, 'messages.pot')
        else:
            path = os.path.join(locales, code)
            path = os.path.join(path, 'LC_MESSAGES')
            path = os.path.join(path, 'messages.po')
        if 'If-Modified-Since' in cherrypy.request.headers:
            del cherrypy.request.headers['If-Modified-Since'] # see ticket #879
        return static.serve_file(path, 'application/x-download', 'attachment')

    @expose('%s.stringCollection' % baseTemplate)
    def string_collection(self, files=[]):
        if files:
            if type(files) != type([]):
                files = [files]
            self.collect_string_for_files(files)
        return dict(project_files=self.project_files(),
            pot_message_file=self.pot_message_file())

    @expose('%s.internationalization' % baseTemplate)
    def index(self):
        return dict()
