
# RB Functions that do not seem to follow our proper decomposiition.
# and got thrown out of spatialdb

  def getNextCube ( self ):
    """ Retrieve the next cube in a queryRange. Not thread safe (context per object) """

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ self._qr_resolution ] 

    # Create a cube object
    cube = anncube.AnnotateCube ( cubedim )

    row = self._qr_cursor.fetchone()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      cube.zeros ()
      self._qr_cursor.close()
      return [None,None]
    else: 
      # decompress the cube
      if self.NPZ:
        cube.fromNPZ ( row[1] )
      else:
        cube.fromBlosc ( row[1] )
      return [row[0],cube]



  # RB needs to be moved to mysql???
  def getAllExceptions ( self, key, resolution ):
    """Load all exceptions for this cube"""

    # get the block from the database
    cursor = self.getCursor()
    sql = "SELECT id, exlist FROM %s where zindex=%s" % ( 'exc'+str(resolution), key )
    try:
      cursor.execute ( sql )
      excrows = cursor.fetchall()
    except MySQLdb.Error, e:
      logger.error ( "Error reading exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor ( cursor )

    # Parse and unzip all of the exceptions    
    excs = []
    if excrows == None:
      return []
    else:
      for excstr in excrows:
        excs.append ((np.uint32(excstr[0]), np.load(cStringIO.StringIO(zlib.decompress(excstr[1])))))
      return excs

