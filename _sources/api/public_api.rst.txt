Public Token API
******************

.. _public-tokens-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/public_tokens/
   
   :synopsis: Get a list of all publicly avaliable tokens from the server. These tokens can be used to GET and PUT data to the server. These tokens can also be used to access :ref:`project information<jsoninfo-get>`

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: http
      
      GET /nd/ca/public_tokens HTTP/1.1
      Host: openconnecto.me

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        "bock11",
        "Ex10R55",
        "Ex12R75",
        "Ex12R76",
        "Ex13R51",
        "Ex14R58",
        "kasthuri11",
        "takemura13"
      ]

.. _public-datasets-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/public_datsets/
   
   :synopsis: Get a list of all publicly avaliable datasets from the server.`

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax
    
   **Example Request**:
   
   .. sourcecode:: http
      
      GET /nd/ca/public_datasets HTTP/1.1
      Host: openconnecto.me

   **Example Response**:

   .. sourcecode:: http
      
      HTTP/1.1 200 OK
      Content-Type: application/json
      
      [
        "bock11", 
        "kasthuri11", 
        "takemura13"
      ]
