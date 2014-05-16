# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
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
import shutil

import sys

inputdir = '/data/scratch/bumbarger13/series14'
outputdir = '/data/EM/bumbarger13/series14'

#
#  Customize ingest script to turn the output of TrackEM export 
#  into OCP-naming-convention CATMAID stack.
#


# Highest resolution: 
highres = 5  # 5 down to 0

# Active tiles at resolution 0
xtiles = 160
ytiles = 160

# Slices to ingest [first,last]
# RB check that these are correct
slices = [0,10]

# build the directories
for res in range(highres,-1,-1):

  #outer directory is resolution
  dirname = "%s/%s" % ( outputdir, res )
  if not os.path.exists ( dirname ):
    os.mkdir ( dirname )

  #inner directory is slicenumber
  for slice in range(slices[0],slices[1]+1):
    dirname = "%s/%s/%s" % ( outputdir, res, slice )
    if not os.path.exists ( dirname ):
      os.mkdir ( dirname )


# Now rename the files.
for res in range(highres,-1,-1):
  for slice in range(slices[0],slices[1]+1):

    # xtiles and ytiles at this resolution
    xrestiles = (xtiles-(2**res))/(2**res)+1
    yrestiles = (ytiles-(2**res))/(2**res)+1

    #print "Tiles %s by %s at resolution %s" % (xrestiles,yrestiles,res)

    for ytile in range(yrestiles):
      for xtile in range(xrestiles):

        infile = "%s/%s/%s_%s_%s.png" % ( inputdir, slice, ytile, xtile, res )
        outfile = "%s/%s/%s/%s_%s.png" % ( outputdir, res, slice, ytile, xtile )
  
        try:
          if not os.path.exists(outfile):
            print "Copying %s to %s" % ( infile, outfile )
            shutil.copy ( infile, outfile )
#          else: 
#            print "Found %s" % ( outfile )
        except:
          print "Missing file %s" % ( infile )
