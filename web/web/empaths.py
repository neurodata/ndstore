#
# Code to load project paths
#

import os, sys

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_UTIL_PATH = os.path.join(EM_BASE_PATH, "util" )
EM_CUTOUT_PATH = os.path.join(EM_BASE_PATH, "cutout" )
EM_ANNOTATE_PATH = os.path.join(EM_BASE_PATH, "annotate" )
EM_DBCONFIG_PATH = os.path.join(EM_BASE_PATH, "dbconfig" )

sys.path += [ EM_UTIL_PATH, EM_DBCONFIG_PATH, EM_ANNOTATE_PATH, EM_CUTOUT_PATH ]

