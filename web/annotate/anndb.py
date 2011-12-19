################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import cStringIO
import zlib
import MySQLdb

import zindex
import anncube

################################################################################
#
#  class: AnnotateDB
#
#  Manipulate/create/read from the Morton-order cube store
#
################################################################################

class AnnotateDB: 

  # Could add these to dbconfig.  Probably remove res as tablebase instead
  ids_tbl = "ids"
  entities_tbl = "entities"
  items_tbl = "items"
  ann_tbl = "annotations" 

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

    # How many slices?
    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # get the size of the image and cube
#    self.cubedim = self.dbcfg.cubedim [ self.dbcfg.annotateres ] 
#    self.imagesize = self.dbcfg.imagesz [ self.dbcfg.annotateres ]
    [ self.xcubedim, self.ycubedim, self.zcubedim ] = self.cubedim = [4,4,4]
    [ self.ximagesize, self.yimagesize, self.zimagesize ] = self.imagesize = [16,16,16]


  def __del ( self ):
    """Close the connection"""
    conn.close()


  #
  #  nextIdentifier
  #
  def nextID ( self ):
    """Get an new identifier"""
    
    # Query the current max identifier
    cursor = self.conn.cursor ()
    sql = "SELECT max(id) FROM " + str ( self.ids_tbl )
    try:
      cursor.execute ( sql )
    except:
      print "Unknown problem with identifier table", self.ids_tbl
      assert 0

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
    # if the table is empty start at 1, 0 is no annotation
    if ( row[0] == None ):
      identifier = 1
    else:
      identifier = int ( row[0] ) + 1

#    print "Identifier = ", identifier

    # increment and update query
    sql = "INSERT INTO " + str(self.ids_tbl) + " VALUES ( " + str(identifier) + " ) "
    try:
      cursor.execute ( sql )
    except:
      print "Failed to insert {0} into identifier table {1}".format( identifier, self.ids_tbl )
      assert 0

    # InnoDB needs a commit
    cursor.close()
    self.conn.commit()

    return identifier

  #
  # getCube
  #
  def getCube ( self, key ):
    """Load a cube from the annotation database"""

    # Create a cube object
    cube = anncube.AnnotateCube ( self.cubedim )

    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT cube FROM " + self.ann_tbl + " WHERE zindex = " + str(key)
    try:
      cursor.execute ( sql )
    except:
      print "Unknown problem with table", self.ann_tbl

    row = cursor.fetchone ()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      cube.zeros ()

    else: 
      # decompress the cube
      cube.fromNPZ ( row[0] )

    cursor.close()
     
    return cube


  #
  # putCube
  #
  def putCube ( self, key, cube ):
    """Store a cube from the annotation database"""

    cursor = self.conn.cursor ()

    # compress the cube
    npz = cube.toNPZ ()

    # we created a cube from zeros
    if cube.fromZeros ():

      sql = "INSERT INTO " + self.ann_tbl +  "(zindex, cube) VALUES (%s, %s)"
      try:
        cursor.execute ( sql, (key,npz))
      except:
        print "Error inserting into ", self.items_tbl

    else:

      sql = "UPDATE " + self.ann_tbl + " SET cube=(%s) WHERE zindex=" + str(key)
      try:
        cursor.execute ( sql, (npz))
      except:
        print "Error updating key={0} in table".format( key, self.items_tbl)
        assert 0

    cursor.close()
    self.conn.commit()


  #
  # addEntity
  #
  #  Add a single entity as a list of voxels
  #
  def addEntity ( self, locations ):
    """Add an entity as a list of voxels"""

    #  An item may exist across several cubes
    #  Convert the locations into Morton order

    # dictionary of mortonkeys
    cubelocs = {}

    #  list of locations inside each morton key
    for loc in locations:
      cubeno = loc[0]/self.cubedim[0], loc[1]/self.cubedim[1], loc[2]/self.cubedim[2]
      key = zindex.XYZMorton(cubeno)
      if cubelocs.get(key,None) == None:
        cubelocs[key] = [];
      cubelocs[key].append(loc)


    # get and identifier for this object
    entityid = self.nextID()

    # iterator over the list for each cube
    for key, loclist in cubelocs.iteritems():

        cube = self.getCube ( key )

        # get a voxel offset for the cube
        cubeoff = zindex.MortonXYZ(key)
        offset = [ cubeoff[0]*self.cubedim[0],\
                   cubeoff[1]*self.cubedim[1],\
                   cubeoff[2]*self.cubedim[2] ]

        # add the items
        exceptions = cube.addEntity ( entityid, offset, loclist )

        # update the sparse list of exceptions
        #RBTODO

        self.putCube ( key, cube)

  #
  # addEntities
  #
  #  This takes a z,y,x cube of identifiers, relabels them and
  #   puts them in the database.
  #
  #  In slice, col, row format (z,y,x) look out for the weirdness
  #   this works with image coordinates
  #
  def addEntities ( self, zyxcorner, zyxdata ):
    """Add an entity as a numpy array in row c"""

    print zyxcorner
    print zyxdata.shape
    print self.zimagesize

    # Check some bounds
    assert zyxcorner[0] >= 0 and zyxcorner[1] >= 0 and zyxcorner[2] >= 0
    assert zyxcorner[0]+zyxdata.shape[0] <= self.zimagesize
    assert zyxcorner[1]+zyxdata.shape[1] <= self.yimagesize
    assert zyxcorner[2]+zyxdata.shape[2] <= self.ximagesize

    #  Get the range of cubes
    zstart = zyxcorner[0] / self.zcubedim
    ystart = zyxcorner[1] / self.ycubedim
    xstart = zyxcorner[2] / self.xcubedim
    zend = (zyxcorner[0] + zyxdata.shape[0] -1 ) / self.ycubedim
    yend = (zyxcorner[1] + zyxdata.shape[1] -1 ) / self.ycubedim
    xend = (zyxcorner[2] + zyxdata.shape[2] -1 ) / self.xcubedim

    # Helpers to index the loop
    zoffset = zyxcorner[0] % self.zcubedim
    yoffset = zyxcorner[1] % self.ycubedim
    xoffset = zyxcorner[2] % self.xcubedim

    # if you gave an unaligned cube, we do a copy
    if ( xoffset != 0 ) or ( yoffset != 0 ) or ( zoffset != 0 ) or\
       ( zyxdata.shape[0] % self.zcubedim != 0 ) or\
       ( zyxdata.shape[1] % self.ycubedim != 0 ) or\
       ( zyxdata.shape[2] % self.xcubedim != 0 ) :

      # OK, let's build into cubedim aligned larger array
      zyxaligned = np.zeros ( [ (zstart - zend + 1) * self.zcubedim,\
                                 (ystart - yend + 1) * self.ycubedim,\
                                 (xstart - xend + 1) * self.xcubedim ] )

      zyxaligned [ zoffset:zoffset+zyxdata.shape[0],\
                    yoffset:yoffset+zyxdata.shape[1],\
                    xoffset:xoffset+zyxdata.shape[2] ] =\
            zyxdata [:,:,:]

    # use input if aligned
    else:
      zyxaligned = zyxdata

    # RBTODO
    # rewrite the identifiers so that they are unique
