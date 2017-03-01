Resources API
*************

Dataset
=======

Create
------

.. _json-createdataset:

.. http:post:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/

   :synopsis: Create a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name in NeuroData
   :type dataset_name: string

   :statuscode 201: Resource created
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      POST /nd/resource/dataset/kasthuri11/ HTTP/1.1
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

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Get
---

.. _json-getdataset:

.. http:get:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/

   :synopsis: Get a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name in NeuroData
   :type dataset_name: string

   :statuscode 200: OK. Get dataset information
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/dataset/kasthuri11/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain
   
   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
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

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

List
----

.. _json-listdataset:

.. http:get:: (string:server_name)/nd/resource/dataset/
   
   :synopsis: List all datasets owned by the user
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string

   :statuscode 200: OK. List of datasets returned
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/dataset/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "kasthuri11"
        "bock11"
        "lee15"
      }

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

List Public
-----------

.. _json-publicdataset:

.. http:get:: (string:server_name)/nd/resource/public/dataset/
   
   :synopsis: List all public datasets
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string

   :statuscode 200: OK. List of datasets returned
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/public/dataset/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "kasthuri11"
      }

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Delete
------

.. _json-deletedataset:

.. http:delete:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/
   
   :synopsis: Delete a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name
   :type dataset_name: string

   :statuscode 204: No content. Resource deleted
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      DELETE /nd/resource/dataset/kasthuri11/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: test/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Project
=======

Create
------

.. _json-createproject:

.. http:post:: (string:server_name)/nd/resource/dataset/{string:dataset_name)/project/(string:project_name)/

   :synopsis: Create a project
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Name of dataset
   :type dataset_name: string
   :param project_name: Name of dataset
   :type project_name: string

   :statuscode 201: Resource created
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      POST /nd/resource/dataset/kasthuri11/project/kat11/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: application/json

      {
        "project_name" : "kat11",
        "host" : "localhost",
        "s3backend" : 1,
        "public" : 1,
        "kvserver" : "localhost",
        "kvengine" : "Redis",
      }
   
   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Get
---

.. _json-getproject:

.. http:get:: (string:server_name)/nd/resource/dataset/{string:dataset_name)/project/(string:project_name)/

   :synopsis: Get a project
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Name of dataset
   :type dataset_name: string
   :param project_name: Name of dataset
   :type project_name: string

   :statuscode 201: Resource created
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/dataset/kasthuri11/project/kat11/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain
   
   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
        "project_name" : "kat11",
        "host" : "localhost",
        "s3backend" : 1,
        "public" : 1,
        "kvserver" : "localhost",
        "kvengine" : "Redis",
      }

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Delete
------

.. _json-deleteproject:

.. http:delete:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/project/(string:project_name)
   
   :synopsis: Delete a dataset
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name
   :type datset_name: string
   :param project_name: Project name
   :type project_name: string

   :statuscode 204: No content. Resource deleted
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      DELETE /nd/resource/dataset/kasthuri11/project/kat11/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: test/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

List
----

.. _json-listproject:

.. http:get:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/project/
   
   :synopsis: List all projectss owned by the user for dataset_name
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name
   :type dataset_name: string

   :statuscode 200: OK. List of datasets returned
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/kasthuri11/project/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "kat11"
        "kat11cc"
        "kat11test"
      }

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/plain

Channel
=======

Create
------

.. _json-createchannel:

.. http:post:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/project/(string:project_name)/channel/(string:channel_name)/

   :synopsis: Create a channel
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Name of dataset
   :type dataset_name: string
   :param: project_name: Name of project
   :type project_name: string
   :param: channel_name: Name of channel
   :type channel_name: string

   :statuscode 201: Resource created
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      POST /nd/resource/kasthuri11/project/kat11/channel/ch0/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: application/json

      {
        "channel_name" : "ch0",
        "channel_type" : "image",
        "channel_datatype" : "uint8",
        "startwindow" : 0,
        "endwindow" : 500,
      }
   
   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Get
---

.. _json-getchannel:

.. http:get:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/project/(string:project_name)/channel/(string:channel_name)/

   :synopsis: Create a channel
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Name of dataset
   :type dataset_name: string
   :param: project_name: Name of project
   :type project_name: string
   :param: channel_name: Name of channel
   :type channel_name: string

   :statuscode 200: OK. Channel information returned.
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/resource/kasthuri11/project/kat11/channel/ch0/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: text/plain
   
   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "channel_name" : "ch0",
        "channel_type" : "image",
        "channel_datatype" : "uint8",
        "startwindow" : 0,
        "endwindow" : 500,
      }

   .. sourcecode:: http
    
      HTTP/1.1 200 OK
      Content-Type: application/json
      
   .. sourcecode:: http
      
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain

Delete
------

.. _json-deletechannel:

.. http:delete:: (string:server_name)/nd/resource/dataset/(string:dataset_name)/project/(string:project_name)/channel/(string:channel_name)/
   
   :synopsis: Delete a channel
   
   :param server_name: Server Name in NeuroData. In the general case this is cloud.neurodata.io
   :type server_name: string
   :param dataset_name: Dataset name
   :type datset_name: string
   :param project_name: Project name
   :type project_name: string
   :param channel_name: Channel name
   :type channel_name: string

   :statuscode 204: No content. Resource deleted
   :statuscode 400: Bad Request. Incorrect syntax
   :statuscode 403: Forbidden. Insufficient permissions.
   
   **Example Request**:
   
   .. sourcecode:: http
      
      DELETE /nd/resource/dataset/kasthuri11/project/kat11/channel/ch0/ HTTP/1.1
      Host: cloud.neurodata.io
      Content-Type: test/plain

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: text/plain

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Content-Type: text/plain
