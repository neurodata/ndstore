## Tests Help
  * Run this command to run all tests
    ```sh
    py.test
    ```
  * Run a particular test
    ```sh
    py.test <test_name>.py
    ```
  * Run a particular test module
    ```sh
    py.test <test_name>.py::<test_module>
    ```
  * Run this command to list all tests:
    ```sh
    py.test --collect-only
    ```

## List of Tests:

* test_image - 16 tests
  
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

* test_info - 4 tests

  - Module Test_Info
    1. test_public_tokens
    2. test_info
    3. test_projinfo
    4. test_reserve

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

* test_propagate - 4 test

  - Module : Test_Image_Zslice_Propagate
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

* test_ramon.py - 12 tests

  - Module : Test_Ramon
    1. test_anno_minmal
    2. test_anno_full
    3. test_anno_update
    4. test_anno_delete
    5. test_anno_upload
    6. test_annotation_field
    7. test_synapse_field
    8. test_seed_field
    9. test_segment_field
    10. test_neuron_field
    11. test_organelle_field
    12. test_wrong_field

* test_time.py - 12 tests
  
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

* test_blosc.py - 2 tests

  - Module : Test_Blosc
    1. test_get_blosc
    2. test_post_blosc

* tests to add
  1. Test filter for image slices
  2. Test neurons, segments and synapses
  3. Test filter for anno
  4. Test anno Paint I/O interfaces
  5. Test 16-bit Timeseries Data
