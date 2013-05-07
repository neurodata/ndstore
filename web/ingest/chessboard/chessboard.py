import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
from PIL import Image

import empaths
import emcaproj
import emcadb

import proteins


#assume a 0 resolution level for now for ingest
RESOLUTION = 0

def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
  parser.add_argument('token', action="store" )
  parser.add_argument('path', action="store" )

  result = parser.parse_args()

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.loadProject ( result.token )

  _ximgsz = proj.datasetcfg.imagesz[0]
  _yimgsz = proj.datasetcfg.imagesz[1]
  startslice = proj.datasetcfg.slicerange[0]
  endslice = proj.datasetcfg.slicerange[1]

  alldirs = os.listdir ( result.path )

  # for each protein
  for prot in proteins.proteins:

    # this finds the highest run (number suffix) for each channel
    pdir = None
    for x in alldirs:
      m = re.match('{0}.*(\d+)$'.format(prot),x)
      if m != None:
        if pdir == None:
          pdir = x
          run = m.group(1)
        else:
          if m.group(1) > run:
            pdir = x

    if pdir:
      # for each slice
      for sl in range(startslice,endslice+1):

        # open the slice file and ingest
        filenm = result.path + '/' + pdir + '/' + pdir + '-S' + '{:0>3}'.format(sl) + '.tif'

        f = open ( filenm, "r" )
        if f:
          print "Found" + filenm



      
  

if __name__ == "__main__":
  main()

