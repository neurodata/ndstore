################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import tiles
import cStringIO
import zlib
import MySQLdb
import zindex
import braincube
import dbconfig

################################################################################
#
#  class: CubeDB
#
#  Manipulate/create/read from the Morton-order cube store
#  This routine manages all of the naming.
#
################################################################################

class CubeDB: 

  # Convenience variables to manage z slices
  startslice = 0
  slices = 0

#RBDBG think that this dictionary leaks memory
#  # batch of cubes in memory to be inserted as a single statement
#  #  dictionary by mortonidx
#  inmemcubes = {}

  def __init__ (self, dbconf):
    """Connect with the brain databases"""

    self.dbcfg = dbconf

    # Connection info in dbconfig
    self.conn = MySQLdb.connect (host = self.dbcfg.dbhost,
                            user = self.dbcfg.dbuser,
                            passwd = self.dbcfg.dbpasswd,
                            db = self.dbcfg.dbname)
#    cursor = self.conn.cursor ()
#    cursor.execute ("SELECT VERSION()")
#    row = cursor.fetchone ()
#    print "server version:", row[0]
#    cursor.close ()

    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

  #
  #  ingestCube
  #
  def ingestCube ( self, mortonidx, resolution, tilestack ):

    print "Ingest for resolution %s morton index %s, xyz " % (resolution , mortonidx) , zindex.MortonXYZ ( mortonidx )

    [ x, y, z ] = zindex.MortonXYZ ( mortonidx )
    [xcubedim, ycubedim, zcubedim] = self.dbcfg.cubedim [resolution ]
    bc = braincube.BrainCube ( self.dbcfg.cubedim[resolution] )
    corner = [ x*xcubedim, y*ycubedim, z*zcubedim ]
    bc.cubeFromFiles (corner, tilestack)
    return bc
#    self.inmemcubes[mortonidx] = bc


  #
  #  generateDB
  #
  def generateDB ( self, resolution ):
    """Generate the database from a tile stack"""

    [ximagesz, yimagesz] = self.dbcfg.imagesz [ resolution ]
    [xcubedim, ycubedim, zcubedim] = self.dbcfg.cubedim [resolution ]
    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # round up to the next largest slice
    if self.slices % zcubedim != 0 : 
      self.slices = ( self.slices / zcubedim + 1 ) * zcubedim

    # You've made this assumption.  It's reasonable.  Make it explicit
    # process more slices than you need.  Round up.  Missing data is 0s.
    assert self.slices % zcubedim == 0
    assert yimagesz % ycubedim == 0
    assert ximagesz % xcubedim == 0

    tilestack = tiles.Tiles ( self.dbcfg.tilesz,\
                              self.dbcfg.inputprefix + '/' + str(resolution), self.startslice,\
                              self.dbcfg.cubedim [resolution ]
                             ) 

    # Set the limits on the number of cubes in each dimension
    xlimit = ximagesz / xcubedim
    ylimit = yimagesz / ycubedim
    zlimit = self.slices / zcubedim

    # list of batched indexes
    idxbatch = []

#RBTODO this works.  But if there's no memory leak, no need to restart
#    # This is the restart code.  Figure out the highest index stored and 
#    #  insert the next one after that
#    dbname = self.dbcfg.tablebase + str(resolution)
#    cursor = self.conn.cursor()
#    sql = "SELECT MAX(zindex) FROM " + dbname 
#    cursor.execute(sql)
#    maxvaltpl = cursor.fetchone ()
#    print maxvaltpl
#    if maxvaltpl [0] != None:
#      maxval = int(maxvaltpl[0])
#      print "Maximum value", int(maxvaltpl[0])
#    else:
#      maxval = None


    # Figure out the geometry of the batch
    #   RBTODO get from program
    #   To prefetch a 4 x 4 x 1 cube is 2 x 2 x 16 tiles
    #  right now batchsize is 4 x 4 x 1 = 16 cubes which is 2 x 2 x 16 = 64 tiles  

    # batchsize is 8 x 8 x 4 cubes which is 4 x 4 x 4 x 16 tiles
    batchsize = 16 * 16 * 8

    # zmaxpf should always be 1, representing either 16 or 64 lines.  Never get more that 1 set of slices
    zstridepf = 32 /zcubedim
    zmaxpf = zstridepf
    # batchsize in number of cubes (converted from tiles)
    batchsize = tilestack.batchsize * (tilestack.xtilesize/xcubedim) * (tilestack.ytilesize/ycubedim) / zcubedim
#    RBDBG check to make sure the batch size is right
    otherbatchsize = tilestack.batchsize / 4
#    assert ( batchsize == otherbatchsize )


    # Ingest the slices in morton order
    for mortonidx in zindex.generator ( [xlimit, ylimit, zlimit] ):

#RBTODO part of the restart code
#      # Skip all values until the one following maxval
#      #  RBTODO do we need this
#      if maxval != None and maxval >= mortonidx:
#        continue

      xyz = zindex.MortonXYZ ( mortonidx )
      
      # if this exceeds the limit on the z dimension, do the ingest
      if len ( idxbatch ) == batchsize or xyz[2] == zmaxpf:

        # if we've hit our area bounds set the new limit
        if xyz [2] == zmaxpf:
           zmaxpf += zstridepf

        # preload the batch
        tilestack.prefetch ( idxbatch )

        # ingest the batch
        for idx in idxbatch:
          bc = self.ingestCube ( idx, resolution, tilestack )
          self.saveCube ( bc, idx, resolution )
        
