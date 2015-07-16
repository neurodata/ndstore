Public Token API's
******************

GET
----

.. http:get:: (string:server_name)/ca/public_tokens/
   
   :synopsis: Get project information from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