#    self.rewrite ( zyxaligned )

    # at this point, data are cubedim aligned in ardata
    # maybe should process this in zorder or ranges.  Maybe later.
    for zcube in range ( zstart, zend ):
      for ycube in range ( ystart, yend ):
        for xcube in range ( xstart, xend ):

          # load the cube from the database
          key = zindex.XYZMorton ( [ xcube, ycube, zcube ] )
          cube = self.getCube ( key )

          # update the cube
          cube.arrayUpdate ( zyxaligned [ (zstart*self.zcubedim):(zstart*self.zcubedim+self.zcubedim),\
                                          (ystart*self.ycubedim):(ystart*self.ycubedim+self.ycubedim),\
                                          (xstart*self.xcubedim):(xstart*self.xcubedim+self.xcubedim) ] )

          # store the cube in the database
          self.putCube ( key, cube )


  #
  #  Return a cube of data from the database
  #  Must account for zeros.
  #
  def cutout ( self, corner, dim ):
    """Extract a cube of arbitrary size.  Need not be aligned."""

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/self.zcubedim
    ystart = corner[1]/self.ycubedim
    xstart = corner[0]/self.xcubedim

    znumcubes = (corner[2]+dim[2]+self.zcubedim-1)/self.zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+self.ycubedim-1)/self.ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+self.xcubedim-1)/self.xcubedim - xstart

    # input cube is the database size
    incube = anncube.AnnotateCube ( self.cubedim )

    # output cube is as big as was asked for and zero it.
    outcube = anncube.AnnotateCube ( [xnumcubes*self.xcubedim,\
                                      ynumcubes*self.ycubedim,\
                                      znumcubes*self.zcubedim] )
    outcube.zeros()
    print outcube.data.shape

    # Build a list of indexes to access
    listofidxs = []
    for z in range ( znumcubes ):
      for y in range ( ynumcubes ):
        for x in range ( xnumcubes ):
          mortonidx = zindex.XYZMorton ( [x+xstart, y+ystart, z+zstart] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # Batch query for all cubes
    dbname = self.ann_tbl
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


      #add the query result cube to the bigger cube
      curxyz = zindex.MortonXYZ(int(idx))
      offset = [ curxyz[0]-lowxyz[0], curxyz[1]-lowxyz[1], curxyz[2]-lowxyz[2] ]

      print idx, curxyz

      # get an input cube 
      incube.fromNPZ ( datastring[:] )

      # add it to the output cube
      outcube.addData ( incube, offset ) 

    # need to trim down the array to size
    #  only if the dimensions are not the same
    if dim[0] % self.xcubedim  == 0 and\
       dim[1] % self.ycubedim  == 0 and\
       dim[2] % self.zcubedim  == 0 and\
       corner[0] % self.xcubedim  == 0 and\
       corner[1] % self.ycubedim  == 0 and\
       corner[2] % self.zcubedim  == 0:
      pass
    else:
      outcube.trim ( corner[0]%self.xcubedim,dim[0],\
                      corner[1]%self.ycubedim,dim[1],\
                      corner[2]%self.zcubedim,dim[2] )
    return outcube





