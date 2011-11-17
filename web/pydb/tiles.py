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
  
  # array of tile data into which we prefetch
  tiledata = []

  #
  # __init__ Constructor
  #
  def __init__ ( self, tiledim, inputprefix, startslice, cubedim ):
    """Create tiles"""
    self.xtiledim = tiledim[0]
    self.ytiledim = tiledim[1]
    self.fileprefix = inputprefix
    self.xcubedim, self.ycubedim, self.zcubedim = cubedim
    self.zstartfile = startslice


  #
  # setBatchSizej 
  #
  #  Maybe this should be part of a constructor.  Easier this way.
  #
  def setBatchSize ( self, numtiles, cubebatchsz ):
    """Set the number of tiles to be prefetched"""
    
    # make sure it's an empty list
    self.tiledata = []

    # get the batch size of the cube for indexing

    # initialize our prefetch buffers
    for i in range ( numtiles ):
      self.tiledata.append ( np.zeros ( [self.ytiledim, self.xtiledim]) )


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
    if self.xcubedim % self.xtiledim == 0:
      if offset == 0:
        return self.xcubedim/self.xtiledim
      else:
        return self.xcubedim/self.xtiledim + 1
    # cube not aligned
    else:   
      if offset + self.xcubedim % self.xtiledim <= self.xtiledim:
        return self.xcubedim/self.xtiledim + 1
      else:
        return self.xclubesize/self.xtiledim + 2
      

  def numYTiles ( self, offset ):
    """number of tiles in y dimension"""
    if self.ycubedim % self.ytiledim == 0:
      if offset == 0:
        return self.ycubedim/self.ytiledim
      else:
        return self.ycubedim/self.ytiledim + 1
    # cube not aligned
    else:   
      if offset + self.ycubedim % self.ytiledim <= self.ytiledim:
        return self.ycubedim/self.ytiledim + 1
      else:
        return self.cubedim/self.ytiledim + 2


  #
  # pfslotidx
  #
  #  Find a location in the tiledata array to put this tile
  #
  #
  def pfSlotIndex ( self, tileidx, baseidx ):
    """Find a location in the tiledata array to put this tile"""
  
#    print tileidx, baseidx, (tileidx[2] - baseidx[2]) +\
#           (tileidx[1] - baseidx[1])*self.zcubedim*self.ytiledim/self.ycubedim +\
#           (tileidx[0] - baseidx[0])*self.zcubedim*self.ycubedim/self.xtiledim*self.xtiledim/self.xcubedim
# Not sure what the bug here is.  NEed to use this one.
    return (tileidx[2] - baseidx[2]) +\
           (tileidx[1] - baseidx[1]) * self.zcubedim*self.zbatchsz  * self.ytiledim/self.ycubedim  +\
           (tileidx[0] - baseidx[0]) * self.zcubedim*self.zbatchsz  * self.ycubedim*self.ybatchsize * self.xtiledim/self.xcubedim

