#
# Code to load project paths
#

import os, sys

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_UTIL_PATH = os.path.join(EM_BASE_PATH, "util" )

sys.path += [ EM_UTIL_PATH ]

