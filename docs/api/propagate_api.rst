Propagate API's
***************

getPropagate
------------

.. http:get:: (string:server_name)/ca/(string:token_name)/(string:channel_name)/getPropagate/
   
   :synopsis: Get the propagation state of the channel

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string
   :param channel_name: Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type channel_name: string

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

setPropagate
------------

.. http:get:: (string:server_name)/ca/(string:token_name)/(string:channel_name)/setPropagate/(int:propagate_value)/

   :synopsis: Set the propagation state of the channel

   :param server_name: Server Name in OCP. In the general case this is ocp.me.
   :type server_name: string
   :param token_name: Token Name in OCP.
   :type token_name: string
   :param channel_name: Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
   :param propagate_value: 0,1,2
   :param propagate_value: int
  
   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
