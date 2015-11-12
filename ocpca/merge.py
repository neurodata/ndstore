

  def mergeGlobal(self, ch, ids, mergetype, res):
    """Global merge routine.  Converts a list of ids into the merge id at a given resolution.
       This will collapse all exceptions for the voxels for the merged ids."""

    # get the size of the image and cube
    resolution = int(res)
    # ID to merge annotations into 
    mergeid = ids[0]
    
    # Turned off for now( Will's request)
    #if len(self.annoIdx.getIndex(int(mergeid),resolution)) == 0:
    #  raise OCPCAError(ids[0] + " not a valid annotation id. This id does not have paint data")
  
    # Get the list of cubeindexes for the Ramon objects
    listofidxs = set()
    addindex = []
    # RB!!!! do this for all ids, promoting the exceptions of the merge id
    for annid in ids:
      if annid == mergeid:
        continue
      # Get the Annotation index for that id
      curindex = self.annoIdx.getIndex(ch, annid,resolution)
      # Final list of index which has to be updated in idx table
      addindex = np.union1d(addindex,curindex)
      # Merge the annotations in the cubes for the current id
      listofidxs = set(curindex)
      for key in listofidxs:
        cube = self.getCube (ch, key,resolution)
        if ch.getExceptions() == EXCEPTION_TRUE:
          oldexlist = self.getExceptions( ch, key, resolution, annid ) 
          self.kvio.deleteExceptions ( ch, key, resolution, annid )
        #
        # RB!!!!! this next line is wrong!  the problem is that
        #  we are merging all annotations.  So at the end, there
        #  need to be no exceptions left.  This line will leave
        #  exceptions with the same value as the annotation.
        #  Just delete the exceptions
        #
        # Ctype optimized version for mergeCube
        ocplib.mergeCube_ctype ( cube.data, mergeid, annid )
        self.putCube ( ch, key, resolution, cube )
        
      # Delete annotation and all it's meta data from the database
      #
      # RB!!!!! except for the merge annotation
      if annid != mergeid:
        try:
          # reordered because paint data no longer exists
          #KL TODO Merge for all resolutions and then delete for all of them.
          self.annoIdx.deleteIndexResolution(ch, annid,resolution)
          #self.annoIdx.deleteIndex(annid,resolution)
          self.deleteAnnotation (ch, annid, '' )
        except:
          logger.warning("Failed to delete annotation {} during merge.".format(annid))
    self.annoIdx.updateIndex(ch, mergeid,addindex,resolution)     
    self.kvio.commit()
    
    return "Merged Id's {} into {}".format(ids, mergeid)

  def merge2D(self, ids, mergetype, res, slicenum):
    # get the size of the image and cube
    resolution = int(res)
    print ids
    # PYTODO Check if this is a valid annotation that we are relabeling to
    if len(self.annoIdx.getIndex(ids[0],1)) == 0:
      raise OCPCAError(ids[0] + " not a valid annotation id")
    print mergetype
    listofidxs = set()
    for annid in ids[1:]:
      listofidxs |= set(self.annoIdx.getIndex(annid,resolution))

    return "Merge 2D"

  def merge3D(self, ids, corner, dim, res):
     # get the size of the image and cube
    resolution = int(res)
    dbname = self.proj.getTable(resolution)
    
    # PYTODO Check if this is a valid annotation that we are relabelubg to
    if len(self.annoIdx.getIndex(ids[0],1)) == 0:
      raise OCPCAError(ids[0] + " not a valid annotation id")

    listofidxs = set()
    for annid in ids[1:]:
      listofidxs |= set(self.annoIdx.getIndex(annid,resolution))

      # Perform the cutout
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ]

    # Get the Cutout
    cube = self.cutout(corner,dim,resolution)    
    vec_func = np.vectorize ( lambda x: ids[0] if x in ids[1:] else x )
    cube.data = vec_func ( cube.data )

    self.annotateDense ( corner, resolution, cube )    

    # PYTODO - Relabel exceptions?????

    # Update Index and delete object?
    for annid in ids[1:]:
      #Wself.annoIdx.deleteIndex(annid,resolution)
      print "updateIndex"

    return "Merge 3D"

  def exceptionsCutout ( self, corner, dim, resolution ):
    """Return a list of exceptions in the specified region.
        Will return a np.array of shape x,y,z,id1,...,idn where n is the longest exception list"""
  
    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    # Build a list of indexes to access                                                                                     
    listofidxs = []
    for z in range ( znumcubes ):
      for y in range ( ynumcubes ):
        for x in range ( xnumcubes ):
          mortonidx = ocplib.XYZMorton ( [x+xstart, y+ystart, z+zstart] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # generate list of ids for query
    sqllist = ', '.join(map(lambda x: str(x), listofidxs))
    sql = "SELECT zindex,id,exlist FROM exc{} WHERE zindex in ({})".format(resolution,sqllist)


    with closing(self.conn.cursor()) as func_cursor:

      # this query needs its own cursor
      try:
        func_cursor.execute(sql)
      except MySQLdb.Error, e:
        logger.warning ("Failed to query exceptions in cutout %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise

      # data structure to hold list of exceptions
      excdict = defaultdict(set)

      prevzindex = None

      while ( True ):

        try: 
          cuboidzindex, annid, zexlist = func_cursor.fetchone()
        except:
          func_cursor.close()
          break

        # first row in a cuboid
        if np.uint32(cuboidzindex) != prevzindex:
          prevzindex = cuboidzindex
          # data for the current cube
          cube = self.getCube ( cuboidzindex, resolution )
          [ xcube, ycube, zcube ] = ocplib.MortonXYZ ( cuboidzindex )
          xcubeoff =xcube*xcubedim
          ycubeoff =ycube*ycubedim
          zcubeoff =zcube*zcubedim

        # accumulate entries and decompress the list of exceptions
        fobj = cStringIO.StringIO ( zlib.decompress(zexlist) )
        exlist = np.load (fobj)

        for exc in exlist:
          excdict[(exc[0]+xcubeoff,exc[1]+ycubeoff,exc[2]+zcubeoff)].add(np.uint32(annid))
          # add voxel data 
          excdict[(exc[0]+xcubeoff,exc[1]+ycubeoff,exc[2]+zcubeoff)].add(cube.data[exc[2]%zcubedim,exc[1]%ycubedim,exc[0]%xcubedim])


    # Watch out for no exceptions
    if len(excdict) != 0:

      maxlist = max([ len(v) for (k,v) in excdict.iteritems() ])
      exoutput = np.zeros([len(excdict),maxlist+3], dtype=np.uint32)

      i=0
      for k,v in excdict.iteritems():
        l = len(v)
        exoutput[i,0:(l+3)] = [x for x in itertools.chain(k,v)]
        i+=1

    # Return None if there are no exceptions.
    else:
      exoutput = None

    return exoutput

