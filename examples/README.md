### Example scripts that demonstrate how to use the service.

##### Unsupported scripts

* Used for internal testing only now.

  1. addCubeIndex.py
  2. cutout.py
  3. getId.py

##### RAMON Interfaces

* XXXwrite.py -- write a randomly generated RAMON object to the database
* XXX = synapse, segment, neuron, seed, or anno (anno=minimal object)
* annoread.py -- read a ramon object from a database polymorphically there are options to fetch data as voxels or cutout

##### Other Queries

* listofids.py -- fetch all annotations matching type and status criteria this is a metadata only query

##### Data Annotation

* addcube/denseaddcube.py -- write an annotation to the database specified as a cube using either dense or sparse interfaces
* addcube/denseaddcube.py -- write an annotation to the database specified as a cube using either dense or sparse interfaces
* [dense]anno[black|white].py -- sparse or dense interfaces to read a cutout from a database and write annotations of the same shape.  These are still pretty customized for hayworth5nm and probably not the usable.

##### Deprecated scripts in deprecated

* hdf5MakePNGs.py -- Get an HDF5 file from the cutout service and write a series of PNG files that show the data
* npzMakePNGs.py -- Get an NPZ (Numpy zip) file from the cutout service and write a series of PNG files that show the data
* annotatewhite.py -- Read a cube of data and write annotations for the whitest pixels.  Uses both cutout and annotate service.
* addcube.py -- Add annotations as a cube
