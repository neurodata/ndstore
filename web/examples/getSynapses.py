import urllib2
import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys

from scipy.sparse import lil_matrix, csc_matrix

import zindex
import empaths
import annrest
import annproj
import anndb



def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')

  result = parser.parse_args()


  # Obtain the annotation project and dbconfiguration
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( result.token )
  dbcfg = annrest.switchDataset ( annoproj )

  # And the annotations DB
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )

  # Get the relevant dimensions
  resolution = annoproj.getResolution()
  [ximagesz, yimagesz] = dbcfg.imagesz [ resolution]
  [xcubedim, ycubedim, zcubedim] = dbcfg.cubedim [resolution ]
  [ startslice, endslice ] = dbcfg.slicerange
  slices = endslice - startslice + 1

  # round up to the next largest slice
  if slices % zcubedim != 0 :
    slices = ( slices / zcubedim + 1 ) * zcubedim

  # Set the limits on the number of cubes in each dimension
  xlimit = ximagesz / xcubedim
  ylimit = yimagesz / ycubedim
  zlimit = slices / zcubedim

  # Iterate over all the cells in the database
  for key in zindex.generator ( [xlimit, ylimit, zlimit] ):

    print key

    anncube = annodb.getCube ( key )

    # mask out the relevant ids
#    vec_func = np.vectorize ( lambda x: x if x == result.annid else 0 )    
    vec_func = np.vectorize ( lambda x: x if x != 0 else 0 )    
    anndata = vec_func ( anncube.data )

    indices = anndata.nonzero()

    print indices[0]
#    sys.exit(0)

    

if __name__ == "__main__":
      main()



