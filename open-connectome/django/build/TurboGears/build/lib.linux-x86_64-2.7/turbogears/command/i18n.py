# test-file: test_command_i18n.py

"""Command-line user interface for i18n administration."""

import re
import glob
import os
import atexit
import optparse
import tempfile

from pkg_resources import resource_filename
import formencode
# XXX: we need to make kid-support pluggable or such.
try:
    import kid
except ImportError:
    kid = None

from turbogears import config
from turbogears.i18n.pygettext import pygettext, msgfmt, catalog
import turbogears.i18n.utils as i18n_utils
from turbogears.command.base import silent_os_remove
from turbogears.util import load_project_config, get_package_name


class ProgramError(StandardError):
    """Signals about a general application error."""


def copy_file(src, dest):
    if os.path.exists(dest):
        os.remove(dest)
    fh = open(src, 'rb')
    data = fh.read()
    fh.close()
    fh = open(dest, 'wb')
    fh.write(data)
    fh.close()


_str_literal = r"""(?:'((?:[^']|\\')*)'|"((?:[^"]|\\")*)")"""
_py_i18n_re = re.compile(r"\b_\s*\(\s*[uU]?[rR]?%s\s*\)" % _str_literal)
_js_i18n_re = re.compile(r"\b_\s*\(\s*%s\s*\)" % _str_literal)