# RBDBG this was for batch testing.  It worked but wasn't fast and maybe leaked memory.
#RBDBG remove dictionary
#        #save the batch
#        self.saveBatch ( idxbatch, resolution )
#        for idx in idxbatch:
#         self.saveCube( self.inmemcubes[idx], idx, resolution )
#        self.inmemcubes.clear()

        # Finished this batch.  Start anew.
        idxbatch = []

      #build a batch of indexes
      idxbatch.append ( mortonidx )

    # preload the remaining
    tilestack.prefetch ( idxbatch )

    # Ingest the remaining once the loop is over
    for idx in idxbatch:
      bc = self.ingestCube ( idx, resolution, tilestack )
      self.saveCube ( bc, idx, resolution )

#RBDBG remove dictionary
#    #save the batch
#    if len ( idxbatch ) != 0:
#      self.saveBatch ( idxbatch, resolution )
#
#    for idx in idxbatch:
#      self.saveCube( self.inmemcubes[idx], idx, resolution )


  #
  # Output the cube to the database
  #   use NumPy formatting I/O routines
  #
  def saveCube ( self, cube, mortonidx, resolution ):
    """Output the cube to the database"""

    dbname = self.dbcfg.tablebase + str(resolution)

    # create the DB BLOB
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, cube.data )
    cdz = zlib.compress (fileobj.getvalue()) 

    # insert the blob into the database
    cursor = self.conn.cursor()
    sql = "INSERT INTO " + dbname + " (zindex, cube) VALUES (%s, %s)"

    cursor.execute(sql, (mortonidx, cdz))


  #
  # Output a batch of cubes to the database
  #
  def saveBatch ( self, idxbatch, resolution ):
    """Output the cube to the database"""

    # This code has been tested and works, but doesn't seem
    #   to go fasst for MySQL.  Maybe reinstate later.
    assert 0

    dbname = self.dbcfg.tablebase + str(resolution)

    args=[]
    for idx in idxbatch:

      args.append ( idx ) 

      # create the DB BLOB
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, self.inmemcubes[idx].data )
      args.append ( zlib.compress (fileobj.getvalue()) )

    # insert the blob into the database
    sql = "INSERT INTO " + dbname + " (zindex, cube) VALUES %s;"
    in_p=', '.join(map(lambda x: '(%s,%s)', idxbatch))
    sql = sql % in_p
    cursor = self.conn.cursor()
    self.cursor.execute(sql, args)


  #
  #  getCube  
  #
  def getCube ( self, corner, dim, resolution ):
    """Extract a cube of arbitrary size.  Need not be aligned."""

    [xcubedim, ycubedim, zcubedim] = self.dbcfg.cubedim [resolution ]

    # Round to the nearest larger cube in all dimensions
    start = [ corner[0]/xcubedim,\
                    corner[1]/ycubedim,\
                    corner[2]/zcubedim ] 

    numcubes = [ (corner[0]+dim[0]+xcubedim-1)/xcubedim - start[0],\
                (corner[1]+dim[1]+ycubedim-1)/ycubedim - start[1],\
                (corner[2]+dim[2]+zcubedim-1)/zcubedim - start[2] ] 

    inbuf = braincube.BrainCube ( self.dbcfg.cubedim [resolution] )
    outbuf = braincube.BrainCube ( [numcubes[0]*xcubedim, numcubes[1]*ycubedim, numcubes[2]*zcubedim] )

    # Build a list of indexes to access
    listofidxs = []
    for z in range ( numcubes[2] ):
      for y in range ( numcubes[1] ):
        for x in range ( numcubes[0] ):
          mortonidx = zindex.XYZMorton ( [x+start[0], y+start[1], z+start[2]] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # Batch query for all cubes
    dbname = self.dbcfg.tablebase + str(resolution)
    cursor = self.conn.cursor()
    sql = "SELECT zindex, cube from " + dbname + " where zindex in (%s)" 
    # creats a %s for each list element
    in_p=', '.join(map(lambda x: '%s', listofidxs))
    # replace the single %s with the in_p string
    sql = sql % in_p
    cursor.execute(sql, listofidxs)

    # xyz offset stored for later use
    lowxyz = zindex.MortonXYZ ( listofidxs[0] )

    # Get the objects and add to the cube
    for i in range ( len(listofidxs) ): 
      idx, datastring = cursor.fetchone()

      # get the data out of the compressed blob
      newstr = zlib.decompress ( datastring[:] )
      newfobj = cStringIO.StringIO ( newstr )
      inbuf.data = np.load ( newfobj )

      #add the query result cube to the bigger cube
      curxyz = zindex.MortonXYZ(int(idx))
      offsetxyz = [ curxyz[0]-lowxyz[0], curxyz[1]-lowxyz[1], curxyz[2]-lowxyz[2] ]
      outbuf.addData ( inbuf, offsetxyz )

    # need to trim down the array to size
    #  only if the dimensions are not the same
    if dim[0] % xcubedim  == 0 and\
       dim[1] % ycubedim  == 0 and\
       dim[2] % zcubedim  == 0 and\
       corner[0] % xcubedim  == 0 and\
       corner[1] % ycubedim  == 0 and\
       corner[2] % zcubedim  == 0:
      pass
    else:
      outbuf.cutout ( corner[0]%xcubedim,dim[0],\
                      corner[1]%ycubedim,dim[1],\
                      corner[2]%zcubedim,dim[2] )
    return outbuf

