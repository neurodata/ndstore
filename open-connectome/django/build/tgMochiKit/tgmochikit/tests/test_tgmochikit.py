import sys
import glob
import os
import logging
import cStringIO as StringIO

import tgmochikit as tgm
import tgmochikit.base as tgm_base


tgm_logger = logging.getLogger("tgmochikit")

def fake_register_static_directory(name, path):
    pass

def test_version_131():
    VERSION = "1.3.1"

    # unpacked, xhtml
    reload(tgm_base)
    tgm.init(fake_register_static_directory, version=VERSION, packed=False, xhtml=True)
    paths = tgm.get_paths()
    assert len(paths) > 1, "We expect several paths because xhtml was True"
    for p in paths:
        assert "unpacked" in p

    # unpacked, no xhtml
    reload(tgm_base)
    tgm.init(fake_register_static_directory, version=VERSION, packed=False, xhtml=False)
    paths = tgm.get_paths()    
    assert len(paths) == 1, "We expect one path because xhtml was False: %r" % paths


    # packed, xhtml
    reload(tgm_base)
    tgm.init(fake_register_static_directory, version=VERSION, packed=True, xhtml=True)
    paths = tgm.get_paths()
    assert len(paths) == 1, "We expect one path because packed was True: %r" % paths
    for p in paths:
        assert "packed" in p

    # packed, no xhtml
    reload(tgm_base)
    tgm.init(fake_register_static_directory, version=VERSION, packed=True, xhtml=False)
    paths = tgm.get_paths()
    assert len(paths) == 1, "We expect one path because packed was True: %r" % paths
    
    # packed, draganddrop

    reload(tgm_base)
    tgm.init(fake_register_static_directory, version=VERSION, packed=True, xhtml=False, draganddrop=True)
    paths = tgm.get_paths()
    assert len(paths) == 1, "We expect one path because draganddrop is ignored in 1.3.1: %r" % paths


def gen_bits(num):
    if num == 1:
        yield False,
        yield True,
    else:
        for bits in gen_bits(num-1):
            yield (False,) + bits
            yield (True,) + bits
            
def test_all_14_versions():
    static_path = []
    
    def register_static_directory(name, path):
        static_path.append(path)

    known_14_versions = [os.path.basename(p) for p in glob.glob(os.path.join(os.path.dirname(__file__), "..", "static", "javascript", "1.4*"))]
    known_14_versions.sort()
    tgm_logger.setLevel(logging.INFO)
    for version in known_14_versions:
        print "testing version: %s" % version
        for packed, xhtml, draganddrop in gen_bits(3):
            print "packed: %r, xhtml: %r, draganddrop: %r" % (packed, xhtml, draganddrop)
            buffer = StringIO.StringIO()
            handler = logging.StreamHandler(buffer)
            tgm_logger.addHandler(handler)

            reload(tgm_base)
            tgm.init(register_static_directory, version=version, packed=packed, xhtml=xhtml, draganddrop=draganddrop)
            base_path = static_path[-1]
            static_path[:] = []
            assert version == os.path.basename(base_path)
            paths = tgm.get_paths()
            print "paths:", paths
            # if we have DnD, we filter out the DnD-path, as it confuses packed/unpacked testing logic
            if draganddrop:
                new_paths = [p for p in paths if not "DragAndDrop" in p]
                assert new_paths != paths, new_paths
                paths = new_paths
            if packed:
                for p in paths:
                    assert "unpacked" not in p, p
            else:
                for p in paths:
                    assert "unpacked" in p, p
                # only if we aren't packed xhtml will include several files
                if xhtml:
                    assert len(paths) > 1, paths
            tgm_logger.removeHandler(handler)
            assert version == buffer.getvalue().strip().split(" ")[-1]



def test_get_shipped_versions():
    print tgm.get_shipped_versions()
