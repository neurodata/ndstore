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

#
# Code to load project paths
#

import os, sys

ND_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.." ))
ND_UTIL_PATH = os.path.join(ND_BASE_PATH, "util" )
ND_WEBSERVICE_PATH = os.path.join(ND_BASE_PATH, "webservices" )
ND_SPATIALDB_PATH = os.path.join(ND_BASE_PATH, "ndspatialdb" )
ND_DJANGO_PATH = os.path.join(ND_BASE_PATH, "django" )

sys.path += [ ND_UTIL_PATH, ND_PROJ_PATH, ND_WEBSERVICE_PATH, ND_SPATIALDB_PATH, ND_RAMON_PATH, ND_LIB_PATH, ND_DJANGO_PATH ]
