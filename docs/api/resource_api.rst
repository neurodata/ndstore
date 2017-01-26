Resources API
*************

.. _json-createchannel:

Channel
-------
  
.. http:post:: (string:server_name)/nd/ca/dataset/(string:dataset_name)/project/(string:project_name)/token/(string:token_name)/

   :synopsis: Create a list of channels for an existing project using the project token and JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 400: Error in file format or if :ref:`channel <channel>` already exists
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: http
      
      POST /nd/ca/test_kat1/ HTTP/1.1
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

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/plain

      Success. The channels were created.

   .. sourcecode:: http
    
      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

      Channel image already exists for project kasthuri11. Specify a different channel.

   .. sourcecode:: http

      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

      Missing Required fields.

.. _json-deletechannel:


deleteChannel
-------------

.. http:post:: (string:server_name)/nd/ca/(string:token_name)/deleteChannel/

   :synopsis: Delete a list of channels for an existing project using the project token and a JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 400: Error in file format or if :ref:`channel <channel>` does not exist
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: http
      
      POST /nd/ca/test_kat1/ HTTP/1.1
      Host: openconnecto.me
      Content-Type: application/json

      {
        "channels": [
                   "CHAN2",
                   "CHAN3"
        ]
      }

   **Example Responses**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: text/plain

      Success. Channels deleted.

   .. sourcecode:: http

      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

      Missing. Required fields.

   .. sourcecode:: http

      HTTP/1.1 400 BadRequest
      Content-Type: text/plain

      Error saving models. The channels were not deleted.
