###############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
from PIL import Image
import sys
import zindex

################################################################################
#
#  class: Tiles
#
#  Helper functions to manage tiles 
#
################################################################################
class Tiles: 

  buffers = {}

  #
  # __init__ Constructor
  #
  def __init__ ( self, tilesize, inputprefix, startslice ):
    """Create tiles"""
    self.xtilesize = tilesize[0]
    self.ytilesize = tilesize[1]
    self.fileprefix = inputprefix
    self.zstartfile = startslice

  #
  # tileFile: Generate the file name.
  #
  def tileFile ( self, x, y, z ):
    filename = self.fileprefix + '/' + str (z+self.zstartfile) + "/" + str(y)  + "_" + str(x) + ".png"
    return filename

  #
  # num[XY]Tiles
  #
  #  Define the boundaries of iteration
  #
  def numXTiles ( self, offset, cubesize ):
    """number of tiles in x dimension"""
    if cubesize % self.xtilesize == 0:
      if offset == 0:
        return cubesize/self.xtilesize
      else:
        return cubesize/self.xtilesize + 1
    # cube not aligned
    else:   
      if offset + cubesize % self.xtilesize <= self.xtilesize:
        return cubesize/self.xtilesize + 1
      else:
        return cubesize/self.xtilesize + 2
      

  def numYTiles ( self, offset, cubesize ):
    """number of tiles in y dimension"""
    if cubesize % self.ytilesize == 0:
      if offset == 0:
        return cubesize/self.ytilesize
      else:
        return cubesize/self.ytilesize + 1
    # cube not aligned
    else:   
      if offset + cubesize % self.ytilesize <= self.ytilesize:
        return cubesize/self.ytilesize + 1
      else:
        return cubesize/self.ytilesize + 2

  #
  # Extract tile data from files into cubes
  #  This class has knowledge of the tile layout.
  #  Returns: size of the cube (as an 3-list/array)
  #
  def tilesToCube ( self, corner, cube ):
    """Move data from tiled files to array"""  

    # local geometry of the copy
    xcorner, ycorner, zcorner = corner
    xoffset = xcorner % self.xtilesize
    yoffset = ycorner % self.ytilesize
    zoffset = zcorner 

    # size of the cube of data
    zcubesize, ycubesize, xcubesize = cube.cubesize

    # z is not tiled
    for z in range(zcubesize):

      # How much data we've moved to the cube
      ycubeoffset = 0

      for y in range(self.numYTiles(yoffset,ycubesize)):

        # Where the tiled data starts
        ytilestart =  ( ycorner / self.ytilesize ) * self.ytilesize + y * self.ytilesize

        # Pick the x scan lines
        # partial first tile
        if ytilestart <=ycorner:
          ytileoffset = yoffset 
          # only one tile
          if ycorner + ycubesize < ytilestart + self.ytilesize:
            yiters = ycubesize 
          else:
            yiters = self.ytilesize - yoffset  
        # partial last tile
        elif  ycorner + ycubesize < ytilestart + self.ytilesize :
          ytileoffset = 0
          yiters = (ycubesize - (self.ytilesize - yoffset)) %  self.ytilesize
        # full tile line
        else:
          ytileoffset = 0  
          yiters = self.ytilesize

        # How much data we've moved to the cube
        xcubeoffset = 0

        for x in range(self.numXTiles(xoffset,xcubesize)):

          # Where the tiled data starts
          xtilestart =  ( xcorner / self.xtilesize ) * self.xtilesize + x * self.xtilesize

          # Pick the x scan lines
          # partial first tile
          if xtilestart <=xcorner:
            xtileoffset = xoffset 
            # only one tile
            if xcorner + xcubesize < xtilestart + self.xtilesize:
              xiters = xcubesize 
            else:
              xiters = self.xtilesize - xoffset  
          # partial last tile
          elif  xcorner + xcubesize < xtilestart + self.xtilesize :
            xtileoffset = 0
            xiters = (xcubesize - (self.xtilesize - xoffset)) %  self.xtilesize
          # full scan line
          else:
            xtileoffset = 0  
            xiters = self.xtilesize

#          print  "X iteration copying ", xiters, " bytes from tileoffset ", xtileoffset, " to cube offset ", xcubeoffset

          fname =  self.tileFile ( (xcorner+xcubeoffset)/self.xtilesize,\
                                   (ycorner+ycubeoffset)/self.ytilesize,\
                                    zcorner+z ) 
          try:
            tileimage = Image.open ( fname, 'r' )
            tiledata = np.asarray ( tileimage )
            cube.data [ z, ycubeoffset:(ycubeoffset+yiters), xcubeoffset:(xcubeoffset+xiters) ]  =  \
              tiledata [ ytileoffset:ytileoffset+yiters, xtileoffset:xtileoffset+xiters ]
          except IOError:
            print "File not found: ", fname
            print "Using zeroed data instead"


          
          #Update the amount of data we've written to cube
          xcubeoffset += xiters
        ycubeoffset += yiters

    # report the size of the cube we built
    return [xcubeoffset, ycubeoffset, zcubesize]


