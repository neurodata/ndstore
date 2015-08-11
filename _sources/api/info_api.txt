Project Info API's
******************

JSON Service
============

.. _json-get:

GET
----

.. http:get:: (string:server_name)/ocp/ca/(string:token_name)/info/
   
   :synopsis: Get project information from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

   **Example Request**:
   
   .. sourcecode:: http
      
      GET /ocp/ca/kasthuri11/info/ HTTP/1.1
      Host: ocp.me

   **Example Response**:

   .. sourcecode:: http
      
      HTTP/1.1 200 OK
      Content-Type: application/json
      
     
      {
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
              "imagesize": {
                  "0": [
                      21504, 
                      26624
                  ], 
                  "1": [
                      10752, 
                      13312
                  ], 
                  "2": [
                      5376, 
                      6656
                  ], 
                  "3": [
                      2688, 
                      3328
                  ], 
                  "4": [
                      1344, 
                      1664
                  ], 
                  "5": [
                      672, 
                      832
                  ], 
                  "6": [
                      336, 
                      416
                  ], 
                  "7": [
                      168, 
                      208
                  ]
              }, 
              "isotropic_slicerange": {
                  "0": [
                      1, 
                      1850
                  ], 
                  "1": [
                      1, 
                      1850
                  ], 
                  "2": [
                      1, 
                      1850
                  ], 
                  "3": [
                      1, 
                      1850
                  ], 
                  "4": [
                      1, 
                      1157
                  ], 
                  "5": [
                      1, 
                      579
                  ], 
                  "6": [
                      1, 
                      290
                  ], 
                  "7": [
                      1, 
                      145
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
              "slicerange": [
                  1, 
                  1850
              ], 
              "timerange": [
                  0, 
                  0
              ], 
              "windowrange": [
                  0, 
                  0
              ], 
              "zscale": {
                  "0": 10.0, 
                  "1": 5.0, 
                  "2": 2.5, 
                  "3": 1.25, 
                  "4": 0.625, 
                  "5": 0.3125, 
                  "6": 0.15625, 
                  "7": 0.078125
              }
          }, 
          "project": {
              "dataset": "kasthuri11", 
              "dataurl": "http://openconnecto.me/ocp", 
              "dbname": "kasthuri11", 
              "exceptions": false, 
              "host": "dsp061.pha.jhu.edu", 
              "kvengine": "MySQL", 
              "kvserver": "localhost", 
              "projecttype": 1, 
              "propagate": 2, 
              "readonly": true, 
              "resolution": 0
          }, 
          "version": {
              "ocp": 0.6, 
              "schema": 0.6
          }
      }


.. _json-post:

POST
----

.. http:get:: (string:server_name)/ocp/ca/json/
   
   :synopsis: Get a HDF5 file from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
    
   :form JSON: Look at the Tech Sheet

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
 
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /ocp/ca/json/ HTTP/1.1
      Host: ocp.me
      Content-Type: application/json

      {
        dataset
        project
        metadata
      }

   **Example Response**:

   .. sourcecode:: http
      
      HTTP/1.1 200 OK
      Content-Type: application/json

      { 
        SUCCESS 
      }


.. _hdf5-get:

HDF5 Service
=============

GET
----

.. http:get:: (string:server_name)/ocp/ca/(string:token_name)/projinfo/
   
   :synopsis: Post a Numpy file to the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
