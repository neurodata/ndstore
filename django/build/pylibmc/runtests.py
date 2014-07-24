# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
"""Run nosetests with build/lib.* in sys.path"""

# Fix up sys.path so as to include the correct build/lib.*/ directory.
import sys
from distutils.dist import Distribution
from distutils.command.build import build

build_cmd = build(Distribution({"ext_modules": True}))
build_cmd.finalize_options()
lib_dirn = build_cmd.build_lib
sys.path.insert(0, lib_dirn)

# Dump info plugin stuff
import nose
import logging
from nose.plugins import Plugin

logger = logging.getLogger("nose.plugins.pylibmc")

def dump_infos():
    logger.info("injected path: %s", lib_dirn)
    import pylibmc, _pylibmc
    if hasattr(_pylibmc, "__file__"):
        logger.info("loaded _pylibmc from %s", _pylibmc.__file__)
        if not _pylibmc.__file__.startswith(lib_dirn):
            logger.warn("double-check the source path")
    else:
        logger.warn("static _pylibmc: %s", _pylibmc)
    logger.info("libmemcached version: %s", _pylibmc.libmemcached_version)
    logger.info("pylibmc version: %s", _pylibmc.__version__)
    logger.info("support compression: %s", _pylibmc.support_compression)
    logger.info("support sasl auth: %s", _pylibmc.support_sasl)

class PylibmcVersionDumper(Plugin):
    name = "info"
    enableOpt = "info"

    def __init__(self):
        Plugin.__init__(self)

    def begin(self):
        dump_infos()

if __name__ == "__main__":
    nose.main(addplugins=[PylibmcVersionDumper()])
