import urllib2
import sys
import os
import tempfile
import h5py
import numpy as np

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
sys.path += [ EM_EMCA_PATH ]

def makeAnno ( anntype, hosturl ):
  """Helper make an annotation"""

  # Create an annotation
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

  # Create the top level annotation id namespace
  idgrp = h5fh.create_group ( str(0) )
  mdgrp = idgrp.create_group ( "METADATA" )
  ann_author='Unit Test'
  mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

  idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=anntype )

  h5fh.flush()
  tmpfile.seek(0)

  # Build the put URL
  url = "http://%s/emca/%s/" % ( hosturl, 'unittest')

  # write an object (server creates identifier)
  req = urllib2.Request ( url, tmpfile.read())
  response = urllib2.urlopen(req)
  putid = int(response.read())

  tmpfile.close()

  return putid
  
