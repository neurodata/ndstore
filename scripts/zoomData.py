import sys
import os

import argparse
import numpy as np
import zlib
import StringIO
from contextlib import closing 

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

from cube import Cube 
import ocplib
import ocpcarest
import ocpcaproj
import ocpcadb

def zoomIn(old_data, scaling):

  new_data = np.zeros ( [old_data.shape[0], old_data.shape[1]*(scaling), old_data.shape[2]*(scaling)], dtype=np.uint16)
  #print new_data.shape
  #print old_data.shape
  for i in xrange(0,new_data.shape[2]):
    for j in xrange(0,new_data.shape[1]):
      for k in xrange(0,new_data.shape[0]):
        #print "({},{},{}) to ({},{},{})".format(i,j,k,i/scaling,j/scaling,j/scaling)
        new_data[k, j, i] = old_data[k/scaling, j/scaling, i/scaling] 

  return new_data

# AB TODO -- zoomInData is made for uint32_t only. Write templated version? 
def cZoomIn(old_data, factor):
  scaling = 2**factor
  new_data = np.zeros ( [old_data.shape[0], old_data.shape[1]*(scaling), old_data.shape[2]*(scaling)], dtype=np.uint16)
  ocplib.zoomInData_ctype_OMP16 ( old_data, new_data, int(factor) )
  return new_data 

def buildStack(token, channel, res, base_res):
  """ build a zoom hierarchy of images """
  scaling = 2**(base_res-res)
  with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
    proj = projdb.loadToken(token)

  with closing(ocpcadb.OCPCADB(proj)) as db:
    ch = proj.getChannelObj(channel)
    
    # get db sizes
    [[ximagesz, yimagesz, zimagesz], timerange] = proj.datasetcfg.imageSize(base_res)
    [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[base_res]

    [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[base_res]

    newcubedim = proj.datasetcfg.getCubeDims()[res]

    xlimit = (ximagesz-1) / xcubedim + 1
    ylimit = (yimagesz-1) / ycubedim + 1
    zlimit = (zimagesz-1) / zcubedim + 1
  
    # iterate over the old cube 
    for z in range(zlimit):
      for y in range(ylimit):
        for x in range(xlimit):
          # cutout data
          old_data = db.cutout( ch, [x*xcubedim, y*ycubedim, z*zcubedim], cubedim, base_res ).data

          #new_data = zoomIn(old_data, scaling)
          new_data = cZoomIn(old_data, base_res-res)

          newzsize = new_data.shape[0] / newcubedim[2] #old_data.shape[0]
          newysize = new_data.shape[1] / newcubedim[1] #old_data.shape[1]
          newxsize = new_data.shape[2] / newcubedim[0] #old_data.shape[2]
          #print "sizes: {} {} {}".format(newxsize, newysize, newzsize) 
          for z2 in range(newzsize):
            for y2 in range(newysize):
              for x2 in range(newxsize):
                #print "{} {} {}".format(x*newxsize+x2,y*newysize+y2,z*newzsize+z2)
                zidx = ocplib.XYZMorton([x*newxsize+x2, y*newysize+y2, z*newzsize+z2])
                cube = Cube.getCube(newcubedim, ch.getChannelType(), ch.getDataType())
                cube.zeros()
                cube.data = new_data[z2*newcubedim[2]:(z2+1)*newcubedim[2], y2*newcubedim[1]:(y2+1)*newcubedim[1], x2*newcubedim[0]:(x2+1)*newcubedim[0]]
                #print "Grabbing cube from [{}:{} , {}:{}, {}:{}]".format(z2*newcubedim[2],(z2+1)*newcubedim[2], y2*newcubedim[1],(y2+1)*newcubedim[1], x2*newcubedim[0],(x2+1)*newcubedim[0])
                print "Inserting Cube {} at res {}".format(zidx, res)
                db.putCube(ch, zidx, res, cube, update=True)

def main():
  
  parser = argparse.ArgumentParser(description='Upsample an image')
  parser.add_argument('token', action='store', help='Token for the project.')
  parser.add_argument('channel', action='store', help='Channel for the project.')
  parser.add_argument('res', action='store', type=int, help='Upsampled resolution.')
  parser.add_argument('base_res', action='store', type=int, help='Base resolution (to upsample).')

  result = parser.parse_args()

  buildStack(result.token, result.channel, result.res, result.base_res)

if __name__ == '__main__':
  main()
