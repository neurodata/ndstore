import urllib2
import cStringIO
import sys
import os
import tempfile
import h5py
import random 
import csv
import numpy as np
import pytest

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
sys.path += [ EM_EMCA_PATH ]

#SITE_HOST = 'openconnecto.me'
SITE_HOST = 'localhost:8000'
#SITE_HOST = 'localhost'

import emcaproj

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class TestRamon:

  # Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""

    self.pd = emcaproj.EMCAProjectsDB()
    self.pd.newEMCAProj ( 'unittest', 'test', 'localhost', 'unittest', 2, 'kasthuri11', None, False, True )

  def teardown_class (self):
    """Destroy the unittest database"""
    print "in teardown_class"
    self.pd.deleteEMCADB ('unittest')


  def test_anno(self):
    """Upload a minimal and maximal annotation.  Verify fields."""

    """Test 1: Create a minimal HDF5 file"""
    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    h5fh = h5py.File ( tmpfile.name )

    # Create the top level annotation id namespace
    idgrp = h5fh.create_group ( str(0) )

    h5fh.flush()
    tmpfile.seek(0)

    # Build the put URL
    url = "http://%s/emca/%s/" % ( SITE_HOST, 'unittest')

    # write an object (server creates identifier)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
    putid1 = int(response.read())
    
    # retrieve the annotation
    url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid1))
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )

    idgrpret = h5ret.get(str(putid1))
    assert idgrpret
    assert ( idgrpret['ANNOTATION_TYPE'][0] == 1 )
    assert not idgrpret.get('RESOLUTION')
    assert not idgrpret.get('XYZOFFSET')
    assert not idgrpret.get('VOXELS')
    assert not idgrpret.get('CUTOUT')
    mdgrpret = idgrpret['METADATA']
    assert mdgrpret
    assert ( mdgrpret['CONFIDENCE'][0] == 0.0 )
    assert ( mdgrpret['STATUS'][0] == 0 )
    assert ( mdgrpret['KVPAIRS'][:] == '' )
    assert ( mdgrpret['AUTHOR'][:] == 'unknown' )

    """Test 2: Create a fully populated HDF5 file"""
    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    # now lets add a bunch of random values for the specific annotation type
    ann_status = random.randint(0,4)
    ann_confidence = random.random()
    ann_author = 'unittest_author'

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=1 )

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    h5fh.flush()
    tmpfile.seek(0)

    # Build the put URL
    url = "http://%s/emca/%s/" % ( SITE_HOST, 'unittest')

    # write an object (server creates identifier)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
    putid2 = int(response.read())

    # retrieve the annotation
    url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid2))
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )

    idgrpret = h5ret.get(str(putid2))
    assert idgrpret
    assert ( idgrpret['ANNOTATION_TYPE'][0] == 1 )
    assert not idgrpret.get('RESOLUTION')
    assert not idgrpret.get('XYZOFFSET')
    assert not idgrpret.get('VOXELS')
    assert not idgrpret.get('CUTOUT')
    mdgrpret = idgrpret['METADATA']
    assert mdgrpret
    assert ( abs(mdgrpret['CONFIDENCE'][0] - ann_confidence) < 0.0001 )
    assert ( mdgrpret['STATUS'][0] == ann_status )
    assert ( mdgrpret['AUTHOR'][:] == ann_author )

    tmpfile.close()


    """Test 3: Update the file with new data"""

    tmpfile = tempfile.NamedTemporaryFile()
    h5fh = h5py.File ( tmpfile.name )

    # Create the top level annotation id namespace
    idgrp = h5fh.create_group ( str(putid2) )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    # now lets add a bunch of random values for the specific annotation type
    ann_status = random.randint(0,4)
    ann_confidence = random.random()
    ann_author = 'unittest_author2'

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=1 )

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    h5fh.flush()
    tmpfile.seek(0)

    # Build the put URL
    url = "http://%s/emca/%s/update/" % ( SITE_HOST, 'unittest')

    # write an object (server creates identifier)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
    putid3 = int(response.read())

    # retrieve the annotation
    url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid3))
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( tmpfile.name, driver='core', backing_store=False )

    idgrpret = h5ret.get(str(putid3))
    assert idgrpret
    assert ( idgrpret['ANNOTATION_TYPE'][0] == 1 )
    assert not idgrpret.get('RESOLUTION')
    assert not idgrpret.get('XYZOFFSET')
    assert not idgrpret.get('VOXELS')
    assert not idgrpret.get('CUTOUT')
    mdgrpret = idgrpret['METADATA']
    assert mdgrpret
    assert ( mdgrpret['CONFIDENCE'][0] == ann_confidence )
    assert ( mdgrpret['STATUS'][0] == ann_status )
    assert ( mdgrpret['AUTHOR'][:] == ann_author )


    """Test 4 delete the object"""
    # Build the delete URL
    url = "http://%s/emca/%s/delete/%s/" % ( SITE_HOST, 'unittest', putid3)
    import httplib
    conn = httplib.HTTPConnection ( "%s" % ( SITE_HOST ))
    conn.request ( 'DELETE', '/emca/%s/%s/' % ( 'unittest', putid3 ))
    resp = conn.getresponse()
    content=resp.read()

    assert content == 'Success'

    # retrieve the annotation
    # verify that it's not there.
    url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid3))
    with pytest.raises(urllib2.HTTPError): 
      urllib2.urlopen ( url )


