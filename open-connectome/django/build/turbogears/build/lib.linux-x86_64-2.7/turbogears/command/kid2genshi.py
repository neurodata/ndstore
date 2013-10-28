"""Command for converting Kid to Genshi templates.

Currently only converts the Kid namespace and simple py:extend directives.

"""

import optparse
import os
import re

from turbogears.util import get_package_name


class Kid2Genshi(object):
    """Convert Kid to Genshi templates."""

    desc = "Convert all Kid templates in the project to Genshi"

    engines = ('Kid', 'Genshi')
    extensions = ('.kid', '.html')
    xmlns = ('http://purl.org/kid/ns#', 'http://genshi.edgewall.org/')

    need_project = True

    def __init__(self, version):
        parser = optparse.OptionParser(
            usage="%prog kid2genshi [options]",
            version="%prog " + version)
        parser.add_option("-f", "--force",
            help="overwrite existing templates",
            action='store_true', dest="force")
        parser.add_option("-k", "--keep",
            help="keep the original templates",
            action='store_true', dest="keep")
        parser.add_option("-r", "--reverse",
            help="convert Genshi to Kid",
            action='store_true', dest="reverse")
        self.parser = parser

    def convert_template(self, filename, force=False, keep=False):
        extensions = self.extensions
        from_index, to_index = self.from_index, self.to_index
        if not force and os.path.exists(filename + extensions[to_index]):
            return
        f = open(filename + extensions[from_index], 'rb')
        try:
            try:
                old = f.read()
            finally:
                f.close()
        except IOError:
            print "Could not open", filename
            return False
        new = old
        for n, r in enumerate(self.re_convert):
            new = r[0].sub(r[1], new, 1)
            if not n and new == old:
                return
        print "Converting", filename, "..."
        f = open(filename + extensions[to_index], 'wb')
        try:
            f.write(new)
        finally:
            f.close()
        if not keep:
            os.unlink(filename + extensions[from_index])
            if self.engines[from_index] == 'Kid':
                try:
                    os.unlink(filename + '.pyc')
                except OSError:
                    pass
                try:
                    os.unlink(filename + '.pyo')
                except OSError:
                    pass
        return True

    def change_config(self, filename):
        f = open(filename, 'rb')
        try:
            try:
                old = f.read()
            finally:
                f.close()
        except IOError:
            print "Could not open", filename
            return False
        new_defaultview = r'\1%s\2' % self.engines[self.to_index].lower()
        new = self.re_defaultview.sub(new_defaultview, old, 1)
        if new == old:
            return
        print "Changing", filename, "..."
        f = open(filename, 'wb')
        try:
            f.write(new)
        finally:
            f.close()
        return True

    def run(self):
        options, args = self.parser.parse_args()
        force, keep, reverse = options.force, options.keep, options.reverse
        from_index, to_index = 0, 1
        if reverse:
            from_index, to_index = to_index, from_index
        self.from_index, self.to_index = from_index, to_index
        engines, extensions, xmlns = self.engines, self.extensions, self.xmlns
        package_name = get_package_name()
        convert = [(r'<([a-z]+)\b([^<]*\bxmlns:py\s*=\s*[\'"])'
            r'%s([\'"][^<]*>.*</\1)>' % xmlns[from_index],
            r"<\1\2%s\3>" % self.xmlns[to_index])]
        if reverse:
            convert.append((r'<([a-z]+)\b([^<]*)\b'
                r'xmlns:xi(\s*=\s*")http://www.w3.org/2001/XInclude'
                r'("[^<]*>)\s*<xi:include\s+href=[\'"]'
                r'([^\'"]*)\.html[\'"]/>(.*</\1)>',
                r"<\1\2py:extends\3'\5.kid'\4\6>"))
        else:
            convert.append((r'<([a-z]+)\b([^<]*)\b'
                r'py:extends(\s*=\s*")\'([^\'"]*)\.kid\'("[^<]*>)(.*</\1)>',
                r'<\1\2xmlns:xi\3http://www.w3.org/2001/XInclude\5'
                r'<xi:include href="\4.html"/>\6>'))
        # we could append more conversion rules here
        self.re_convert = [(re.compile(r[0], re.S), r[1]) for r in convert]
        self.re_defaultview = re.compile(
            r'^(\s*tg.defaultview\s*=\s*[\'"])(?:%s)([\'"]\s*(?:#.*)?)$'
                % engines[from_index].lower(), re.M)
        print "Converting all %s to %s templates in package %s" % (
            engines[from_index], engines[to_index], package_name)
        print "(the %s templates will be %s) ..." % (engines[from_index],
            keep and 'kept' or 'removed')
        n = 0
        for dirpath, dirnames, filenames in os.walk(package_name):
            i = 0
            while i < len(dirnames):
                dirname = dirnames[i]
                if dirname.startswith('.') or dirname.endswith('~'):
                    del dirnames[i]
                else:
                    i += 1
            for filename in filenames:
                if filename.endswith('~'):
                    continue
                name, ext = os.path.splitext(filename)
                if ext == extensions[from_index]:
                    filename = os.path.join(dirpath, name)
                    if self.convert_template(filename, force, keep):
                        n += 1
        if n:
            if n > 1:
                print "%d %s templates have been converted to %s." % (
                    n, engines[from_index], engines[to_index])
            print "Changing the configuration of package %s ..." % package_name
            if not self.change_config(
                    os.path.join(package_name, 'config', 'app.cfg')):
                print "Application config with defaultview setting not found."
        elif force:
            print "No %s templates were found in the current project." % (
                engines[from_index])
        else:
            print "No %s templates needed to be converted in this project." % (
                engines[from_index])
