import logging
import sys
import StringIO

import turbogears
import pkg_resources
from turbogears import controllers, expose
from code import InteractiveConsole


log = logging.getLogger('turbogears.toolbox')


class WebConsole(controllers.RootController):
    """Web based Python interpreter"""

    __label__ = 'WebConsole'

    icon = "/tg_static/images/shell.png"

    def __init__(self, width=80):
        self.console = None

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '

    @expose()
    def process_request(self, line):
        more, output = self._process_request(line)
        return dict(more=more, output=output)

    @expose()
    def process_multiline_request(self, block):
        outlines = []

        lines = [line for line in block.split('\n')]

        for line in lines:
            more, output = self._process_request(line)

            if output[-1] == '\n':     # we'll handle the newlines later.
                output = output[:-1]

            outlines.append(output)

        return dict(more=more, output='\n'.join(outlines))

    def _process_request(self, line):
        if len(self.console.buffer):
            prompt = sys.ps2
        else:
            prompt = sys.ps1

        myout = StringIO.StringIO()

        output = "%s%s" % (prompt, line)
        # hopefully Python doesn't interrupt in this block
        # lest we'll get some curious output.
        try:
            sys.stdout = myout
            sys.stderr = myout
            more = self.console.push(line)
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        stdout = myout.getvalue()

        if stdout:
            output = '%s\n%s' % (output, stdout)

        return more, output.rstrip()

    def new_console(self):
        data = dict()
        locs = dict(__name__='tg-admin', __doc__=None,
            reload_console=self.new_console)
        try:
            mod = turbogears.util.get_model()
            if mod:
                locs.update(mod.__dict__)
        except (pkg_resources.DistributionNotFound, ImportError):
            import traceback
            error = "Error: could not load data model.\n"
            data['errors'] = [error]
            error += traceback.format_exc()
            log.warn(error)
        self.console = InteractiveConsole(locals=locs)
        return data

    @expose('turbogears.toolbox.console')
    def index(self):
        data = dict()
        if not self.console:
            data.update(self.new_console())
        return data
