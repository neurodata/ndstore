RAMON API's
***********

RAMON Field Service
===================

getField
--------

.. http:get:: (string:server_name)/ca/(string:token_name)/(string:channel_name)/getField/(string:field)/(string/int/float:value)
   
   :synopsis: Get project information from the server

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

setField
--------

Query Object Service
====================

GET
---

Annotation Service
==================

GET
---

POST
----

Merge Service
=============

GET
---
