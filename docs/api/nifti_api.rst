NIFTI API's
***********

.. _nifti-get:

getNifti
--------

.. http:get:: (string:server_name)/ocp/ca/(string:token_name)/(string:channel_name)/getPropagate/

   :synopsis: Get the graph from the server.

   :param server_name: Server Name in OCP. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string
   :param channel_name: Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type channel_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
