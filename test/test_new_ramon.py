# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
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

import urllib2
import re
import tempfile
import h5py
import random 
import csv
import numpy as np
import pytest
import httplib
from contextlib import closing

from pytesthelpers import makeAnno

from params import Params
import kvengine_to_test
import site_to_test
import makeunitdb
SITE_HOST = site_to_test.site


class TestRamon:


  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB('unittest', readonly=0)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB('unittest')

  def putAnnotation (self, f, update=False ):
    """Put the specified Annotation"""
    
    # Build the put URL
    if update:
      url = "http://{}/ca/{}/{}/update/".format(SITE_HOST, 'unittest', 'unit_anno')
    else:
      url = "http://{}/ca/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno')
    # write an object (server creates identifier)
    req = urllib2.Request ( url, f.read())
    response = urllib2.urlopen(req)
    return int(response.read())

  def getAnnotation (self, putid):
    """Get the specified Annotation"""
    # retrieve the annotation
    url = "http://{}/ca/{}/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno', putid)
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.seek(0)
    return h5py.File ( retfile.name, driver='core', backing_store=False )

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
    
    putid1 = self.putAnnotation(tmpfile)
    h5ret = self.getAnnotation(putid1)

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

    putid2 = self.putAnnotation(tmpfile)
    h5ret = self.getAnnotation(putid2)

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

    putid3 = self.putAnnotation(tmpfile, update=True)
    h5ret = self.getAnnotation(putid3)

    idgrpret = h5ret.get(str(putid3))
    assert idgrpret
    assert ( idgrpret['ANNOTATION_TYPE'][0] == 1 )
    assert not idgrpret.get('RESOLUTION')
    assert not idgrpret.get('XYZOFFSET')
    assert not idgrpret.get('VOXELS')
    assert not idgrpret.get('CUTOUT')
    mdgrpret = idgrpret['METADATA']
    assert mdgrpret
    assert ( abs(mdgrpret['CONFIDENCE'][0] - ann_confidence) < 0.0001 )
    #assert ( mdgrpret['CONFIDENCE'][0] == ann_confidence )
    assert ( mdgrpret['STATUS'][0] == ann_status )
    assert ( mdgrpret['AUTHOR'][:] == ann_author )


    """Test 4 delete the object"""
    # Build the delete URL

    # Check if it's an HTTPS conncetion
