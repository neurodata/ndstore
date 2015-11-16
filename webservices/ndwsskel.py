# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
#Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

import annotation

from ndtype import ISOTROPIC

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

      
def ingestSWC ( res, swcfile, ch, db ):
  """Ingest the SWC file into a database.  This will involve:
        parsing out separate connected components as skeletons
        deduplicating nodes (for Vaa3d) """     

  # dictionary of skeletons by parent node id
  skels = {}

  # list of nodes in the swc file.
  nodes={}

  # comment in the swcfiles
  comments = []

  try:

    # number of ids to create.  do them all at once.
    idsneeded = 0

    # first pass of the file
    for line in swcfile:

      # find how many ids we need
      if not re.match ( '^#.*$', line ):

        # otherwise, parse the record according to SWC 
        # n T x y z R P
        ( swcnodeidstr, nodetype, xpos, ypos, zpos, radius, swcparentidstr )  = line.split()
        swcnodeid = int(swcnodeidstr)
        swcparentid = int(swcparentidstr)

        if swcparentid == -1:
          idsneeded += 2
        else:
          idsneeded += 1

    # reserve ids
    lowid = db.reserve ( ch, idsneeded )

    # reset file pointer for second pass
    swcfile.seek(0)

    # second pass to ingest the field
    for line in swcfile:
  
      # Store comments as KV 
      if re.match ( '^#.*$', line ):
        comments.append(line)
      else:

        # otherwise, parse the record according to SWC 
        # n T x y z R P
        ( swcnodeidstr, nodetype, xpos, ypos, zpos, radius, swcparentidstr )  = line.split()
        swcnodeid = int(swcnodeidstr)
        swcparentid = int(swcparentidstr)

        # scale points to resolution 
        xpos = float(xpos)*(2**res) 
        ypos = float(ypos)*(2**res) 
        # check for isotropic
        if db.datasetcfg.scalingoption == ISOTROPIC:
          zpos = float(zpos)*(2**res) 
        else:
          zpos = float(zpos)

        # create a node
        node = annotation.AnnNode( db ) 

        node.setField ( 'annid', lowid )
        lowid += 1
        node.setField ( 'nodetype', nodetype )
        node.setField ( 'location', (xpos,ypos,zpos) )
        node.setField ( 'radius', radius )
        if swcparentid == -1:
          node.setField ( 'parentid', -1 )
        else:
          node.setField ( 'parentid', nodes[swcparentid].getField('annid'))

        nodes[swcnodeid] = node

        # if it's a root node create a new skeleton
        if swcparentid == -1: 

          # Create a skeleton
          skels[swcnodeid] = annotation.AnnSkeleton ( db )

          # assign an identifier
          skels[swcnodeid].setField('annid', lowid)

          # assign sekeleton id for the node
          node.setField ( 'skeletonid', lowid )

          # increment the id
          lowid += 1

        else:

          # set to skelton id of parent
          node.setField ( 'skeletonid', nodes[swcparentid].getField('skeletonid') )

  except Exception, e:
    logger.warning("Failed to put SWC file {}".format(e))
    raise NDWSError("Failed to put SWC file {}".format(e))

  # having parsed the whole file, send to DB in a transaction
  db.startTxn()
  cursor = db.getCursor()

  # store the skeletons
  for (skelid, skel) in skels.iteritems():

    # add comments to each skeleton KV pair
    commentno = 0
    for comment in comments:
      skel.kvpairs[commentno] = comment
      commentno += 1

    skel.store( ch, cursor )

  # store the nodes
  for (nodeid,node) in nodes.iteritems():
    node.store( ch, cursor )

  db.commit()

  return [ x.annid for (i,x) in skels.iteritems() ]


def querySWC ( res, swcfile, ch, db, proj, skelids=None ):
  """Query the list of skelids (skeletons) and populate an open file swcfile
     with lines of swc data."""

  try:

    cursor = db.getCursor()
    db.startTxn()

    # write out metadata about where this came from
    # ND version number and schema number
    swcfile.write('# ND (NeuroData) Version {} Schema {}\n'.format(proj.getNDVersion(),proj.getSchemaVersion()))
    # ND project and channel
    swcfile.write('# Project {} Channel {}\n'.format(proj.getProjectName(),ch.getChannelName()))

    # get a skeleton for metadata and populate the comments field
    if skelids != None and len(skelids)==0:

      skel == annotation.Skeleton( db )
      skel.retrieve ( ch, skelids[0], cursor )

      # write each key value line out as a comment
      for (k,v) in skel.getKVPairs():
        # match a comment
        if re.match ( "^#.*", v ):
          swcfile.write(v)
        else:
          swcfile.write("# {} {}".format(k,v))
      
    nodegen = annotation.nodesBySkeleton ( ch, skelids, db, cursor )

    # iterate over all nodes
    for node in nodegen: 

      (annid, nodetype, xpos, ypos, zpos, radius, parentid) = node

      # scale points to resolution 
      xpos = xpos/(2**res) 
      ypos = ypos/(2**res) 
      # check for isotropic
      if db.datasetcfg.scalingoption == ISOTROPIC:
        zpos = zpos/(2**res) 

      # write an node in swc
      # n T x y z R P
      swcfile.write ( "{} {} {} {} {} {} {}\n".format ( annid, nodetype, xpos, ypos, zpos, radius, parentid ))

    db.commit()

  finally:
    db.closeCursor(cursor)

