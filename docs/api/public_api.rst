Public Token API's
******************

GET
----

.. http:get:: (string:server_name)/ca/(string:token_name)/info/
   
   :synopsis: Get project information from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
