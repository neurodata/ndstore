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

      
def ingestSWC ( swcfile, ch, db ):
  """Ingest the SWC file into a database.  This will involve:
        parsing out separate connected components as skeletons
        deduplicating nodes (for Vaa3d) """     

  # dictionary of skeletons by parent node id
  skels = {}
  # dictionary that tracks the previously seen roots
  noderoot = {}

  # list of nodes in the swc file.
  nodelist=[]

  # comment in the 
  comments = []

  for line in swcfile:

    # Store comments as KV 
    if re.match ( '^#.*$', line ):
      comments.append(line)
    else:

      # otherwise, parse the record according to SWC 
      # n T x y z R P
      ( nodeid, nodetype, xpos, ypos, zpos, radius, parentid )  = line.split()

      # first check if it is a duplicate node

      # if it's a root node create a new skeleton
      if int(parentid) == -1: 

        # Create a skeleton
        skels[nodeid] = annotation.AnnSkeleton ( db )
        # assign an identifier
        skels[nodeid].setField('annid', db.nextID(ch))

        # set the node root to itself
        noderoot[nodeid] = nodeid

      else:

        # update the noderoot dictionary
        noderoot[nodeid]=noderoot[parentid]

      # create a node
      node = annotation.AnnNode( db ) 
      node.setField ( 'skeletonid', skels[noderoot[nodeid]].annid )
      node.setField ( 'annid', db.nextID(ch) )
      node.setField ( 'nodetype', nodetype )
      node.setField ( 'location', (xpos,ypos,zpos) )
      node.setField ( 'radius', radius )
      node.setField ( 'parentid', parentid )

      nodelist.append(node)

      # set the skeleton rootnode to the nodes
      if int(parentid) == -1:
        skels[nodeid].setField('rootnode', node.getField('annid'))


  # having parsed the whole file, send to DB in a transaction
  db.startTxn()
  cursor = db.getCursor()

  # store the skeletons
  for (nodeid, skel) in skels.iteritems():

    # add comments to each skeleton KV pair
    commentno = 0
    for comment in comments:
      skel.kvpairs[commentno] = comment
      commentno += 1

    skel.store( ch, cursor )

  # store the nodes
  for node in nodelist:
    node.store( ch, cursor )

  db.commit()

  return [ x.annid for (i,x) in skels.iteritems() ]


def querySWC ( swcfile, ch, db, proj, skelids=None ):
  """Query the list of skelids (skeletons) and populate an open file swcfile
     with lines of swc data."""

  try:

    cursor = db.getCursor()
    db.startTxn()

    # write out metadata about where this came from
    # OCP version number and schema number
    f.write('# OCP (Open Connectome Project) Version {} Schema {}'.format(proj.getOCPVersion(),proj.getSchemaVersion()))
    # OCP project and channel
    f.write('# Project {} Channel {}'.format(proj.getProjectName(),ch.getChannelName()))

    # get a skeleton for metadata and populate the comments field
    if skelids != None and len(skelids)==0:

      skel == annotation.Skeleton( db )
      skel.retrieve ( ch, skelids[0], cursor )

      # write each key value line out as a comment
      for (k,v) in skel.getKVPairs():
        # match a comment
        if re.match ( "^#.*", v ):
          fwrite(v)
        else:
          fwrite("# {} {}".format(k,v))
      
    nodegen = db.queryNodes ( skelids )
    # iterate over all nodes
    for node in nodegen: 
      skeletonid = node.getField ( 'skeletonid' )
      annid = node.getField ( 'annid' ) 
      nodetype = node.getField ( 'nodetype')
      (xpos,ypos,zpos) = node.getField ( 'location')
      radius = node.getField ( 'radius')
      parentid = node.getField ( 'parentid')

    # write an node in swc
    # n T x y z R P
#    fwrite ( "{} {} {} {} {} {} {} {}".format ( annid, nodetype,  ,,,,, parentid ))

    db.commit()

  finally:
    db.closeCursor()

