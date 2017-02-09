Resources API
*************

Dataset
-------

.. _json-createdataset:

.. https:post:: (string:server_name)/nd/resource/dataset/

   :synopsis: Create a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string

   :statuscode 201: Resource created
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: https
      
      POST /nd/resource/kasthuri11/ HTTPS/1.1
      Host: cloud.neurodata.io
      Content-Type: application/json

      {
        "dataset_name" : "kasthuri11",
        "ximagesize" : 2000,
        "yimagesize" : 2000,
        "zimagesize" : 100,
        "xvoxelres" : 5.0,
        "yvoxelres" : 5.0,
        "zvoxelres" : 10.0,
        "public" : 1
      }
   
   **Example Responses**:

   .. sourcecode:: https

      HTTPS/1.1 201 Created
      Content-Type: text/plain

   .. sourcecode:: https
    
      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: https

      HTTPS/1.1 403 Forbidden
      Content-Type: text/plain

.. _json-listdataset:

.. https:get:: (string:server_name)/nd/resource/dataset/
   
   :synopsis: List all datasets
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string

   :statuscode 200: OK. List of datasets returned
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: https
      
      GET /nd/resource/kasthuri11/ HTTPS/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain

   **Example Responses**:

   .. sourcecode:: https

      HTTPS/1.1 200 OK
      Content-Type: application/json

      {
        'kasthuri11'
        'bock11'
        'lee15'
      }

   .. sourcecode:: https
    
      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: https

      HTTPS/1.1 403 Forbidden
      Content-Type: text/plain

.. _json-deletedataset:

.. https:delete:: (string:server_name)/nd/resource/dataset/
   
   :synopsis: Delete a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string

   :statuscode 204: No content. Resource deleted
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: https
      
      POST /nd/resource/kasthuri11/ HTTPS/1.1
      Host: cloud.neurodata.io
      Content-Type: application/json

      {
        "dataset_name" : "kasthuri11",
      }
   
   **Example Responses**:

   .. sourcecode:: https

      HTTPS/1.1 204 No Content
      Content-Type: text/plain

   .. sourcecode:: https
    
      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: https

      HTTPS/1.1 403 Forbidden
      Content-Type: text/plain


.. _json-createchannel:

Channel
-------
  
.. https:post:: (string:server_name)/nd/sd/dataset/(string:dataset_name)/project/(string:project_name)/token/(string:token_name)/

   :synopsis: Create a list of channels for an existing project using the project token and JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 400: Error in file format or if :ref:`channel <channel>` already exists
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: https
      
      POST /nd/ca/test_kat1/ HTTPS/1.1
      Host: openconnecto.me
      Content-Type: application/json

      {
        "channels": {
          "CHAN1": {
            "channel_name": "CHAN1",
            "channel_type": "image",
            "datatype": "uint8",
            "readonly": 0
          },
          "CHAN2": {
            "channel_name": "CHAN2",
            "channel_type": "image",
            "datatype": "uint8",
            "readonly": 0
          }
        }
      }

   **Example Responses**:

   .. sourcecode:: https

      HTTPS/1.1 201 Created
      Content-Type: text/plain

   .. sourcecode:: https
    
      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: https

      HTTPS/1.1 403 Forbidden
      Content-Type: text/plain

.. _json-deletechannel:


deleteChannel
-------------

.. https:post:: (string:server_name)/nd/ca/(string:token_name)/deleteChannel/

   :synopsis: Delete a list of channels for an existing project using the project token and a JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 400: Error in file format or if :ref:`channel <channel>` does not exist
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: https
      
      POST /nd/ca/test_kat1/ HTTPS/1.1
      Host: openconnecto.me
      Content-Type: application/json

      {
        "channels": [
                   "CHAN2",
                   "CHAN3"
        ]
      }

   **Example Responses**:

   .. sourcecode:: https

      HTTPS/1.1 200 OK
      Content-Type: text/plain

      Success. Channels deleted.

   .. sourcecode:: https

      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

      Missing. Required fields.

   .. sourcecode:: https

      HTTPS/1.1 400 BadRequest
      Content-Type: text/plain

      Error saving models. The channels were not deleted.
