RAMON API
***********

JSON Service
============

The RAMON JSON service retrieves RAMON objects from the database and returns them in JSON format.

getJSONObject
-------------

.. http:get:: (string:server_name)/nd/ramon/(string:token_name)/(string:channel_name)/(int:id)/

   :synopsis: Retrieve the RAMON object specified by ID as a JSON object.

   :param server_name: NeuroData Server Name (typically cloud.neurodata.io
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string
   :param id: An integer identifier for the request RAMON object.
   :type id: int

   :statuscode 200: RAMON object returned as JSON.
   :statuscode 404: RAMON object not found or error.

   **Example Return**:

   .. code-block:: json

      {
         "21": {
               "syn_weight": 0.0,
               "ann_type": 2,
               "syn_type": 0,
               "ann_status": 0,
               "postgaba": "0",
               "ann_confidence": 1.0,
               "ann_id": 21,
               "syn_centroid": "[]",
               "ann_author": "Randal Burns",
               "gaba": "0",
               "display": "0",
               "syn_segments": [0]
            }
      }



getBoundingBox
--------------
   .. http:get:: (string:server_name)/nd/ramon/(string:token_name)/(string:channel_name)/(int:id)/boundingbox/(int:res)/

      :synopsis: Retrieve the bounding box around the specified RAMON object along with the rest of the RAMON metadata and return it as a JSON object.

      :param server_name: NeuroData Server Name (typically cloud.neurodata.io
      :type server_name: string
      :param token_name: NeuroData Token
      :type token_name: string
      :param channel_name: NeuroData Channel
      :type channel_name: string
      :param id: An integer identifier for the request RAMON object.
      :type id: int
      :param res: Resolution for Bounding Box Coordinates
      :type res: int

      :statuscode 200: RAMON object and bounding box returned as JSON.
      :statuscode 404: RAMON object not found or error.

      **Example Return**:

      .. code-block:: json

         {
            "21": {
               "syn_weight": 0.0,
               "ann_type": 2,
               "syn_type": 0,
               "ann_status": 0,
               "postgaba": "0",
               "ann_confidence": 1.0,
               "ann_id": 21,
               "syn_centroid": "[]",
               "bbcorner": [1549, 2940, 0],
               "ann_author": "Forrest Collman",
               "bbdim": [112, 101, 4],
               "gaba": "0",
               "display": "0",
               "syn_segments": [0]
            }
         }

      **Bounding Box**:

      The bounding box is described by the `bbcorner` and `bbdim` keys:

      * `bbcorner`: The lower corner of the bounding box.
      * `bbdim`: The dimensions of the bounding box.

      To reconstruct the upper corner of the bounding box, add `bbcorner` and `bbdim`.


Query by Key
============

query
-----

.. http:get:: (string:server_name)/nd/ramon/(string:token_name)/(string:channel_name)/query/(string/int/float:key)/(string/int/float:value)/

   :synopsis: Retrieve a list of RAMON objects with the specified key/value combination.

   :param server_name: NeuroData Server Name (typically cloud.neurodata.io
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string
   :param key: The RAMON object key to search on.
   :type key: string/int/float
   :param value: The RAMON object value to match for the specified key.
   :type value: string/int/float

   :statuscode 200: RAMON object list returned.
   :statuscode 500: Server Error (text returned).

   **Note**:

   In the RAMON data model all standard RAMON attributes are also keys. So, finding all synapses would amount to using the query interface with a key of `ann_type` and a value of `2`.

topKeys
-------

.. http:get:: (string:server_name)/nd/ramon/(string:token_name)/(string:channel_name)/topkeys/(int:num_results)/

   :synopsis: Retrieve a list of the top RAMON keys for the specified project.

   :param server_name: NeuroData Server Name (typically cloud.neurodata.io
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string
   :param num_results: The number of keys to return.
   :type num_results: int

   :statuscode 200: List of RAMON keys returned.
   :statuscode 500: Server Error (error text returned).

topKeysByType
-------------

.. http:get:: (string:server_name)/nd/ramon/(string:token_name)/(string:channel_name)/topkeys/(int:num_results)/type/(int:ramon_type)/

   :synopsis: Retrieve a list of the top RAMON keys for the specified project restricted to a certain type of RAMON object.

   :param server_name: NeuroData Server Name (typically cloud.neurodata.io
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string
   :param num_results: The number of keys to return.
   :type num_results: int
   :param ramon_type: Restrict the top keys list to this type of RAMON object.
   :type ramon_type: int

   :statuscode 200: List of RAMON keys returned.
   :statuscode 500: Server Error (error text returned).

Field Service
=============

setField
--------

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/setField/(string:ramon_field)/(string/int/float:ramon_value)

   :synopsis: Set the value of the RAMON field for the specified channel

   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param ramon_field: RAMON field. For more details look at the RAMON documents.
   :type ramon_field: string
   :param ramon_value: Value of the corresponding RAMON field
   :type ramon_value: string/int/float

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

getField
--------

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/getField/(string:ramon_field)/

   :synopsis: Set the value of the RAMON field for the specified channel

   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param ramon_field: RAMON field. For more details look at the RAMON documents.
   :type ramon_field: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

Annotation Service
==================

GET
---

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/(int:annotation_id)/(string:option_args)/(int:resolution)/

   :synopsis: Get an annotation from the server

   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param annotation_id: Id of the annotation to be cut from the database.
   :type annotation_id: int
   :param options_args: *Optional Arguments*. This can be overwrite, preserve, exception.
   :type options_args: string
   :param resolution: Resolution for the annotation
   :type resolution: int

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

POST
----

.. http:post:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/(string:option_args)/

   :synopsis: Post an annotation to the server

   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param options_args: *Optional Arguments*. This can be overwrite, preserve, exception.
   :type options_args: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

Merge Service
=============

GET
---

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/merge/(string:listofids)/(string:option_args)/

   :synopsis: Merge two annotation ids on the server.

   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param options_args: *Optional Arguments*. This can be overwrite, preserve, exception.
   :type options_args: string
   :param listofids: Comma separated list of ids
   :type listofids: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
