import numpy as np
import cStringIO
import zlib
import MySQLdb

import zindex
import anncube
import annproj

import sys

#TODO convert the asserts into exceptions so that not found can be returned

################################################################################
#
#  class: AnnotateDB
#
#  Manipulate/create/read from the Morton-order cube store
#
################################################################################

class AnnError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class AnnotateDB: 

  def __init__ (self, dbconf, annoproj):
    """Connect with the brain databases"""

    self.dbcfg = dbconf
    self.annoproj = annoproj

    dbinfo = self.annoproj.getDBHost(), self.annoproj.getDBUser(), self.annoproj.getDBPasswd(), self.annoproj.getDBName() 

    # Connection info 
    try:
      self.conn = MySQLdb.connect (host = self.annoproj.getDBHost(),
                            user = self.annoproj.getDBUser(),
                            passwd = self.annoproj.getDBPasswd(),
                            db = self.annoproj.getDBName())
    except:
      raise AnnError ( dbinfo )
      

    # How many slices?
    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # get the size of the image and cube
    [ self.xcubedim, self.ycubedim, self.zcubedim ] = self.cubedim = self.dbcfg.cubedim [ annoproj.getResolution() ] 
    [ self.ximagesize, self.yimagesize ] = self.imagesize = self.dbcfg.imagesz [ annoproj.getResolution() ]

    # PYTODO create annidx object


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
    sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Problem retrieving identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
    # if the table is empty start at 1, 0 is no annotation
    if ( row[0] == None ):
      identifier = 1
    else:
      identifier = int ( row[0] ) + 1

    # increment and update query
    sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(identifier) + " ) "
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
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
    sql = "SELECT cube FROM " + self.annoproj.getAnnotationsTbl() + " WHERE zindex = " + str(key)
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0


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

      sql = "INSERT INTO " + self.annoproj.getAnnotationsTbl() +  "(zindex, cube) VALUES (%s, %s)"
      try:
        cursor.execute ( sql, (key,npz))
      except MySQLdb.Error, e:
        print "Error inserting cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        assert 0

    else:

      sql = "UPDATE " + self.annoproj.getAnnotationsTbl() + " SET cube=(%s) WHERE zindex=" + str(key)
      try:
        cursor.execute ( sql, (npz))
      except MySQLdb.Error, e:
        print "Error updating cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        assert 0

    cursor.close()
    self.conn.commit()


  #
  # getExceptions
  #
  def getExceptions ( self, key, entityid ):
    """Load a the list of excpetions for this cube"""
   
    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT exlist FROM " + self.except_tbl + " WHERE zindex = " + str(key) + " AND id = " + str(entityid)
    print sql 
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error reading exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    row = cursor.fetchone ()

    cursor.close()

    # If we can't find a list of exceptions, they don't exist
    if ( row == None ):
      return []
    else: 
      fobj = cStringIO.StringIO ( row[0] )
      return np.load ( fobj )

  #
  # updateExceptions
  #
  def updateExceptions ( self, key, entityid, exceptions ):
    """Store a list of exceptions"""

    curexlist = self.getExceptions( key, entityid ) 

    print ("Current exceptions", curexlist )

    cursor = self.conn.cursor ()

    # RBTODO need to make exceptions a set
    if curexlist==[]:

      print "Adding new exceptions", exceptions 

      sql = "INSERT INTO " + self.except_tbl +  "(zindex, id, exlist) VALUES (%s, %s, %s)"
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, exceptions )
        print sql, key, entityid 
        cursor.execute ( sql, (key, entityid, fileobj.getvalue()))
      except MySQLdb.Error, e:
        print "Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        assert 0

    # In this case we have an update query
    else:

      newexlist = np.append ( curexlist, exceptions )

      print newexlist

      print "Updating exceptions with ", exceptions 

      sql = "UPDATE " + self.except_tbl + " SET exlist=(%s) WHERE zindex=" + str(key) + " AND id = " + str(entityid)
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, newexlist )
        cursor.execute ( sql, (fileobj.getvalue()))
      except MySQLdb.Error, e:
        print "Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        assert 0

    cursor.close()
    self.conn.commit()




  #
  # annotate
  #
  #  Called by newEntity, addEntity and extendEntity to actually number
  #   the voxels and build the exception
  #
  def annotate ( self, entityid, locations, conflictopt ):
    """Label the voxel locations or add as exceptions is the are already labeled."""

    #  An item may exist across several cubes
    #  Convert the locations into Morton order

    # dictionary of mortonkeys
    # RBTODO make a defaultdict
    cubelocs = {}

    #  list of locations inside each morton key
    for loc in locations:
      cubeno = loc[0]/self.cubedim[0], loc[1]/self.cubedim[1], (loc[2]-self.startslice)/self.cubedim[2]
      key = zindex.XYZMorton(cubeno)
      if cubelocs.get(key,None) == None:
        cubelocs[key] = [];
      cubelocs[key].append([loc[0],loc[1],loc[2]-self.startslice])

    # iterator over the list for each cube
    for key, loclist in cubelocs.iteritems():

        cube = self.getCube ( key )

        # get a voxel offset for the cube
        cubeoff = zindex.MortonXYZ(key)
        offset = [ cubeoff[0]*self.cubedim[0],\
                   cubeoff[1]*self.cubedim[1],\
                   cubeoff[2]*self.cubedim[2] ]

        # add the items
        exceptions = cube.annotate ( entityid, offset, loclist, conflictopt )

        # update the sparse list of exceptions
        if len(exceptions) != 0:
          self.updateExceptions ( key, entityid, exceptions )

        self.putCube ( key, cube)

    # PMTODO update index

  # end annotate

  #
  # addEntity
  #
  #  Include the following locations as part of the specified entity.
  #  entity as a list of voxels.  Returns the entity id
  #  This is for ingesting already annotated data sets.  
  #  Don't check to make sure that the object exists.
  #
  def addEntity ( self, entityid, locations, conflictopt ):
    """Extend an existing entity as a list of voxels"""

    # label the voxels and exceptions
    self.annotate ( entityid, locations, conflictopt )

    return entityid

  #
  # extendEntity
  #
  #  Include the following locations as part of the specified entity.
  #  entity as a list of voxels.  Returns the entity id
  #
  def extendEntity ( self, entityid, locations, conflictopt ):
    """Extend an existing entity as a list of voxels"""

