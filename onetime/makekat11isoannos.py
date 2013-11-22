import urllib2
import argparse
import numpy as np
import cStringIO
import sys
import tempfile
import h5py
import re
import csv

#RBTODO why does this break on 247 with isoaxons

"""Import the axons from a VAST file into RAMON objects"""

def main():

  parser = argparse.ArgumentParser(description='Create annotations for kat11isoaxons')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('file', action="store")

  result = parser.parse_args()

  fh = open ( result.file, "r" )

  for line in fh:

    # skip comments 
    if re.match("^\s*%", line) or re.match("^\s*$",line):
      continue

    metadata = line.split(None, 24)
    annid = int(metadata[0]) 

    if annid == 0:
      continue

    mstring = metadata[24]
    mobj = re.search('[\w\s]+', mstring)
    kv_value = mobj.group(0)

    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    h5fh = h5py.File ( tmpfile.name )

    # Create the top level annotation id namespace
    idgrp = h5fh.create_group ( str(annid) )

    ann_type = 4

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=ann_type )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    ann_status = 0
    ann_author = 'N. Kasthuri'

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    kvpairs={}
    kvpairs['sourceId']=str(annid)
    kvpairs['sourceDescription']=kv_value

    # Turn our dictionary into a csv file
    fstring = cStringIO.StringIO()
    csvw = csv.writer(fstring, delimiter=',')
    csvw.writerows([r for r in kvpairs.iteritems()])

    # User-defined metadata
    mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())

    url = "http://%s/emca/%s/" % ( result.baseurl, result.token)
    print url, kvpairs

    h5fh.flush()
    tmpfile.seek(0)

    try:
      req = urllib2.Request ( url, tmpfile.read()) 
      response = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print "Failed URL", url
      print "Error %s" % (e) 
      sys.exit(0)

    the_page = response.read()
    print "Success with id %s" % the_page
    tmpfile.close()

if __name__ == "__main__":
  main()


