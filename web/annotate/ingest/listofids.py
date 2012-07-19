import argparse
import sys
import os

import empaths
import annproj
import dbconfig
import anndb

import zindex

import numpy as np
import cStringIO
import collections

import ann_cy

#
#  ingest the PNG files into the database
#

"""Output an entire list of points for a given annotation"""


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution of the ingest data.')
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  
  result = parser.parse_args()

  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( result.token )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )

  # Bind the annotation database
  annoDB = anndb.AnnotateDB ( dbcfg, annoproj )

  zidxs = annoDB.annoIdx.getIndex ( result.annid, result.resolution )
  
  print zidxs

  allvoxels = []

  total = 0

  for zidx in zidxs:

    cb = annoDB.getCube ( zidx, result.resolution ) 

    # mask out the entries that do not match the annotation id
    vec_func = np.vectorize ( lambda x: result.annid if x == result.annid else 0 )
    annodata = vec_func ( cb.data )
    
    # where are the entries
    offsets = np.nonzero ( annodata ) 
    voxels = zip ( offsets[2], offsets[1], offsets[0] ) 

    # Get cube offset information
    [x,y,z]=zindex.MortonXYZ(zidx)
    xoffset = x * dbcfg.cubedim[result.resolution][0] 
    yoffset = y * dbcfg.cubedim[result.resolution][1] 
    zoffset = z * dbcfg.cubedim[result.resolution][2] + dbcfg.slicerange[0]

    total += len(voxels)
    print "Found %s voxels" % len(voxels)
    print "Total so far %s " % total

    [ allvoxels.append([a+xoffset, b+yoffset, c+zoffset]) for (a,b,c) in voxels ] 
    
  print "Total %s compared to list length %s" % ( total, len(allvoxels))


if __name__ == "__main__":
  main()

