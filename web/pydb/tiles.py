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

  # number of files to read in during the ingest process.
  #  This needs to be tuned to memory capacity
  batchsize = 256
  
  # array of tile data into which we prefetch
  tiledata = []

  #
  # __init__ Constructor
  #
  def __init__ ( self, tilesize, inputprefix, startslice, cubesize ):
    """Create tiles"""
    self.xtilesize = tilesize[0]
    self.ytilesize = tilesize[1]
    self.fileprefix = inputprefix
    self.xcubesize, self.ycubesize, self.zcubesize = cubesize
    self.zstartfile = startslice

    # initialize our prefetch buffers
    for i in range ( self.batchsize ):
      self.tiledata.append ( np.zeros ( [self.ytilesize, self.xtilesize]))

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
  def numXTiles ( self, offset ):
    """number of tiles in x dimension"""
    if self.xcubesize % self.xtilesize == 0:
      if offset == 0:
        return self.xcubesize/self.xtilesize
      else:
        return self.xcubesize/self.xtilesize + 1
    # cube not aligned
    else:   
      if offset + self.xcubesize % self.xtilesize <= self.xtilesize:
        return self.xcubesize/self.xtilesize + 1
      else:
        return self.xclubesize/self.xtilesize + 2
      

  def numYTiles ( self, offset ):
    """number of tiles in y dimension"""
    if self.ycubesize % self.ytilesize == 0:
      if offset == 0:
        return self.ycubesize/self.ytilesize
      else:
        return self.ycubesize/self.ytilesize + 1
    # cube not aligned
    else:   
      if offset + self.ycubesize % self.ytilesize <= self.ytilesize:
        return self.ycubesize/self.ytilesize + 1
      else:
        return self.cubesize/self.ytilesize + 2


  #
  # pfslotidx
  #
  #  Find a location in the tiledata array to put this tile
  #
  #
  def pfSlotIndex ( self, tileidx, baseidx ):
    """Find a location in the tiledata array to put this tile"""
  
    return  (tileidx[0] - baseidx[0]) + (tileidx[1] - baseidx[1]) * self.xtilesize/self.xcubesize + \
            (tileidx[2] - baseidx[2]) * self.xtilesize/self.xcubesize * self.ytilesize/self.ycubesize  


  #
  # prefetch
  #
  #  Load a  specified tiles into the buffer.
  #
  #    This is a little weird.  You can ask for up to the prefetch batch in typical cases,
  #    but can only ask for up to batchsize / (xcubesize/xtilesize) * (ycubesize/ytilesize)  
  #    slices.  This only applies to coarse resolutions and makes the indexing easier.
  #    This is all a hack to fix the fact that a dictionary leaked memory, so we place
  #    the tiles in a dense array of numpy objects
  #
  def prefetch ( self, idxbatch ):
    """Fetch an area (not number) of tiles into memory"""

    # Files are best read in the order they are laid out on disk and then transferred to to appropriate buffer
    # For now let's assume they are laid out in x then y order in z directories.  This is the way that it works on xfs.

    # List of tiles to be prefetch
    tilelist = []

    # Need to clear previous cache contents
    for i in range ( self.batchsize ):
      self.tiledata [ i ] =  np.zeros ( [self.ytilesize, self.xtilesize] )

    # Figure out the base index for this prefetch group
    xyzbase =  zindex.MortonXYZ ( idxbatch[0] )
    self.pfbaseidx = [ xyzbase[0]*self.xcubesize/self.xtilesize, xyzbase[1]*self.ycubesize/self.ytilesize, xyzbase[2]*self.zcubesize ]

    for idx in idxbatch:

      xyz = zindex.MortonXYZ(idx)

      # add the tiles needed for this cube
      #  assume that the cubes and tiles are aligned and tiles are bigger than cubes

      # z is not tiled
      # and there are multiple cubes per tile.  so tilelist has duplicates
      for w in range(self.zcubesize):
        tilelist.append ( str(xyz[2] * self.zcubesize + w) + ' ' +  str(xyz[1]*self.ycubesize/self.ytilesize) + ' ' + str( xyz[0]*self.xcubesize/self.xtilesize))

    # get the unique indices
    tilelist = sorted ( set (tilelist) )

    # build the tile data dictionary
    for j in range (len ( tilelist )):
      tile = tilelist[j]
      [ zstr, ystr, xstr ] = tile.split()
      tileidx = [ int(xstr), int(ystr), int(zstr) ]

      fname =  self.tileFile ( tileidx[0], tileidx[1], tileidx[2] )

      # when we run out of tiles to prefetch we're out of data, i.e.
      # no more z tiles or missing data.  this keeps this simple, but
      #  this means that there is no bounds checking on this routine
      try:
        tileimage = Image.open ( fname, 'r' )
        pfslotidx = self.pfSlotIndex ( tileidx, self.pfbaseidx )
        self.tiledata [ pfslotidx ] = np.asarray ( tileimage )
      except IOError:
        continue


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

    # z is not tiled
    for z in range(self.zcubesize):

      # How much data we've moved to the cube
      ycubeoffset = 0

      for y in range(self.numYTiles(yoffset)):

        # Where the tiled data starts
        ytilestart =  ( ycorner / self.ytilesize ) * self.ytilesize + y * self.ytilesize

        # Pick the x scan lines
        # partial first tile
        if ytilestart <=ycorner:
          ytileoffset = yoffset 
          # only one tile
          if ycorner + self.ycubesize < ytilestart + self.ytilesize:
            yiters = self.ycubesize 
          else:
            yiters = self.ytilesize - yoffset  
        # partial last tile
        elif  ycorner + self.ycubesize < ytilestart + self.ytilesize :
          ytileoffset = 0
          yiters = (self.ycubesize - (self.ytilesize - yoffset)) %  self.ytilesize
        # full tile line
        else:
          ytileoffset = 0  
          yiters = self.ytilesize

        # How much data we've moved to the cube
        xcubeoffset = 0

        for x in range(self.numXTiles(xoffset)):

          # Where the tiled data starts
          xtilestart =  ( xcorner / self.xtilesize ) * self.xtilesize + x * self.xtilesize

          # Pick the x scan lines
          # partial first tile
          if xtilestart <=xcorner:
            xtileoffset = xoffset 
            # only one tile
            if xcorner + self.xcubesize < xtilestart + self.xtilesize:
              xiters = self.xcubesize 
            else:
              xiters = self.xtilesize - xoffset  
          # partial last tile
          elif  xcorner + self.xcubesize < xtilestart + self.xtilesize :
            xtileoffset = 0
            xiters = (self.xcubesize - (self.xtilesize - xoffset)) %  self.xtilesize
          # full scan line
          else:
            xtileoffset = 0  
            xiters = self.xtilesize