#  def test_kvpairs(self):
#
#    """Test 1: Create a minimal HDF5 file"""
#    # Create an in-memory HDF5 file
#    tmpfile = tempfile.NamedTemporaryFile()
#    h5fh = h5py.File ( tmpfile.name )
#
#    # Create the top level annotation id namespace
#    idgrp = h5fh.create_group ( str(0) )
#
#    # Create a metadata group
#    mdgrp = idgrp.create_group ( "METADATA" )
#
#    kvpairs={}
#
#    # Turn our dictionary into a csv file
#    fstring = cStringIO.StringIO()
#    csvw = csv.writer(fstring, delimiter=',')
#    csvw.writerows([r for r in kvpairs.iteritems()])
#
#    # User-defined metadata
#    mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())
#
#    # Now put an empty file
#    # Build the put URL
#    url = "http://%s/emca/%s/" % ( SITE_HOST, 'unittest')
#
#    # write an object (server creates identifier)
#    req = urllib2.Request ( url, tmpfile.read())
#    response = urllib2.urlopen(req)
#    putid = int(response.read())
#
#    # now read and verify
#    # retrieve the annotation
#    url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid))
#    f = urllib2.urlopen ( url )
#    retfile = tempfile.NamedTemporaryFile ( )
#    retfile.write ( f.read() )
#    retfile.tell()
#    h5ret = h5py.File ( tmpfile.name, driver='core', backing_store=False )
#
#    mdgrpret = idgrpret['METADATA']
#    idgrpret = h5ret.get(str(putid1))
#
#    assert ( mdgrpret['KVPAIRS'][:] == '' )
#
#    for i in range(10):