#  Change the function for small cases
#    print baseidx, tileidx, (tileidx[0] - baseidx[0]) + (tileidx[1] - baseidx[1]) * self.xtiledim/self.xcubedim + \
#               (tileidx[2] - baseidx[2]) * self.xtiledim/self.xcubedim * self.ytiledim/self.ycubedim
#
#    return  (tileidx[0] - baseidx[0]) + (tileidx[1] - baseidx[1]) * self.xtiledim/self.xcubedim + \
#           (tileidx[2] - baseidx[2]) * self.xtiledim/self.xcubedim * self.ytiledim/self.ycubedim  


  #
  # prefetch
  #
  #  Load a  specified tiles into the buffer.
  #
  #    This is a little weird.  You can ask for up to the prefetch batch in typical cases,
  #    but can only ask for up to batchsize / (xcubedim/xtiledim) * (ycubedim/ytiledim)  
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

    
    print len(idxbatch) 
    print idxbatch
    # Need to clear previous cache contents
    for i in range ( len ( self.tiledata ) ):
      self.tiledata[i] = np.zeros ( [self.ytiledim, self.xtiledim] )

    # Figure out the base index for this prefetch group
    xyzbase =  zindex.MortonXYZ ( idxbatch[0] )
    self.pfbaseidx = [ xyzbase[0]*self.xcubedim/self.xtiledim, xyzbase[1]*self.ycubedim/self.ytiledim, xyzbase[2]*self.zcubedim ]

    for idx in idxbatch:

      xyz = zindex.MortonXYZ(idx)

      # add the tiles needed for this cube
      #  assume that the cubes and tiles are aligned and tiles are bigger than cubes

      # z is not tiled
      # and there are multiple cubes per tile.  so tilelist has duplicates
      for w in range(self.zcubedim):
        tilelist.append ( str(xyz[2] * self.zcubedim + w) + ' ' +  str(xyz[1]*self.ycubedim/self.ytiledim) + ' ' + str( xyz[0]*self.xcubedim/self.xtiledim))

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
        print tileidx, self.pfbaseidx, pfslotidx
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
    xoffset = xcorner % self.xtiledim
    yoffset = ycorner % self.ytiledim
    zoffset = zcorner 

    # z is not tiled
    for z in range(self.zcubedim):

      # How much data we've moved to the cube
      ycubeoffset = 0

      for y in range(self.numYTiles(yoffset)):

        # Where the tiled data starts
        ytilestart =  ( ycorner / self.ytiledim ) * self.ytiledim + y * self.ytiledim

        # Pick the x scan lines
        # partial first tile
        if ytilestart <=ycorner:
          ytileoffset = yoffset 
          # only one tile
          if ycorner + self.ycubedim < ytilestart + self.ytiledim:
            yiters = self.ycubedim 
          else:
            yiters = self.ytiledim - yoffset  
        # partial last tile
        elif  ycorner + self.ycubedim < ytilestart + self.ytiledim :
          ytileoffset = 0
          yiters = (self.ycubedim - (self.ytiledim - yoffset)) %  self.ytiledim
        # full tile line
        else:
          ytileoffset = 0  
          yiters = self.ytiledim

        # How much data we've moved to the cube
        xcubeoffset = 0

        for x in range(self.numXTiles(xoffset)):

          # Where the tiled data starts
          xtilestart =  ( xcorner / self.xtiledim ) * self.xtiledim + x * self.xtiledim

          # Pick the x scan lines
          # partial first tile
          if xtilestart <=xcorner:
            xtileoffset = xoffset 
            # only one tile
            if xcorner + self.xcubedim < xtilestart + self.xtiledim:
              xiters = self.xcubedim 
            else:
              xiters = self.xtiledim - xoffset  
          # partial last tile
          elif  xcorner + self.xcubedim < xtilestart + self.xtiledim :
            xtileoffset = 0
            xiters = (self.xcubedim - (self.xtiledim - xoffset)) %  self.xtiledim
          # full scan line
          else:
            xtileoffset = 0  
            xiters = self.xtiledim

# RBDBG
#          print  "X iteration copying ", xiters, " bytes from tileoffset ", xtileoffset, " to cube offset ", xcubeoffset

# RBDBG use the prefetched data instead of the file data
          fname =  self.tileFile ( (xcorner+xcubeoffset)/self.xtiledim,\
                                  (ycorner+ycubeoffset)/self.ytiledim,\
                                   zcorner+z ) 
          try:
            tileimage = Image.open ( fname, 'r' )
            tiledata = np.asarray ( tileimage )
            cube.data [ z, ycubeoffset:(ycubeoffset+yiters), xcubeoffset:(xcubeoffset+xiters) ]  =  \
              tiledata [ ytileoffset:ytileoffset+yiters, xtileoffset:xtileoffset+xiters ]
          except IOError:
            print "File not found: ", fname
            print "Using zeroed data instead"
            tiledata = np.zeros ( [ self.ytiledim, self.xtiledim ] )


          tileidx = [ (xcorner+xcubeoffset)/self.xtiledim, (ycorner+ycubeoffset)/self.ytiledim, zcorner+z ]
          pfslotidx = self.pfSlotIndex ( tileidx, self.pfbaseidx )
          cube.data [ z, ycubeoffset:(ycubeoffset+yiters), xcubeoffset:(xcubeoffset+xiters) ]  =  \
            self.tiledata [ pfslotidx ]  [ ytileoffset:ytileoffset+yiters, xtileoffset:xtileoffset+xiters ]
           
#        RBDBG for debugging check that the data is the same
#          Check that the data in the array is the same as the data the in prefetch buffers
#          if ( tiledata.all() != self.tiledata [ pfslotidx ].all() ):
#            print "Read", tiledata
#            print "Buffered", pfslotidx, self.tiledata [ pfslotidx ]
          assert tiledata.all() == self.tiledata [ pfslotidx ].all()
          
          #Update the amount of data we've written to cube
          xcubeoffset += xiters
        ycubeoffset += yiters

    # report the size of the cube we built
    return [xcubeoffset, ycubeoffset, self.zcubedim]

