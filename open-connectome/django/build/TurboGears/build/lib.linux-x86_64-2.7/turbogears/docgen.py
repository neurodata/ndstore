import os
import time
from glob import glob
from setuptools import Command
import pkg_resources
pkg_resources.require('Kid >= 0.6.4')
import kid
import re
from distutils import log


class GenSite(Command):
    """setuptools command to generate the TurboGears website"""

    user_options = [
        ('srcdirs=', 's', "directories containing the source files (default: docs)"),
        ('destdir=', 'd', "destination output directory (default: dist/site)"),
        ('encoding=', 'e', "encoding for output (default: utf-8)"),
        ('force', 'f', "regenerate all files"),
        ('ignoredirs=', 'i', "directories to ignore (default: ['.svn', '.cvs'])"),
        ('ignorefiles=', 'x', "files to ignore (default: ['.*\\.pyc', '.DS_Store'])"),
        ('nodelete=', 'l', "directories to leave alone rather than delete"),
        ('templates=', 't', "mapping of templates to load (format: name=templatefile,name=templatefile)"),
        ('copydirs=', 'c', "copy files from these directories without template proc. (destdir=srcdir,...)"),
        ('noprintable', 'N', "don't make printable version of tutorials"),
        ('eggdir=', 'g', "which directory has the eggs in it (default: '../thirdparty/eggs')")
    ]

    boolean_options = ['force']

    srcdirs = None
    destdir = 'dist/site'
    encoding = 'utf-8'
    force = False
    ignoredirs = None
    ignorefiles = None
    nodelete = None
    templates = None
    copydirs = None
    eggdir = '../thirdparty/eggs'
    noprintable = False

    def initialize_options(self):
        pass

    def finalize_options(self):
        if self.srcdirs is None:
            self.srcdirs = ['docs']
        if self.srcdirs == '':
            self.srcdirs = []
        self.ensure_string_list('srcdirs')
        self.ensure_string('destdir', 'dist/site')
        self.ensure_string('encoding', 'utf-8')
        if self.ignoredirs is None:
            self.ignoredirs = ['.svn', '.cvs']
        self.ensure_string_list('ignoredirs')
        if self.ignorefiles is None:
            self.ignorefiles = ['.*\\.pyc', '.DS_Store']
        if self.nodelete is None:
            self.nodelete = ['dist/site/preview']
        self.ensure_string_list('nodelete')
        self.ensure_string_list('ignorefiles')

        regexes = []
        for pat in self.ignorefiles:
            regexes.append(re.compile(pat))
        self.ignorepatterns = regexes

        self.templates, self.templates_order = self._split_mapping(self.templates, True)
        self.copydirs = self._split_mapping(self.copydirs)

    def _split_mapping(self, valToSplit, preserve_order=False):
        mapping = {}
        order = []
        if valToSplit and isinstance(valToSplit, basestring):
            pairs = re.split(',\s*', valToSplit)
            for pair in pairs:
                name, filename = re.split('\s*=\s*', pair)
                mapping[name] = os.path.abspath(filename)
                order.append(name)
        if preserve_order:
            return mapping, order
        return mapping

    def check_if_newer(self, src, dest):
        srcmtime = os.path.getmtime(src)
        if os.path.exists(dest):
            destmtime = os.path.getmtime(dest)
        else:
            destmtime = 0
        return srcmtime > destmtime

    def copy_if_newer(self, src, dest):
        if self.force or self.check_if_newer(src, dest):
            d = os.path.dirname(dest)
            if not os.path.exists(d):
                os.makedirs(d)
            self.copy_file(src, dest)

    def render_template(self, src, dest, depth):
        if not self.force and not self.check_if_newer(src, dest):
            return
        if not self.dry_run:
            log.info("rendering %s" % dest)
        else:
            log.info("skipping rendering %s" % dest)
            return

        template = kid.load_template(src, cache=False)
        template.Template.serializer = self.serializer
        toroot = '../' * depth
        destfile = dest[len(self.destdir)+1:]
        updated = time.strftime('%b %d, %Y', time.localtime(os.path.getmtime(src)))
        output = template.serialize(encoding=self.encoding, root=toroot, updated=updated,
            destfile=destfile, eggs=self.eggs)
        output = output.replace('$$', '$')
        destfile = open(dest, 'w')
        destfile.write(output)
        destfile.close()

    def update_site_files(self, srcdir, processTemplates = True, destroot=None):
        if not destroot:
            destroot = self.destdir
        for root, dirs, files in os.walk(srcdir):
            if root != srcdir:
                fromroot = root[len(srcdir)+1:]
                segments = fromroot.split(os.sep)
                if set(segments).intersection(self.ignoredirs):
                    continue
                depth = len(segments)
            else:
                fromroot = ''
                depth = 0
            destdir = os.path.join(destroot, fromroot)
            if not os.path.exists(destdir):
                if not self.dry_run:
                    log.info("creating directory %s" % (destdir))
                    os.makedirs(destdir)
                else:
                    log.info("skipping creating directory %s" % (destdir))

            for file in files:
                ignore = False
                abs = os.path.abspath(file)
                for pat in self.ignorepatterns:
                    if pat.match(file):
                        ignore = True
                        break
                if ignore:
                    continue

                for tempfile in self.templates.values():
                    if tempfile == abs:
                        ignore = True
                        break
                if ignore:
                    continue

                ext = os.path.splitext(file)[1]
                dest = os.path.join(destdir, file)
                self.currentfiles.add(dest)
                if not processTemplates or ext != '.html':
                    self.copy_if_newer(os.path.join(root, file),
                        dest)
                else:
                    self.render_template(os.path.join(root, file),
                        dest, depth)

    def delete_excess_files(self):
        for root, dirs, files in os.walk(self.destdir):
            leavealone = False
            for dirname in self.nodelete:
                if root.startswith(dirname):
                    leavealone = True
                    break
            if leavealone:
                continue
            for file in files:
                dest = os.path.join(root, file)
                if dest not in self.currentfiles:
                    if not self.dry_run:
                        log.info("deleting %s" % dest)
                        os.unlink(dest)
                    else:
                        log.info("skipping deleting %s" % dest)

    def run(self):
        destdir = self.destdir
        log.info("generating website to %s" % destdir)

        if not os.path.exists(destdir):
            log.info("creating %s" % destdir)
            os.makedirs(destdir)

        for name in self.templates_order:
            filename = self.templates[name]
            log.info("template %s loaded as %s" % (filename, name))
            kid.load_template(filename, name=name)

        if self.eggdir:
            if not self.eggdir.endswith('/'):
                self.eggdir += '/'
            choplen = len(self.eggdir)
            self.eggs = [fn[choplen:] for fn in glob(self.eggdir + '*')]
            self.eggs.sort()

        self.currentfiles = set()

        self.serializer = kid.HTMLSerializer(encoding=self.encoding)

        for d in self.srcdirs:
            self.update_site_files(d)
        for dest, src in self.copydirs.items():
            if os.path.isdir(src):
                self.update_site_files(src, processTemplates=False,
                    destroot=os.path.join(self.destdir, dest))
            else:
                destfile = os.path.join(self.destdir, os.path.normpath(dest))
                self.copy_if_newer(src, destfile)
                self.currentfiles.add(destfile)
        self.printable_tutorial()
        self.delete_excess_files()

    def printable_tutorial(self):
        if self.noprintable:
            return
        self._make_printable(os.path.join('docs', 'tutorials', 'wiki20'), 3)
        self._make_printable(os.path.join('docs', 'wiki20'))

    def _make_printable(self, tutdir, up_to_root=2):
        endpath = tutdir
        tutdir = os.path.join(self.srcdirs[0], tutdir)
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError: # Py < 2.5
            try:
                import cElementTree as ElementTree
            except ImportError: # no C implementation
                try:
                    from xml.etree import ElementTree
                except ImportError: # Py < 2.5
                    try:
                        from elementtree import ElementTree
                    except ImportError:
                        raise ImportError, "ElementTree not installed."

        masterdoc = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import printable ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="printable">
