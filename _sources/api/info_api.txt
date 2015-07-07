Project Info API's
******************

JSON Service
============

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

.. gist:: https://gist.github.com/kunallillaney/19b78e5a83611edf7808


POST
----

.. http:get:: (string:server_name)/ca/json/
   
   :synopsis: Get a HDF5 file from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
    
   :form JSON: Look at the Tech Sheet

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
  
.. gist:: https://gist.github.com/kunallillaney/19b78e5a83611edf7808

HDF5 Service
=============

GET
----

.. http:get:: (string:server_name)/ca/(string:token_name)/projinfo/
   
   :synopsis: Post a Numpy file to the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

.. gist:: https://gist.github.com/kunallillaney/19b78e5a83611edf7808
