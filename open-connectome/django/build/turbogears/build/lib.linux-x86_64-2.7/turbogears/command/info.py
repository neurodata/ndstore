"""Commands for listing TurboGears default and extension packages info"""

try:
    from email.parser import Parser
except ImportError: # Python < 2.5
    from email.Parser import Parser

import pkg_resources

entrypoints = {
    'tg-admin Commands' : 'turbogears.command',
    'Template Engines' : 'python.templating.engines',
    'Widget Packages' : 'turbogears.widgets',
    'TurboGears Extensions' : 'turbogears.extensions',
    'Identity Providers' : 'turbogears.identity.provider',
    'Visit Managers' : 'turbogears.visit.manager',
    'Toolbox Gadgets' : 'turbogears.toolboxcommand'}

parsestr = Parser().parsestr

def retrieve_pkg_info(distribution):
    """Retrieve parsed package info from distribution."""
    return parsestr(distribution.get_metadata('PKG-INFO'))


def retrieve_url(distribution):
    """Retrieve URL from distribution."""
    try:
        info = retrieve_pkg_info(distribution)
    except Exception:
        url = None
    else:
        url = info['Home-page'] or info['Url']  or info['Download-Url']
    return url


def add_link(distribution):
    """Add link to distribution."""
    info = str(distribution)
    url = retrieve_url(distribution)
    if url:
        info = str(info).split(None, 1)
        info[0] = '<a href="%s">%s</a>' % (url, info[0])
        info = ' '.join(info)
    return info


def retrieve_info(with_links=False):
    """Retrieve default and extension packages info."""
    format = with_links and add_link or str
    # get default packages
    packages = [format(pkg) for pkg in pkg_resources.require('Turbogears')]
    # get extension packages
    plugins = {}
    for name, pointname in entrypoints.items():
        plugins[name] = ['%s (%s)' % (entrypoint.name, format(entrypoint.dist))
            for entrypoint in pkg_resources.iter_entry_points(pointname)]
    return packages, plugins


class InfoCommand:
    """Shows version info for debugging."""

    desc = "Show version info"

    def __init__(self,*args, **kwargs):
        pass

    def run(self):
        print """TurboGears Complete Version Information

TurboGears requires:
"""
        packages, plugins = retrieve_info()
        seen_packages = set()
        for p in packages:
            if p not in seen_packages:
                print '*', p
                seen_packages.add(p)
        for name, pluginlist in plugins.items():
            print '\n', name, '\n'
            for plugin in pluginlist:
                print '*', plugin
