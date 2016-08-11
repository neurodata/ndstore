Project Info API
******************

JSON Informatio Service
=======================

.. _jsoninfo-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/info/
   
   :synopsis: Get all metadata associated with a project that the specified token refers to, including metadata for the dataset it points to, as well as each channel it contains in JSON format.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 403: Forbidden
   :statuscode 404: Error in the syntax

   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/ca/kasthuri11/info/ HTTP/1.1
      Host: openconnecto.me

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "channels": {
              "image": {
                  "channel_type": "image",
                  "datatype": "uint8",
                  "exceptions": 0,
                  "propagate": 2,
                  "readonly": 1,
                  "resolution": 0,
                  "windowrange": [
                      0,
                      0
                  ]
              }
          },
          "dataset": {
              "cube_dimension": {
                  "0": [
                      128,
                      128,
                      16
                  ],
                  "1": [
                      128,
                      128,
                      16
                  ],
                  "2": [
                      128,
                      128,
                      16
                  ],
                  "3": [
                      128,
                      128,
                      16
                  ],
                  "4": [
                      128,
                      128,
                      16
                  ],
                  "5": [
                      64,
                      64,
                      64
                  ],
                  "6": [
                      64,
                      64,
                      64
                  ],
                  "7": [
                      64,
                      64,
                      64
                  ]
              },
              "description": "kasthuri11",
              "imagesize": {
                  "0": [
                      21504,
                      26624,
                      1850
                  ],
                  "1": [
                      10752,
                      13312,
                      1850
                  ],
                  "2": [
                      5376,
                      6656,
                      1850
                  ],
                  "3": [
                      2688,
                      3328,
                      1850
                  ],
                  "4": [
                      1344,
                      1664,
                      1850
                  ],
                  "5": [
                      672,
                      832,
                      1850
                  ],
                  "6": [
                      336,
                      416,
                      1850
                  ],
                  "7": [
                      168,
                      208,
                      1850
                  ]
              },
              "neariso_scaledown": {
                  "0": 1,
                  "1": 1,
                  "2": 1,
                  "3": 1,
                  "4": 2,
                  "5": 3,
                  "6": 6,
                  "7": 13
              },
              "offset": {
                  "0": [
                      0,
                      0,
                      1
                  ],
                  "1": [
                      0,
                      0,
                      1
                  ],
                  "2": [
                      0,
                      0,
                      1
                  ],
                  "3": [
                      0,
                      0,
                      1
                  ],
                  "4": [
                      0,
                      0,
                      1
                  ],
                  "5": [
                      0,
                      0,
                      1
                  ],
                  "6": [
                      0,
                      0,
                      1
                  ],
                  "7": [
                      0,
                      0,
                      1
                  ]
              },
              "resolutions": [
                  0,
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
              ],
              "scaling": "zslices",
              "scalinglevels": 7,
              "timerange": [
                  0,
                  0
              ],
              "voxelres": {
                  "0": [
                      1.0,
                      1.0,
                      10.0
                  ],
                  "1": [
                      2.0,
                      2.0,
                      10.0
                  ],
                  "2": [
                      4.0,
                      4.0,
                      10.0
                  ],
                  "3": [
                      8.0,
                      8.0,
                      10.0
                  ],
                  "4": [
                      16.0,
                      16.0,
                      10.0
                  ],
                  "5": [
                      32.0,
                      32.0,
                      10.0
                  ],
                  "6": [
                      64.0,
                      64.0,
                      10.0
                  ],
                  "7": [
                      128.0,
                      128.0,
                      10.0
                  ]
              }
          },
          "metadata": {},
          "project": {
              "description": "kasthuri11",
              "name": "kasthuri11",
              "version": "0.0"
          }
      }


.. _hdf5info-get:

HDF5 Information Service
========================

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/projinfo/
   
   :synopsis: Get all metadata associated with a project that the specified token refers to, including metadata for the dataset it points to, as well as each channel it contains in HDF5 format.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 403: Forbidden
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: http
      
      GET /nd/ca/kasthuri11/projinfo/ HTTP/1.1
      Host: openconnecto.me

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/hdf5