class InternationalizationTool(object):
    """Manages i18n data via command-line interface.

    Contributed to TurboGears by Max Ischenko (http://maxischenko.in.ua).

    """

    desc = "Manage i18n data"
    need_project = True
    config = None
    load_config = True
    locale_dir = 'locales'
    domain = 'messages'
    ignore_dirs = ('cvs', 'sqlobject-history')

    name = None
    package = None

    def __init__(self, version):
        parser = optparse.OptionParser(usage="""
%prog i18n [options] <command>

Available commands:
  add <locale>        Creates a message catalog for specified locale
  collect             Scan source files to gather translatable strings in a .pot file
  merge               Sync message catalog in different languages with .pot file
  compile             Compile message catalog (.po -> .mo)
  create_js_messages  Create message catalogs for JS usage
  clean               Delete backups and compiled files
""", version="%prog " + version)
        parser.add_option("-f", "--force", default=False,
            action="store_true", dest="force_ops",
            help="Force potentially damaging actions")
        parser.add_option("-a", "--ascii", default=False,
            action="store_true", dest="ascii_output",
            help="Escape non-ascii characters (.py files only)")
        parser.add_option("-K", "--no-kid-support", default=True,
            action="store_false", dest="kid_support",
            help="Do not extract messages from Kid templates")
        parser.add_option("-G", "--no-genshi-support", default=True,
            action="store_false", dest="genshi_support",
            help="Do not extract messages from Genshi templates")
        parser.add_option("", "--template-dir", default='templates',
            action="store", dest="template_dir",
            help="The name of directories containing templates")
        parser.add_option("", "--src-dir", default=None,
            action="store", dest="source_dir",
            help="Directory that contains source files")
        parser.add_option("", "--no-js-support", default=True,
            action="store_false", dest="js_support",
            help="Extract messages from js-files.")
        parser.add_option("", "--js-base-dir",
            action="store", dest="js_base_dir",
            default="static/javascript",
            help="Base directory of javascript files"
                " for generated message-files.")
        parser.add_option("-e", "--js-encoding",
            dest="js_encoding", default="utf-8", metavar="ENCODING",
            help="Encoding of JavaScript source files (default: UTF-8)")
        parser.set_defaults(js_support=True)
        self.parser = parser

    def load_project_config(self):
        """Choose the config file.

        Try to guess whether this is a development or installed project.

        """

        # check whether user specified custom settings
        if self.load_config:
            load_project_config(self.config)

        if config.get('i18n.locale_dir'):
            self.locale_dir = config.get('i18n.locale_dir')
            print "Use %s as a locale directory" % self.locale_dir
        if config.get('i18n.domain'):
            self.domain = config.get('i18n.domain')
            print "Use %s as a message domain" % self.domain

        if (os.path.exists(self.locale_dir)
                and not os.path.isdir(self.locale_dir)):
            raise ProgramError(
                "%s is not a directory" % self.locale_dir)

        if not os.path.exists(self.locale_dir):
            os.makedirs(self.locale_dir)

    def parse_args(self):
        return self.parser.parse_args()

    def run(self):
        self.load_project_config()
        options, args = self.parse_args()
        if not args:
            self.parser.error("No command specified")
        self.options = options
        command, args = args[0], args[1:]
        if 'collect' == command:
            self.scan_source_files()
        elif 'add' == command:
            self.add_languages(args)
        elif 'compile' == command:
            self.compile_message_catalogs()
        elif 'merge' == command:
            self.merge_message_catalogs()
        elif 'clean' == command:
            self.clean_generated_files()
        elif 'create_js_messages' == command:
            self.create_js_messages()
        else:
            self.parser.error("Command not recognized")

    def create_js_messages(self):
        self.load_project_config()
        languages = []
        # we assume the the structure of messages is always
        # <self.locale_dir>/<lang>/LC_MESSAGES ...
        # to extract the languages known to the app
        locale_dir_prefix = self.locale_dir.split(os.sep)
        for fname in self.list_message_catalogs():
            languages.append(fname.split(os.sep)[len(locale_dir_prefix):][0])
        srcdir = self.options.source_dir or get_package_name().split('.', 1)[0]
        def list_js_files():
            for root, dirs, files in os.walk(srcdir):
                dir = os.path.basename(root)
                if dir.startswith('.') or dir in self.ignore_dirs:
                    continue
                for fname in files:
                    ext = os.path.splitext(fname)[1]
                    srcfile = os.path.join(root, fname)
                    if ext == '.js':
                        yield srcfile
        def escape(arg):
            if "'" in arg:
                return '"%s"' % arg
            return "'%s'" % arg
        for locale in languages:
            def gl():
                return locale
            i18n_utils._get_locale = gl
            messages = []
            for filename in list_js_files():
                for key in self.get_strings_in_js(os.path.join(filename))[0]:
                    key = unicode(key)
                    msg = unicode(_(key, locale))
                    messages.append((key, msg))
            # for a final return
            header = """
if (typeof(MESSAGES) == 'undefined') {
    MESSAGES = {};
}

LANG = '%s';
_messages = [
""" % locale
            footer = """
             ];

for(var i in _messages) {
  MESSAGES[_messages[i][0]] = _messages[i][1];
 }
"""
            message_block = u',\n'.join(['[%s , %s]' % (escape(msgid),
                escape(msgstr)) for msgid, msgstr in messages]).encode('utf-8')
            message_block += '\n'
            outfilename = os.path.join(srcdir, self.options.js_base_dir,
                'messages-%s.js' % locale)
            print "Creating message file <%s>." % outfilename
            mf = open(outfilename, 'w')
            mf.write(header)
            mf.write(message_block)
            mf.write(footer)
            mf.close()

    def clean_generated_files(self):
        potfile = self.get_potfile_path()
        silent_os_remove(potfile.replace('.pot', '.bak'))
        for fname in self.list_message_catalogs():
            silent_os_remove(fname.replace('.po', '.mo'))
            silent_os_remove(fname.replace('.po', '.back'))

    def merge_message_catalogs(self):
        potfile = self.get_potfile_path()
        catalogs = self.list_message_catalogs()
        catalog.merge(potfile, catalogs)

    def compile_message_catalogs(self):
        for fname in self.list_message_catalogs():
            dest = fname.replace('.po','.mo')
            msgfmt.make(fname, dest)
            if os.path.exists(dest):
                print "Compiled %s OK" % fname
            else:
                print "Compilation of %s failed!" % fname

    def _copy_file_withcheck(self, sourcefile, targetfile):
        if not (os.path.exists(targetfile) and not self.options.force_ops):
            copy_file(sourcefile, targetfile)
            print "Copy", sourcefile, "to", targetfile
        else:
            print "File %s exists, use --force to override" % targetfile

    def _copy_moduletranslation(self, sourcefile, targetdir, language):
        modulefilename = os.path.basename(sourcefile)
        if os.path.exists(sourcefile):
            targetfile = os.path.join(targetdir, modulefilename)
            self._copy_file_withcheck(sourcefile, targetfile)
        else:
            print ("%s translation for language '%s' does not exist"
                " (file searched '%s').\nPlease consider to contribute"
                " a translation." % (modulefilename, language, sourcefile))

    def add_languages(self, codes):
        potfile = self.get_potfile_path()
        if not os.path.isfile(potfile):
            print "Run 'collect' first to create", potfile
            return
        for code in codes:
            catalog_file = self.get_locale_catalog(code)
            langdir = os.path.dirname(catalog_file)
            if not os.path.exists(langdir):
                os.makedirs(langdir)

            sourcefile_fe = os.path.join(formencode.api.get_localedir(), code,
                'LC_MESSAGES', 'FormEncode.mo')
            self._copy_moduletranslation(sourcefile_fe, langdir, code)

            basedir_i18n_tg = resource_filename('turbogears.i18n', 'data')
            sourcefile_tg  = os.path.join(basedir_i18n_tg, code,
                'LC_MESSAGES', 'TurboGears.mo')
            self._copy_moduletranslation(sourcefile_tg, langdir, code)

            self._copy_file_withcheck(potfile, catalog_file)

    def scan_source_files(self):
        source_files = []
        kid_files = []
        genshi_files = []
        js_files = []
        srcdir = self.options.source_dir or get_package_name().split('.', 1)[0]
        tmpldir = self.options.template_dir
        print "Scanning source directory", srcdir
        for root, dirs, files in os.walk(srcdir):
            dir = os.path.basename(root)
            if dir.startswith('.') or dir in self.ignore_dirs:
                continue
            for fname in files:
                ext = os.path.splitext(fname)[1]
                srcfile = os.path.join(root, fname)
                if ext == '.py':
                    source_files.append(srcfile)
                elif ext == '.kid' and (not tmpldir or dir == tmpldir):
                    kid_files.append(srcfile)
                elif ext == '.html' and (not tmpldir or dir == tmpldir):
                    genshi_files.append(srcfile)
                elif ext == '.js':
                    js_files.append(srcfile)
                else:
                    pass # do nothing
        tmp_handle, tmp_potfile = tempfile.mkstemp(
            '.pot', 'tmp', self.locale_dir)
        os.close(tmp_handle)
        potbasename = os.path.basename(tmp_potfile)[:-4]
        pygettext_options = ['-v', '-d', potbasename,
            '-p', os.path.dirname(tmp_potfile)]
        if self.options.ascii_output:
            pygettext_options.insert(0, '-E')
        pygettext.sys.argv = [''] + pygettext_options + source_files
        pygettext.main()
        if not os.path.exists(tmp_potfile):
            raise ProgramError("pygettext failed")
        atexit.register(silent_os_remove, tmp_potfile)

        if kid_files and self.options.kid_support:
            if not kid:
                print "Kid not installed, no support for Kid templates."
            else:
                self.scan_kid_files(tmp_potfile, kid_files)

        if genshi_files and self.options.genshi_support:
            try:
                self.scan_genshi_files(tmp_potfile, genshi_files)
            except ImportError:
                print "Genshi not installed, no support for Genshi templates."

        if js_files and self.options.js_support:
            self.scan_js_files(tmp_potfile, js_files)

        potfile = self.get_potfile_path()
        if os.path.isfile(potfile):
            bakfile = potfile.replace('.pot', '.bak')
            silent_os_remove(bakfile)
            os.rename(potfile, bakfile)
            print "Backup existing file to", bakfile
        os.rename(tmp_potfile, potfile)
        print "Message templates written to", potfile

    def scan_genshi_files(self, potfile, files):
        """Extract strings from Genhsi templates and write to pot file.

        Configuration settings:

        `genshi.i18n.ignore_tags` -- `['script', 'style']`
            List of element names. Content inside elements named in this list
            is not extracted as translatable text. Can be a space-separated
            string or a list of string.
        `genshi.i18n.include_attrs` -- `['abbr', 'alt', 'label', 'prompt',
                'standby', 'summary', 'title']`
            List of attribute names. Only values of the attributes named in
            this list are extracted as translatable text. Can be a
            space-separated string or a list os strings.

        See http://genshi.edgewall.org/wiki/Documentation/0.5.x/i18n.html for
        more information.

        """

        extract_strings = pygettext.extract_genshi_strings
        messages = []
        options = {}
        for opt in ('include_attrs', 'ignore_tags'):
            val = config.get('genshi.i18n.' + opt)
            if val:
                options[opt] = val

        for fname in files:
            print "Working on", fname
            for msg in extract_strings(fname, options or None):
                # Genshi 0.6 adds comments as additional 4th element of msg,
                # so we take care to stay compatible
                lineno, text = msg[0], msg[2]
                if text:
                    if isinstance(text, tuple): # e.g. for ngettext
                        for subtext in text:
                            if subtext:
                                messages.append((lineno, fname, subtext))
                    else:
                        messages.append((lineno, fname, text))

        self._write_potfile_entries(potfile, messages)

    def scan_kid_files(self, potfile, files):
        """Extract strings from Genshi templates and write to pot file."""

        # XXX: This duplicates functionality already present in
        #   turbogears.i18n.pygettext! This should be refactored.
        messages = []
        tags_to_ignore = ['script', 'style']
        keys = []

        def process_text(is_attribute, k, tag):
            key = None
            s = _py_i18n_re.search(k)
            if s:
                key = (s.group(1) or s.group(2) or '').strip()
            elif not is_attribute:
                # we don't have a kid expression in there, so it is
                # "just" a text entry - which we want to be translated!
                import kid.codewriter as cw
                parts = cw.interpolate(k)
                if isinstance(parts, list) and len(parts) > 1:
                    print "Warning: Mixed content in tag <%s>: %s" % (tag, k)
                elif isinstance(parts, basestring):
                    key = k.strip()
            if key and key not in keys and tag not in tags_to_ignore:
                messages.append((tag, fname, key))
                keys.append(key)

        for fname in files:
            print "Working on", fname
            tree = None
            fh = open(fname)
            try:
                tree = kid.document(fh)
            except Exception, e:
                fh.close()
                print "Skip %s: %s" % (fname, e)
                continue
            sentinel = None
            tag = None
            for ev, el in tree:
                if ev == kid.parser.START:
                    if not isinstance(el.tag, unicode):
                        # skip comments, processing instructions etc.
                        continue
                    if el.get('lang', None) is not None:
                        # if we have a lang-attribute, ignore this
                        # node AND all it's descendants.
                        sentinel = el
                        continue
                    # set the tag from the current one.
                    tag = re.sub('({[^}]+})?(\w+)', '\\2', el.tag)
                    if tag in ('script', 'style'):
                        # skip JavaScript, CSS etc.
                        sentinel = el
                        continue
                    # process the attribute texts
                    for attrib_text in el.attrib.values():
                        process_text(True, attrib_text, tag)
                elif ev == kid.parser.END:
                    if el is sentinel:
                        sentinel = None
                elif ev == kid.parser.TEXT:
                    if sentinel is None and el.strip():
                        process_text(False, el, tag)
            fh.close()
        self._write_potfile_entries(potfile, messages)

    def get_strings_in_js(self, fname):
        messages = []
        keys = []
        fh = open(fname)
        for i, line in enumerate(fh):
            s = _js_i18n_re.search(line.decode(self.options.js_encoding))
            while s:
                key = s.group(1) or s.group(2)
                pos = s.end()
                if key and key not in keys:
                    messages.append((i + 1, fname, key))
                    keys.append(key)
                s = _js_i18n_re.search(line, pos)
        fh.close()
        return keys, messages

    def scan_js_files(self, potfile, files):
        messages = []
        keys = []
        for fname in files:
            print "Working on", fname
            k, m = self.get_strings_in_js(fname)
            keys.extend(k)
            messages.extend(m)
        self._write_potfile_entries(potfile, messages)

    def _write_potfile_entries(self, potfile, messages):
        if messages:
            fd = open(potfile, 'at+')
            for linenumber, fname, text in messages:
                if text:
                    text = catalog.normalize(text.encode('utf-8'))
                    fd.write('#: %s:%s\n' % (fname, linenumber))
                    fd.write('msgid %s\n' % text)
                    fd.write('msgstr ""\n\n')
            fd.close()

    def get_potfile_path(self):
        return os.path.join(self.locale_dir, '%s.pot' % self.domain)

    def get_locale_catalog(self, code):
        return os.path.join(self.locale_dir, code, 'LC_MESSAGES',
            '%s.po' % self.domain)

    def list_message_catalogs(self):
        files = []
        for name in glob.glob(self.locale_dir + '/*'):
            if os.path.isdir(name):
                fname = os.path.join(name, 'LC_MESSAGES', '%s.po' % self.domain)
                if os.path.isfile(fname):
                    files.append(fname)
        return files

    def fix_tzinfo(self, potfile):
        """Fix tzinfo.

        In certain enviroments, tzinfo as formatted by strftime() is not utf-8,
        e.g. Windows XP with Russian MUL.

        This leads to later error when a program trying to read catalog.

        """
        fh = open(potfile, 'rb')
        data = fh.read()
        fh.close()
        def repl(m):
            """Remove tzinfo if it breaks encoding."""
            tzinfo = m.group(2)
            try:
                tzinfo.decode('utf-8')
            except UnicodeDecodeError:
                return m.group(1) # cut tz info
            return m.group(0) # leave unchanged
        data = re.sub(
            "(POT-Creation-Date: [\d-]+ [0-9:]+)\+([^\\\\]+)", repl, data)
        fh = open(potfile, 'wb')
        fh.write(data)
        fh.close()


def main():
    tool = InternationalizationTool()
    tool.run()


if __name__ == '__main__':
    main()
