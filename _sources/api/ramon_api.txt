RAMON API's
***********

RAMON Field Service
===================

setField
--------

.. http:get:: (string:server_name)/ca/(string:token_name)/(string:channel_name)/setField/(string:ramon_field)/(string/int/float:ramon_value)
   
   :synopsis: Set the value of the RAMON field for the specified channel

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string
   :param channel_name: Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param ramon_field: RAMON field. For more details look at the RAMON documents.
   :type ramon_field: string
   :param ramon_value: Value of the corresponding RAMON field
   :type ramon_value: string/int/float

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

getField
--------

.. http:get:: (string:server_name)/ca/(string:token_name)/(string:channel_name)/getField/(string:ramon_field)/
   
   :synopsis: Set the value of the RAMON field for the specified channel

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string
   :param channel_name: Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param ramon_field: RAMON field. For more details look at the RAMON documents.
   :type ramon_field: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

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
