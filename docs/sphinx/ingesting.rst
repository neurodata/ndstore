How to Ingest Data
******************

Prepping The Data
=================
//AE TODO Add enumerated steps

There are two important components to how data should be organized before uploading to the service. First is file hierarchy (how the folders holding data should be organized) which is as follows; all channel specific data is saved in a folder with the name of the channel. For example if you have image data of two mouse cortices, one cortex would be stored in an image channel Cortex1. So, all the data from that imaging would be stored in a folder named Cortex1. In the case of time series data each channel folder should contain sub-folders time0, time1, time2, ..., timeN, each of which contains the image data for that specific time slot. All the channel folders should be stored inside a folder named the same as the token name.

Second is how the files themselves are organized. Currently the auto-ingest service only supports tiff, tif, and png files. The files should be organized such that there is a tiff/png/tif for each Z-slice, with each named the slice number up to 4 digits. For example if there was a imaging set with 405 image slices in tif form, the image channel folder(s) should have files labeled 0000.tif through 0404.tiff. 

Uploading
=========
//AE TODO Add enumerated steps

This section will initially address how to upload one channels worth of material. Located in the autoingest folder in the ingest folder of open-connectome is a file named generatejson.py (https://github.com/openconnectome/open-connectome\\/blob/master/ingest/autoingest/generatejson.py). To upload your data edit the hard-coded values in the code to reflect your data, being sure to specify that you are trying to put data to http://openconnecto.me and your DataURL is http accessible (if it is not the script will fail). Once the script has run you do not need to maintain a connection to the script.

Unsupported Image Types
=======================

We currently do not support 3-D tiffs.