#
#  def test_synapse(self):
#    pass
#
#  def test_segment(self):
#    pass
#
#  def test_seed(self):
#    pass  
##
#  def test_neuron(self):
#    pass
#
#  def test_organelle(self):
#    pass
#
#  def test_kvpairs(self):
#    pass
#
#
  def H5AnnotationFile ( self, annotype, annoid ):
    """Create an HDF5 file and populate the fields. Return a file object.
        This is a support routine for all the RAMON tests."""

    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    h5fh = h5py.File ( tmpfile.name )

    # Create the top level annotation id namespace
    idgrp = h5fh.create_group ( str(annoid) )

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    # now lets add a bunch of random values for the specific annotation type
    ann_status = random.randint(0,4)
    ann_confidence = random.random()
    ann_author = 'randal'

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    # Synapse:
    if annotype == 2:

      syn_weight = random.random()*1000.0
      syn_synapse_type = random.randint(1,9)
      syn_seeds = [ random.randint(1,1000) for x in range(5) ]
      syn_segments = [ [random.randint(1,1000),random.randint(1,1000)] for x in range(4) ]

      mdgrp.create_dataset ( "WEIGHT", (1,), np.float, data=syn_weight )
      mdgrp.create_dataset ( "SYNAPSE_TYPE", (1,), np.uint32, data=syn_synapse_type )
      mdgrp.create_dataset ( "SEEDS", (len(syn_seeds),), np.uint32, data=syn_seeds )
      mdgrp.create_dataset ( "SEGMENTS", (len(syn_segments),2), np.uint32, data=syn_segments)

    # Seed
    elif annotype == 3:

      seed_parent = random.randint(1,1000)
      seed_position = [ random.randint(1,10000) for x in range(3) ]
      seed_cubelocation = random.randint(1,9)
      seed_source = random.randint(1,1000)

      mdgrp.create_dataset ( "PARENT", (1,), np.uint32, data=seed_parent )
      mdgrp.create_dataset ( "CUBE_LOCATION", (1,), np.uint32, data=seed_cubelocation )
      mdgrp.create_dataset ( "SOURCE", (1,), np.uint32, data=seed_source )    
      mdgrp.create_dataset ( "POSITION", (3,), np.uint32, data=seed_position )

    # Segment
    elif annotype == 4:
       
      seg_parentseed = random.randint(1,100000)
      seg_segmentclass = random.randint(1,9)
      seg_neuron = random.randint(1,100000)
      seg_synapses = [ random.randint(1,100000) for x in range(5) ]
      seg_organelles = [ random.randint(1,100000) for x in range(5) ]

      mdgrp.create_dataset ( "SEGMENTCLASS", (1,), np.uint32, data=seg_segmentclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=seg_parentseed )
      mdgrp.create_dataset ( "NEURON", (1,), np.uint32, data=seg_neuron )
      mdgrp.create_dataset ( "SYNAPSES", (len(seg_synapses),), np.uint32, seg_synapses )
      mdgrp.create_dataset ( "ORGANELLES", (len(seg_organelles),), np.uint32, seg_organelles )

    # Neuron
    elif annotype == 5:

      neuron_segments = [ random.randint(1,1000) for x in range(10) ]
      mdgrp.create_dataset ( "SEGMENTS", (len(neuron_segments),), np.uint32, neuron_segments )

    # Organelle
    elif annotype == 6:

      org_parentseed = random.randint(1,100000)
      org_organelleclass = random.randint(1,9)
      org_seeds = [ random.randint(1,100000) for x in range(5) ]
      org_centroid = [ random.randint(1,10000) for x in range(3) ]

      mdgrp.create_dataset ( "ORGANELLECLASS", (1,), np.uint32, data=org_organelleclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=org_parentseed )
      mdgrp.create_dataset ( "SEEDS", (len(org_seeds),), np.uint32, org_seeds )
      mdgrp.create_dataset ( "CENTROID", (3,), np.uint32, data=org_centroid )

    h5fh.flush()
    tmpfile.seek(0)
    return tmpfile


  def getH5id ( self, f ):
    """Extract annotation id from the HDF5 file"""
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( f.read() )
    tmpfile.tell()
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )
    keys = h5f.keys()
    tmpfile.close()
    return int (keys[0])

  def test_updown( self ):
    """Upload all different kinds of annotations and retrieve"""

    for anntype in [ 1, 2, 3, 4, 5, 6]:
      
      annoid = 0
      fobj = self.H5AnnotationFile ( anntype, annoid )

      # Build the put URL
      url = "http://%s/emca/%s/" % ( SITE_HOST, 'unittest')

      # write an object (server creates identifier)
      req = urllib2.Request ( url, fobj.read())
      response = urllib2.urlopen(req)
      putid1 = int(response.read())

      # write an object (we choose identifier)
      #  this assumes that +1 is available (which it is)
      newid = putid1 + 1
      fobj = self.H5AnnotationFile ( anntype, newid )

      req = urllib2.Request ( url, fobj.read())
      response = urllib2.urlopen(req)
      putid2 = int(response.read())

      # retrieve both annotations
      url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid1))
      f = urllib2.urlopen ( url )
      getid1 = self.getH5id ( f )
   
      assert ( getid1 == putid1 )

      url = "http://%s/emca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid2))
      req = urllib2.Request ( url )
      f = urllib2.urlopen ( url )
      getid2 = self.getH5id ( f )

      assert ( getid2 == putid2 )

