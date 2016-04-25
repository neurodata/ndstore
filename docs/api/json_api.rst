JSON API
**********

.. _json-createchannel:

createChannel
-------------

.. http:post:: (string:server_name)/ocp/ca/(string:token_name)/createChannel/

   :synopsis: Create a list of channels for an existing project using the project token and JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

   **Example Request**:

   .. sourcecode:: http

      POST /ocp/ca/test_kat1/ HTTP/1.1
      HOST: openconnecto.me
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

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "SUCCESS"
      }

.. _json-deletechannel:

deleteChannel
-------------

.. http:post:: (string:server_name)/ocp/ca/(string:token_name)/deleteChannel/

   :synopsis: Delete a list of channels for an existing project using the project token and a JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

   **Example Request**:

   .. sourcecode:: http

      POST /ocp/ca/test_kat1/ HTTP/1.1
      HOST: openconnecto.me
      Content-Type: application/json

      {
        "channels": [
                   "CHAN2",
                   "CHAN3"
        ]
      }

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "SUCCESS"
      }

.. _json-autoingest:

autoIngest
----------

.. http:post:: (string:server_name)/ocp/ca/autoIngest/

   :synopsis: Create a dataset, project and channels with a JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string

   :form JSON: Look at the Tech Sheet

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

   **Example Request**:

   .. sourcecode:: http

      GET /ocp/ca/json/ HTTP/1.1
      Host: openconnecto.me
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