# RBDBG
#          print  "X iteration copying ", xiters, " bytes from tileoffset ", xtileoffset, " to cube offset ", xcubeoffset

# RBDBG use the prefetched data instead of the file data
#          fname =  self.tileFile ( (xcorner+xcubeoffset)/self.xtilesize,\
#                                   (ycorner+ycubeoffset)/self.ytilesize,\
#                                    zcorner+z ) 
#          try:
#            tileimage = Image.open ( fname, 'r' )
#            tiledata = np.asarray ( tileimage )
#            cube.data [ z, ycubeoffset:(ycubeoffset+yiters), xcubeoffset:(xcubeoffset+xiters) ]  =  \
#              tiledata [ ytileoffset:ytileoffset+yiters, xtileoffset:xtileoffset+xiters ]
#          except IOError:
#            print "File not found: ", fname
#            print "Using zeroed data instead"


          tileidx = [ (xcorner+xcubeoffset)/self.xtilesize, (ycorner+ycubeoffset)/self.ytilesize, zcorner+z ]
          pfslotidx = self.pfSlotIndex ( tileidx, self.pfbaseidx )
          cube.data [ z, ycubeoffset:(ycubeoffset+yiters), xcubeoffset:(xcubeoffset+xiters) ]  =  \
            self.tiledata [ pfslotidx ]  [ ytileoffset:ytileoffset+yiters, xtileoffset:xtileoffset+xiters ]
           
#        RBDBG for debugging check that the data is the same
#          Check that the data in the array is the same as the data the in prefetch buffers
#          assert tiledata.all() == self.tiledata [ pfslotidx ].all()
          
          #Update the amount of data we've written to cube
          xcubeoffset += xiters
        ycubeoffset += yiters

    # report the size of the cube we built
    return [xcubeoffset, ycubeoffset, self.zcubesize]

