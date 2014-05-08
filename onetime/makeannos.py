import urllib2
import argparse
import numpy as np
import cStringIO
import sys
import tempfile
import h5py


def main():

  parser = argparse.ArgumentParser(description='Create emptuy annotations')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('low', action="store", type=int )
  parser.add_argument('high', action="store", type=int )

  result = parser.parse_args()

  for annid in range ( result.low, result.high ):

    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    h5fh = h5py.File ( tmpfile.name )

    # Create the top level annotation id namespace
    idgrp = h5fh.create_group ( str(annid) )

    ann_type = 1

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=ann_type )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    ann_status = 0
    ann_author = 'autoingest'

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )


    url = "http://%s/emca/%s/" % ( result.baseurl, result.token)
    print url

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