<head>
 <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
 <link rel="stylesheet" type="text/css" href="../../default.css" py:attrs="href=root+'default.css'"/>
 <link type="text/css" rel="stylesheet" href="../../sh/SyntaxHighlighter.css" py:attrs="href=root+'sh/SyntaxHighlighter.css'"></link>
 <title>TurboGears: 20 Minute Wiki Tutorial</title>
</head>
<body>
"""
        docs = os.listdir(tutdir)
        docs.sort()
        for doc in docs:
            if not doc.endswith('.html'):
                continue
            log.info("combining %s" % doc)
            tree = ElementTree.parse(os.path.join(tutdir, doc))
            body = tree.find("{http://www.w3.org/1999/xhtml}body")
            map(body.remove, body.findall("{http://www.w3.org/1999/xhtml}script"))
            bodytext = ElementTree.tostring(body)
            bodytext = bodytext.replace("</html:body>", "")
            bodytext = bodytext.replace('<html:body xmlns:html="http://www.w3.org/1999/xhtml">', "")
            masterdoc += bodytext

        masterdoc += """<script src="../../sh/shCore.js" py:attrs="src=root+'sh/shCore.js'"></script>
<script src="../../sh/shBrushPython.js" py:attrs="src=root+'sh/shBrushPython.js'"></script>
<script src="../../sh/shBrushXml.js" py:attrs="src=root+'sh/shBrushXml.js'"></script>
<script src="../../sh/shBrushJScript.js" py:attrs="src=root+'sh/shBrushJScript.js'"></script>
<script language="javascript">
        dp.SyntaxHighlighter.HighlightAll('code');
</script>
</body></html>"""
        masterdoc = masterdoc.replace('html:', '')
        template = kid.Template(source=masterdoc, root='../' * up_to_root)
        template.serializer = self.serializer

        destend = os.path.join(self.destdir, endpath)
        if not os.path.exists(destend):
            os.makedirs(destend)
        outfn = os.path.join(destend, 'printable.html')
        print "combined output: %s" % outfn
        outfile = open(outfn, 'w')
        masterdoc = template.serialize(encoding=self.encoding)
        masterdoc = masterdoc.replace('$${', '${')
        outfile.write(masterdoc)
        outfile.close()
        self.currentfiles.add(outfn)