#    m = re.match('http(s?)://(.*)', SITE_HOST)
#    if m.group(1) == 's':
#      conn = httplib.HTTPSConnection ( "%s" % ( m.group(2)))
#    else:
#      conn = httplib.HTTPConnection ( "%s" % ( m.group(2))

    try:
      (base,suffix) = SITE_HOST.split("/",1)
    except:
      base = SITE_HOST
      suffix = None

    conn = httplib.HTTPConnection ( base )

    if suffix:
      conn.request ('DELETE', '/{}/ca/{}/{}/{}/'.format(suffix, 'unittest', 'unit_anno', putid3)) 
    else:
      conn.request ('DELETE', '/ca/{}/{}/{}/'.format('unittest', 'unit_anno', putid3))

    resp = conn.getresponse()
    content=resp.read()

    assert content == 'Success'

    # retrieve the annotation
    # verify that it's not there.
    url = "http://{}/ca/{}/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno', putid3)
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
#    url = "http://%s/ca/%s/" % ( SITE_HOST, 'unittest')
#
#    # write an object (server creates identifier)
#    req = urllib2.Request ( url, tmpfile.read())
#    response = urllib2.urlopen(req)
#    putid = int(response.read())
#
#    # now read and verify
#    # retrieve the annotation
#    url = "http://%s/ca/%s/%s/" % ( SITE_HOST, 'unittest', str(putid))
#    f = urllib2.urlopen ( url )
#    retfile = tempfile.NamedTemporaryFile ( )
#    retfile.write ( f.read() )
#    retfile.seek(0)
#    h5ret = h5py.File ( tmpfile.name, driver='core', backing_store=False )
#
#    mdgrpret = idgrpret['METADATA']
#    idgrpret = h5ret.get(str(putid1))
#
#    assert ( mdgrpret['KVPAIRS'][:] == '' )
#
#    for i in range(10):



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
#    tmpfile.tell()
    tmpfile.seek(0)
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
      url = "http://{}/ca/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno')

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
      assert ( putid1 == self.getId(putid1) )
      assert ( putid2 == self.getId(putid2) )
  

  def getId ( self, putid ):
    """Get the annotation at this Id"""
    url = "http://{}/ca/{}/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno', putid)
    f = urllib2.urlopen ( url )
    return self.getH5id ( f )
  
  def getField (self, annid, field):
    """Get the specified field"""
    url =  "http://{}/ca/{}/{}/{}/getField/{}/".format(SITE_HOST, 'unittest', 'unit_anno', annid, field)
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    return f

  def setField ( self, annid, field, value ):
    """Set the specified field to the value"""
    url =  "http://{}/ca/{}/{}/{}/setField/{}/{}/".format(SITE_HOST, 'unittest', 'unit_anno', annid, field, value)
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    return f
    

  def test_fields (self):
    """Test the getField and setField"""

    # Make an annotation 
    annid = makeAnno ( 1, SITE_HOST )
    
    # Test Status
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 

    # Test confidence
    confidence = random.random ()
    f = self.setField(annid, 'confidence', confidence)
    assert f.read()==''
    f = self.getField(annid, 'confidence')
    assert confidence - float(f.read()) < 0.001
    
    # Test author
    f = self.getField(annid, 'author')
    assert 'Unit Test' == f.read()

    # Make a synapse
    annid = makeAnno ( 2, SITE_HOST )

    # Test synapse type
    synapse_type = random.randint (0,100)
    f = self.setField(annid, 'synapse_type', synapse_type)
    assert f.read()==''
    f = self.getField(annid, 'synapse_type')
    assert synapse_type == int(f.read()) 

    # Test the weight
    weight = random.random ()
    f = self.setField(annid, 'weight', weight)
    assert f.read()==''
    f = self.getField(annid, 'weight')
    assert weight - float(f.read()) < 0.001

    # Test the inheritance
    # set the status
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 

    # Make a seed
    annid = makeAnno ( 3, SITE_HOST )

    # Test the parent
    parent = random.randint (0,100)
    f = self.setField(annid, 'parent', parent)
    assert f.read()==''
    f = self.getField(annid, 'parent')
    assert parent == int(f.read()) 

    # Test the source
    source = random.randint (0,100)
    f = self.setField(annid, 'source', source)
    assert f.read()==''
    f = self.getField(annid, 'source')
    assert source == int(f.read()) 

    # Test the cubelocation
    cubelocation = random.randint (0,100)
    f = self.setField(annid, 'cubelocation', cubelocation)
    assert f.read()==''
    f = self.getField(annid, 'cubelocation')
    assert cubelocation == int(f.read()) 

    # Make a segment
    annid = makeAnno ( 4, SITE_HOST )

    # Test the parentseed
    parentseed = random.randint (0,100)
    f = self.setField(annid, 'parentseed', parentseed)
    assert f.read()==''
    f = self.getField(annid, 'parentseed')
    assert parentseed == int(f.read()) 

    # Test the segmentclass
    segmentclass = random.randint (0,100)
    f = self.setField(annid, 'segmentclass', segmentclass)
    assert f.read()==''
    f = self.getField(annid, 'segmentclass')
    assert segmentclass == int(f.read()) 

    # Test the neuron
    neuron = random.randint (0,100)
    f = self.setField(annid, 'neuron', neuron)
    assert f.read()==''
    f = self.getField(annid, 'neuron')
    assert neuron == int(f.read()) 

    # Test inheritance
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 

    # Make a neuron
    annid = makeAnno ( 5, SITE_HOST )
    # no independently set fields

    # Test inheritance
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 

    # Make an organelle 
    annid = makeAnno ( 6, SITE_HOST )

    # Test the parentseed
    parentseed = random.randint (0,100)
    f = self.setField(annid, 'parentseed', parentseed)
    assert f.read()==''
    f = self.getField(annid, 'parentseed')
    assert parentseed == int(f.read()) 

    # Test the organelleclass
    organelleclass = random.randint (0,100)
    f = self.setField(annid, 'organelleclass', organelleclass)
    assert f.read()==''
    f = self.getField(annid, 'organelleclass')
    assert organelleclass == int(f.read()) 

    # Test inheritance
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 

    # TODO error caes.
    #  bad format to a number
    url =  "http://{}/ca/{}/{}/{}/setField/status/aa/".format(SITE_HOST, 'unittest', 'unit_anno', annid)
    with pytest.raises(urllib2.HTTPError): 
      req = urllib2.Request ( url )
      f = urllib2.urlopen ( url )

# RBTODO add tests key/value and compound fields.
    #  assign a field for a wrong annotation type
#    url =  "http://%s/ca/%s/%s/setField/segmentclass/2/" % ( SITE_HOST, 'unittest',str(annid))
#    with pytest.raises(urllib2.HTTPError): 
#      req = urllib2.Request ( url )
#      f = urllib2.urlopen ( url )

    #  assign a missing field
#    url =  "http://%s/ca/%s/%s/setField/nonesuch/2/" % ( SITE_HOST, 'unittest',str(annid))
#    with pytest.raises(urllib2.HTTPError): 
#      req = urllib2.Request ( url )
#      f = urllib2.urlopen ( url )

    #  request a missing field
    url =  "http://{}/ca/{}/{}/{}/getField/othernonesuch/".format(SITE_HOST, 'unittest', 'unit_anno', annid)
    with pytest.raises(urllib2.HTTPError): 
      req = urllib2.Request ( url )
      f = urllib2.urlopen ( url )


  def test_last ( self ):
   
    # Make an annotation 
    annid = makeAnno ( 2, SITE_HOST )

    # Test the synapse type
    synapse_type = random.randint (0,100)
    f = self.setField(annid, 'synapse_type', synapse_type)
    assert f.read()==''
    f = self.getField( annid, 'synapse_type')
    assert synapse_type == int(f.read()) 

    # Test the weight
    weight = random.random ()
    f = self.setField(annid, 'weight', weight)
    assert f.read()==''
    f = self.getField( annid, 'weight')
    assert weight - float(f.read()) < 0.001

    # Test inheritance
    status = random.randint (0,100)
    f = self.setField(annid, 'status', status)
    assert f.read()==''
    f = self.getField( annid, 'status')
    assert status == int(f.read()) 
