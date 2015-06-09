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

import os
import sys
import urllib2
import argparse
import time
import multiprocessing as mp
import glob
from sets import Set

"""

  A simple test which finds the missing slices for mitra's data. 

"""

def main():

  parser = argparse.ArgumentParser(description="Run the simple test")
  parser.add_argument('path', action="store", help="Target Data Location")
  result = parser.parse_args()
  
  fileList = glob.glob(result.path+'/*.tiff')
  newFileList = Set([])
  keyFileList = Set(range(0,280))

  for name in fileList:
    fileNumber = int( name.split('/')[6].split('.')[0] )
    newFileList.add( fileNumber )

  print keyFileList.difference( newFileList ) 


if __name__ == "__main__":
  main()
