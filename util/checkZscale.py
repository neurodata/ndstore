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

"""
  This file is used to check the zscale and cubedimensions for a dataset. 
  Enter the dataset name and let it run.
"""

import os
import sys
import argparse

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest

def main():

  parser = argparse.ArgumentParser( description='Check the zscale for the dataset')
  parser.add_argument('dataset', action="store", help='Dataset name for the project')

  result = parser.parse_args()

  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.dataset )
  ( xcubedim, ycubedim, zcubedim ) = proj.datasetcfg.cubedim [ 0 ]
  for res in proj.datasetcfg.resolutions:
    print "Resolution ", res, "Zscale ", proj.datasetcfg.zscale[res], "Dims ", proj.datasetcfg.cubedim[res]
  

if __name__ == "__main__":
  main()
