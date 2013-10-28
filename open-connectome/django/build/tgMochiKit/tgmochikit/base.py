import pkg_resources

import os
import glob
import logging

logger = logging.getLogger(".".join(__name__.split(".")[:-1]))

VERSION = '1.3.1'

INITIALIZED = False
PACKED = False #True
XHTML = False
SUBMODULES = []
PATHS = []
DRAGANDDROP = False

def init(register_static_directory, config={}, version=None, packed=None, xhtml=None, draganddrop=None):
    """Initializes the MochiKit resources.

    The parameter register_static_directory is somewhat hackish: because this
    init is called during initialization of turbogears.widgets itself,
    register_static_directory isn't importable. So we need to pass it as
    argument.

    """
    global INITIALIZED, PACKED, XHTML, PATHS, VERSION, DRAGANDDROP
    if not INITIALIZED:
        if version is not None:
            VERSION = version
        if packed is not None:
            PACKED = packed
        if xhtml is not None:
            XHTML = xhtml
        if draganddrop is not None:
            DRAGANDDROP = draganddrop
        INITIALIZED = True
        PACKED = config.get('tg_mochikit.packed', PACKED)
        VERSION = config.get('tg_mochikit.version', VERSION)
        XHTML = config.get('tg_mochikit.xhtml', XHTML)
        DRAGANDDROP = config.get('tg_mochikit.draganddrop', DRAGANDDROP)

        is_131 = '1.3.1' in VERSION
        js_base_dir = pkg_resources.resource_filename("tgmochikit",
            "static/javascript/")
        # we check for all the versions in the js_base_dir and fetch the
        # one that matches best. If several candidates exist, the best is the latest.
        if os.path.exists(os.path.join(js_base_dir, VERSION)):
            js_dir = os.path.join(js_base_dir, VERSION)
        else:
            candidates = glob.glob(os.path.join(js_base_dir, "%s*" % VERSION))
            candidates.sort()
            js_dir = candidates[-1]
        logger.info("MochiKit version chosen: %s", os.path.basename(js_dir))
        path = os.path.join(js_dir, "unpacked", "*.js")
        for name in glob.glob(path):
            module = os.path.basename(name)
            if not "__" in name and not "MochiKit" in module:
                SUBMODULES.append(module)
        register_static_directory("tgmochikit", js_dir)

        if PACKED:
            PATHS = ["packed/MochiKit/MochiKit.js"]
        else:
            res = ["unpacked/MochiKit.js"]
            if XHTML:
                for submodule in SUBMODULES:
                    res.append("unpacked/%s" % submodule)
            PATHS = res
        if DRAGANDDROP and not is_131:
            PATHS.append("unpacked/DragAndDrop.js")

def get_paths():
    return PATHS


def get_shipped_versions():
    js_base_dir = pkg_resources.resource_filename("tgmochikit",
                                                  "static/javascript/")
    return [os.path.basename(p) for p in glob.glob(os.path.join(js_base_dir, "*"))]
    
