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

import os
import sys
import argparse
import tempfile

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import h5py
import MySQLdb
import numpy as np
from celery import Celery
from contextlib import closing

import h5ann
import annotation
import ocpcarest
import ocpcaproj
import ocpcadb

from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

def writeDataSSD( webargs, postdata ):
  """ Write hdf5 files to SSD """

  [ token, sym, optionsargs ] = webargs.partition ('/')
  #any_db = anydbm.open( ocpcaprivate.ssd_log_location+ocpcaprivate.bsd_name, 'c' )
  any_db = None
  import time
  import pdb; pdb.set_trace()

  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )

  with closing ( ocpcadb.OCPCADB(proj) ) as db:

    # Don't write to readonly projects
    if proj.getReadOnly()==1:
      logger.warning("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))
      raise OCPCAError("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))

    # return string of id values
    retvals = []
 
    # Make a named temporary file for the HDF5
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( postdata )
    tmpfile.seek(0)
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )
 
    # get the conflict option if it exists
    options = optionsargs.split('/')
    if 'preserve' in options:
      conflictopt = 'P'
    elif 'exception' in options:
      conflictopt = 'E'
    else:
      conflictopt = 'O'

    try:

      for k in h5f.keys():

        # Convert HDF5 to annotation
        idgrp = h5f.get(k)
        anno = h5ann.H5toAnnotation ( k, idgrp, db )
        # set the identifier (separate transaction)
        if not ('update' in options or 'dataonly' in options or 'reduce' in options):
          anno.setID ( db )
        # start a transaction: get mysql out of line at a time mode
        db.startTxn ()

        try:

          if anno.__class__ in [ annotation.AnnNeuron, annotation.AnnSeed ] and ( idgrp.get('VOXELS') or     idgrp.get('CUTOUT')):
            logger.warning ("Cannot write to annotation type %s" % (anno.__class__))
            raise OCPCAError ("Cannot write to annotation type %s" % (anno.__class__))
          if 'update' in options and 'dataonly' in options:
            logger.warning ("Illegal combination of options. Cannot use udpate and dataonly together")
            raise OCPCAError ("Illegal combination of options. Cannot use udpate and dataonly together")
          elif not 'dataonly' in options and not 'reduce' in options:

            db.putAnnotation ( anno, options )
            
          #  Get the resolution if it's specified
          if 'RESOLUTION' in idgrp:
            resolution = int(idgrp.get('RESOLUTION')[0])
          
          # Load the data associated with this annotation
          #  Is it voxel data?
          if 'VOXELS' in idgrp:
            voxels = np.array(idgrp.get('VOXELS'),dtype=np.uint32)
          else:
            voxels = None
          
          if voxels!=None and 'reduce' not in options:
            
            if 'preserve' in options:
              conflictopt = 'P'
            elif 'exception' in options:
              conflictopt = 'E'
            else:
              conflictopt = 'O'
            # Check that the voxels have a conforming size:
            if voxels.shape[1] != 3:
              logger.warning ("Voxels data not the right shape.Must be (:,3).Shape is {}".format(voxels.shape))
              raise OCPCAError ("Voxels data not the right shape.Must be (:,3).Shape is %s".format(voxels.shape))
            
            ds = datastream.DataStream()
            import pdb; pdb.set_trace()
            ds.insert(anno)

        # rollback if you catch an error
        except MySQLdb.OperationalError, e:
          logger.warning (" Put Anntotation: Transaction did not complete. %s" % (e))
          db.rollback()
          continue
        except MySQLdb.Error, e:
          logger.warning ("Put Annotation: Put transaction rollback. %s" % (e))
          db.rollback()
          raise
        except Exception, e:
          logger.exception ("Put Annotation:Put transaction rollback. %s" % (e))
          db.rollback()
          raise
        # Commit if there is no error
        db.commit()
        
    finally:
      h5f.close()
      tmpfile.close()
            conflictopt = 'O'

          # the zstart in datasetcfg is sometimes offset to make it aligned.
          # Probably remove the offset is the best idea and align the data to zero regardless of where it starts.
          # for now.

          corner = h5xyzoffset[:]
          # RBISO?? apply offsets?

          db.annotateEntityDense ( anno.annid, corner, resolution, np.array(cutout), conflictopt )

        elif cutout != None and h5xyzoffset != None and 'reduce' in options:

          corner = h5xyzoffset[:]
          # RBISO?? apply offsets?

        elif cutout != None or h5xyzoffset !=None:
          #TODO this is a loggable error
          pass

        # only add the identifier if you commit
        if not 'dataonly' in options and not 'reduce' in options:
          retvals.append ( anno.annid )

        os.remove( fileName )

        # Here with no error is successful
        print " Done successfully :", anno.annid
        print time.time()-start

      except MySQLdb.OperationalError, e:
        logger.warning ( "Put Annotation: Transaction did not complete. {}".format(e) )
        continue
      except MySQLdb.Error, e:
        logger.warning ( "Put Annotation: Put transaction rollback. {}".format(e) )
        rsybaise
      except OSError , e:
        logger.warning ( "Cannot unlink file from system. {}".format(e) )
      except Exception, e:
        logger.warning ( "Put Annotation: Put transaction rollback. {}".format(e) )
        raise
