# Copyright 2014 NeuroData (http://neurodata.io)
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
import argparse
import glob
import subprocess

import pdb

"""
  This is a script to convert jp2 to png for Mitra's Data. \
  We use Kakadu software for this script. Kakadu only runs on Ubuntu \
  and has to have the library added to shared path.
"""

def main():
  
  parser = argparse.ArgumentParser(description='Convert JP2 to PNG')
  parser.add_argument('path', action="store", help='Directory with JP2 Files')
  parser.add_argument('location', action="store", help='Directory to write to')

  result = parser.parse_args()

  # Reading all the jp2 files in that directory
  filelist = glob.glob(result.path+'*.jp2')
 
  for name in filelist:
    
    print "Opening: {}".format( name )
    
    # Identifying the subdirectory to place the data under
    if name.find('F') != -1:
      subfile = 'F/'
    elif name.find('IHC') != -1:
      subfile = 'IHC/'
    elif name.find('N') != -1:
      subfile = 'N/'
    # Determine the write location of the file. This was /mnt on datascopes
    writelocation =  result.location+subfile+name.split(result.path)[1].split('_')[3].split('.')[0]
    # Call kakadu expand from the command line, specify the input and the output filenames
    subprocess.call( [ './kdu_expand' ,'-i', '{}'.format(name), '-o', '{}.tiff'.format(writelocation) ] )

if __name__ == "__main__":
  main()
