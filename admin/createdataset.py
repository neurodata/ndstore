# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj

def main():

  parser = argparse.ArgumentParser(description='Create a new dataset.')
  parser.add_argument('dsname', action="store", help='Name of the dataset')
  parser.add_argument('ximagesize', type=int, action="store")
  parser.add_argument('yimagesize', type=int, action="store")
  parser.add_argument('startslice', type=int, action="store")
  parser.add_argument('endslice', type=int, action="store")
  parser.add_argument('zoomlevels', type=int, action="store")
  parser.add_argument('zscale', type=float, action="store", help='Relative resolution between x,y and z')

  result = parser.parse_args()

  # Get database info
  pd = ocpcaproj.OCPCAProjectsDB()

  pd.newDataset ( result.dsname, result.ximagesize, result.yimagesize, result.startslice, result.endslice, result.zoomlevels, result.zscale )


if __name__ == "__main__":
  main()


  
