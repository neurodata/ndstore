## Tests Help
* Run this command to run all tests
```console
py.test
```
* Run a particular test
```console
py.test <test_name>.py
```
* Run a particular test module
```console
py.test <test_name>.py::<test_module>
```
* Run this command to list all tests:
```console
py.test --collect-only
```

## List of Tests:

* test_image - 21 tests

  - Module : Test_Image_Slice
    1. test_xy
    2. test_yz
    3. test_xz
    4. test_xy_incorrect

  - Module : Test_Image_Window
    1. test_window_default
    2. test_window_args

  - Module : Test_Image_Simple_Catmaid
    1. test_xy_tile
    2. test_yz_tile
    3. test_xz_tile

  - Module : Test_Image_Mcfc_Catmaid
    1. test_xy_tile

  - Module : Test_Image_Post
    1. test_npz 
    2. test_npz_incorrect_region
    3. test_npz_incorrect_datatype
    4. test_hdf5
    5. test_hdf5_incorrect_region
    6. test_hdf5_incorrect_datatype
    7. test_npz_incorrect_channel
    8. test_hdf5_incorrect_channel

  - Module : Test_Image_Default
    1. test_npz_default_channel
    2. test_xy_default_channel

  - Module : Test_Image_Simple_Catmaid
    1. test_xy_tile

* test_info - 5 tests

  - Module Test_Info
    1. test_public_tokens
    2. test_public_datasets
    3. test_info
    4. test_projinfo
    5. test_xmlinfo
    6. test_reserve

* test_io.py - 6 tests

  - Module : TestRW
    1. test_raw
    2. test_batch
    3. test_rw
    4. test_cuboids
    5. test_update
    6. test_dataonly

* test_probability.py - 12 tests

  - Module : Test_Probability_Slice
    1. test_xy
    2. test_yz
    3. test_xz
    4. test_xy_incorrect

  - Module : Test_Probability_Post
    1. test_npz
    2. test_npz_incorrect_region
    3. test_npz_incorrect_datatype
    4. test_hdf5
    5. test_hdf5_incorrect_region
    6. test_hdf5_incorrect_datatype
    7. test_npz_incorrect_channel
    8. test_hdf5_incorrect_channel

* test_propagate - 6 test

  - Module : Test_Image_Zslice_Propagate
    1. test_web_propagate

  - Module : Test_Image_Readonly_Propagate
    1. test_web_propagate

  - Module : Test_Image_Propagated_Propagate
    1. test_web_propagate
 
  - Module : Test_Image_Isotropic_Propagate
    1. test_web_propagate

  - Module : Test_Anno_Zslice_Propagate
    1. test_web_propagate

  - Module : Test_Anno_Isotropic_Propagate
    1. test_web_propagate

* test_query.py - 1 test

  - Module : Test_Ramon
  1. test_query_objects

* test_ramon.py - 15 tests

  - Module : Test_Ramon
    1. test_anno_minmal
    2. test_anno_full
    3. test_anno_update
    4. test_anno_delete
    5. test_anno_upload
    6. test_annotation
    7. test_synapse
    8. test_seed
    9. test_neuron
    10. test_organelle
    11. test_wrong
    12. test_node
    13. test_skeleton
    14. test_roi
    15. test_kvpairs

* test_time.py - 17 tests

  - Module : Test_Image_Slice
    1. test_xy
    2. test_yz
    3. test_xz

  - Module : Test_Image_Post
    1. test_npz
    2. test_npz_incorrect_region
    3. test_npz_incorrect_datatype
    4. test_npz_incorrect_timesize
    5. test_hdf5
    6. test_hdf5_incorrect_region
    7. test_hdf5_incorrect_datatype
    8. test_npz_incorrect_channel
    9. test_hdf5_incorrect_channel

  - Module : Test_Time_Simple_Catmaid
    1. test_xy_tile
    2. test_yz_tile
    3. test_xz_tile

  - Module : Test_Image_Window
    1. test_window_default
    2. test_window_args

* test_autoingest.py - 3 tests

  - Module : Test_AutoIngest_Json
    1. test_basic_json
    2. test_complex_json
    3. test_error_json

* test_project_management.py - 3 tests

  - Module : Test_Create_Channel_Json
    1. test_create_json
    2. test_error_json
  - Module : Test_Delete_Channel_Json
    1. test_single_channel_json


* test_graphgen.py - 4 tests

  - Module : Test_GraphGen
    1. test_checkTotal
    2. test_checkType
    3. test_checkCutout
    4. test_ErrorHandling

* test_blosc.py - 4 tests

  - Module : Test_Blosc
    1. test_get_blosc
    2. test_post_blosc
    3. test_incorrect_dim_blosc
    4. test_incorrect_channel_blosc

* test_jpeg.py - 2 tests

  - Module : Test_Jpeg
    1. test_get_jpeg

* test_stats.py - 7 tests

  - Module : Test_Histogram8
    1. test_genhistogram

  - Module : Test_Histogram16
    1. test_genhistogram

  - Module : TestHistogramROI
    1. test_genhistogramROI
    2. test_genhistogramROICuboid
    3. test_genhistogramROICuboidEnd 
    4. test_genhistogramROIError 

  - Module : TestHistogramROIMultiple 
    1. test_genhistogramROIMultiple 

* tests to add
  1. Test filter for image slices
  2. Test neurons, segments and synapses
  3. Test filter for anno
  4. Test anno Paint I/O interfaces
  5. Test 16-bit Timeseries Data