# RB TODO comment out for kasthuri.  Do we want to check?

    # Query the identifier
    cursor = self.conn.cursor ()
    sql = "SELECT id FROM {0} WHERE id={1}".format(str(self.annoproj.getIDsTbl()),str(entityid))
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error reading identifier: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    # Get the query result
    row = cursor.fetchone ()
    print row
    # If the annotation doesn't exist, throw an error
    if ( row == None ):
      assert 0

    # label the voxels and exceptions
    self.annotate ( entityid, locations, conflictopt )

    return entityid


  #
  # newEntity
  #
  #  Add a single entity as a list of voxels. Returns the entity id.
  #
  def newEntity ( self, locations, conflictopt ):
    """Add an entity as a list of voxels"""

    # get and identifier for this object
    entityid = self.nextID()

    self.annotate ( entityid, locations, conflictopt )

    return entityid


  #
  # annotateEntityDense
  #
  #  Process a cube of data that has been labelled with annotations.
  #
  def annotateEntityDense ( self, corner, dim, annodata, conflictopt ):
    """Process all the annotations in the dense volume"""

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/self.zcubedim
    ystart = corner[1]/self.ycubedim
    xstart = corner[0]/self.xcubedim

    znumcubes = (corner[2]+dim[2]+self.zcubedim-1)/self.zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+self.ycubedim-1)/self.ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+self.xcubedim-1)/self.xcubedim - xstart

    zoffset = corner[2]%self.zcubedim
    yoffset = corner[1]%self.ycubedim
    xoffset = corner[0]%self.xcubedim

    databuffer = np.zeros ([znumcubes*self.zcubedim, ynumcubes*self.ycubedim, xnumcubes*self.xcubedim], dtype=np.uint32 )
    databuffer [ zoffset:zoffset+dim[2], yoffset:yoffset+dim[1], xoffset:xoffset+dim[0] ] = annodata 

    for z in range(znumcubes):
      for y in range(ynumcubes):
        for x in range(xnumcubes):

          key = zindex.XYZMorton ([x+xstart,y+ystart,z+zstart])
          cube = self.getCube ( key )

          if conflictopt == 'O':
            cube.overwrite ( databuffer [ z*self.zcubedim:(z+1)*self.zcubedim, y*self.ycubedim:(y+1)*self.ycubedim, x*self.xcubedim:(x+1)*self.xcubedim ] )
          else:
            print "Unsupported conflict option.  FIX ME"
            assert 0

          self.putCube ( key, cube)
          
          
   


  def addEntityDense ( self, corner, dim, annodata, conflictopt ):
    """Add the annotations in this cube.  Do not interpret the values.  Put values straight into the DB."""

    self.annotateEntityDense ( corner, dim, annodata, conflictopt )


  def newEntityDense ( self, corner, dim, annodata, conflictopt ):
    """Add a new annotation associated with the cube of data.  Create new identifiers."""

    # TODO rewrite volume with identifiers
    self.annotateEntityDense ( corner, dim, annodata, conflictopt )



  #
  #  Return a cube of data from the database
  #  Must account for zeros.
  #
  def cutout ( self, corner, dim, resolution ):
    """Extract a cube of arbitrary size.  Need not be aligned."""

    # Not doign anything with resolution yet.

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
    dbname = self.annoproj.getAnnotationsTbl()
    cursor = self.conn.cursor()
    sql = "SELECT zindex, cube from " + dbname + " where zindex in (%s)" 
    # creats a %s for each list element
    in_p=', '.join(map(lambda x: '%s', listofidxs))
    # replace the single %s with the in_p string
    sql = sql % in_p
    rc = cursor.execute(sql, listofidxs)

    # xyz offset stored for later use
    lowxyz = zindex.MortonXYZ ( listofidxs[0] )

    # Get the objects and add to the cube
    while ( True ):

      try: 
        idx, datastring = cursor.fetchone()
      except:
        break

      #add the query result cube to the bigger cube
      curxyz = zindex.MortonXYZ(int(idx))
      offset = [ curxyz[0]-lowxyz[0], curxyz[1]-lowxyz[1], curxyz[2]-lowxyz[2] ]


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


  #
  # getVoxel -- return the identifier at a voxel
  #
  #
  def getVoxel ( self, voxel ):
    """Return the identifier at a voxel"""

    # convert the voxel into zindex and offsets
    # Round to the nearest larger cube in all dimensions
    xyzcube = [ voxel[0]/self.xcubedim, voxel[1]/self.ycubedim, (voxel[2]-self.startslice)/self.zcubedim ]
    xyzoffset =[ voxel[0]%self.xcubedim, voxel[1]%self.ycubedim, (voxel[2]-self.startslice)%self.zcubedim ]

    # Create a cube object
    cube = anncube.AnnotateCube ( self.cubedim )

    mortonidx = zindex.XYZMorton ( xyzcube )

    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT cube FROM " + self.annoproj.getAnnotationsTbl() + " WHERE zindex = " + str(mortonidx)
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error reading annotation data: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    row = cursor.fetchone ()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      retval = 0
    else: 
      cube.fromNPZ ( row[0] )
      retval = cube.getVoxel ( xyzoffset )

    cursor.close()
     
    return retval

  #
  # getLocations -- return the list of locations associated with an identifier
  #
  # PYTODO
  #
  def getLocations ( self, locations ):
    """Return the list of locations associated with an identifier"""
    pass

