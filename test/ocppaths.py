#
# Code to load project paths
#

import os, sys

OCP_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
OCP_UTIL_PATH = os.path.join(OCP_BASE_PATH, "util" )
OCP_OCPCA_PATH = os.path.join(OCP_BASE_PATH, "ocpca" )

sys.path += [ OCP_UTIL_PATH, OCP_OCPCA_PATH ]

