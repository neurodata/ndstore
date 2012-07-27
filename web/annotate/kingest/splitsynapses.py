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
import itertools

import annotation
import anndb
import h5ann

from pprint import pprint

#
#  ingest the PNG files into the database
#
"""Currently this script is broken in the following ways.  If synapses extend more 
     than +/- 128 beyond their seed point the script goes into debug mode.  This found 
     voxels are skipped.  They may be relabelled from another seed point or they may not 
     be relabelled at all.  This is the "dont store" stuff.

     If synapses are with 128 pixels of the boundary.  They will throw an exception.
     If synapses are not in 2-d xy plane only, they will get split.
     
     Run this only with databases that you have backed up because if the script
     fails it will leave the database in an inconsistent state.
     
     Use mysqldump to create a backup.  Run and if you get an error, restore your
     database and have Randal write a better script.  If it runs to completion, 
     the data are good modulo the 2-d assumption."""

"""Output an entire list of points for a given annotation"""

class SynapseRewriter:
  """Rewrites synapses from old values to separate objects"""

  def __init__(self,token,annoid,resolution):
    """DB configuration and some state"""

    self._annid = annoid
    self._resolution = resolution

    # Get DB configuration stuff
    annprojdb = annproj.AnnotateProjectsDB()
    annoproj = annprojdb.getAnnoProj ( token )
    self.dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
    self.annodb = anndb.AnnotateDB ( self.dbcfg, annoproj )

    # Now get metadata for the old object
    self.seg = self.annodb.getAnnotation( self._annid )
    pprint (vars(self.seg))



  def addSynapse ( self, newid, voxels ):
    """Send the specific synapse to the database"""

    # Define synapse metadata
    syn = annotation.AnnSynapse ( )
    syn.annid = newid
    syn.author = self.seg.author
    syn.kvpairs = self.seg.kvpairs

    print "Writing synapse ", syn.annid

    # Put the RAMON object
    self.annodb.putAnnotation ( syn )

    # Rewrite the voxels
    self.annodb.annotate ( newid, self._resolution, voxels )

  def rewriteSynapses ( self ):
    """Relabel all voxels and separate into synapse objects"""

    voxels = self.annodb.getLocations(self._annid,self._resolution)

    print "Should ", len(voxels) 
    found = 0

    dontstore = False

    # Let's assume that all the synapses are in a single plane.
    while len(voxels) != 0:

      curvoxel = voxels[0] 

      # Do a cutout around a voxel and get the data
      #RBTODO address cutouts that exceed boundaries
      if curvoxel[0] < 128 or curvoxel[1] < 128:
        print "Found a voxel to close to border.  This script doesn't work there yet"
        sys.exit(-1)
      elif curvoxel[0] >= self.dbcfg.imagesz[self._resolution][0]-128 or curvoxel[0] >= self.dbcfg.imagesz[self._resolution][1]-128:
        print "Found a voxel to close to border.  This script doesn't work there yet"
        sys.exit(-1)
      # safe to cutout
      else:
        syncutout = self.annodb.cutout([curvoxel[0]-128,curvoxel[1]-128,curvoxel[2]-self.dbcfg.slicerange[0]],[256,256,1],self._resolution).data

      # Get and id for the synapse
      nextid = self.annodb.peekID()

      # sanity check
      assert ( syncutout[0,128,128] == self._annid )

      # create an empty active list
      active=[]
      # Search locally around center voxel
      active.append([0,128,128])
      while len(active) != 0 and dontstore==False:
        [z,y,x] = active.pop()
        syncutout[z,y,x] = nextid
        for [b,a] in itertools.product ([y-1,y,y+1],[x-1,x,x+1]): 
          try:
            if syncutout [z,b,a] == self._annid:
              active.append([z,b,a])
              syncutout[z,b,a] = nextid
          except Exception as e:
            print "Object not totally contained within cutout"
            print "If you got this error.  Your ingest is broken."
            print "  There are two know problems with this script.  See comments top of file."
            print "Skip this object and keep on going"

            dontstore = True
            break
            

      # Get a list of found voxels
      vec_func = np.vectorize ( lambda x: nextid if x == nextid else 0 )
      founddata = vec_func ( syncutout )
    
      # where are the entries
      offsets = np.nonzero ( founddata ) 
      foundlocvoxels = zip ( offsets[2], offsets[1], offsets[0] ) 

      # Offset information to relabel voxels into global space
      xoffset = curvoxel[0]-128
      yoffset = curvoxel[1]-128
      zoffset = curvoxel[2]
     
      # Relabel voxels into global space
      foundvoxels = [ [a+xoffset, b+yoffset, c+zoffset] for (a,b,c) in foundlocvoxels ] 
      if not dontstore:
        self.addSynapse ( nextid, foundvoxels )
      else:
        dontstore = False

      # RBTODO this may not be correct?  maybe this should be in the don't store clause
      # Remove found voxels from list we are trying to find
      found += len(foundvoxels)
      voxels = [ x for x in voxels if not x in foundvoxels ]

    print "Found ", found




def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution of the ingest data.')
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  
  result = parser.parse_args()

  sr = SynapseRewriter ( result.token, result.annid, result.resolution )

  sr.rewriteSynapses ()


if __name__ == "__main__":
  main()

