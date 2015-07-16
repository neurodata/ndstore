Overlay API's
*************

Cutut Service
=============

GET XY Slice Cutout
-------------------

.. http:post:: (string:host_server_name)/ocp/overlay/(float:alpha_value)/(string:first_server_name)/(string:first_token_name)/(string:first_channel_name)/(string:second_server_name)/(string:second_token_name)/(string:second_channel_name)/xy/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:z_slice)/(int:time_slice)/
   
   :synopsis: Get a XY Slice Cutout

   :param host_server_name: Host Server Name in OCP. In the general case this is ocp.me.
   :type host_server_name: string
   :param first_server_name: First Server Name in OCP. In the general case this is ocp.me.
   :type first_server_name: string
   :param first_token_name: First Token Name in OCP.
   :type first_token_name: string
   :param first_channel_name: First Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type first_channel_name: string
   :param second_server_name: Second Server Name in OCP. In the general case this is ocp.me.
   :type second_server_name: string
   :param second_token_name: Second Token Name in OCP.
   :type second_token_name: string
   :param second_channel_name: Second Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type second_channel_name: string
   :param resolution: Resolution for the data
   :type resolution: int
   :param min_x: Minimum value in the xrange
   :type min_x: int
   :param max_x: Maximum value in the xrange
   :type max_x: int
   :param min_y: Minimum value in the yrange
   :type min_y: int
   :param max_y: Maximum value in the yrange
   :type max_y: int
   :param z_slice: Z-slice value
   :type z_slice: int
   :param time_slice: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type time_slice: int
    
   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format


GET XZ Slice Cutout
-------------------

.. http:post:: (string:host_server_name)/ocp/overlay/(float:alpha_value)/(string:first_server_name)/(string:first_token_name)/(string:first_channel_name)/(string:second_server_name)/(string:second_token_name)/(string:second_channel_name)/xz/(int:resolution)/(int:min_x),(int:max_x)/(int:y_slice)/(int:min_z),(int:max_z)/(int:time_slice/
   
   :synopsis: Get an overlay XZ slice cutout

   :param host_server_name: Host Server Name in OCP. In the general case this is ocp.me.
   :type host_server_name: string
   :param first_server_name: First Server Name in OCP. In the general case this is ocp.me.
   :type first_server_name: string
   :param first_token_name: First Token Name in OCP.
   :type first_token_name: string
   :param first_channel_name: First Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type first_channel_name: string
   :param second_server_name: Second Server Name in OCP. In the general case this is ocp.me.
   :type second_server_name: string
   :param second_token_name: Second Token Name in OCP.
   :type second_token_name: string
   :param second_channel_name: Second Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type second_channel_name: string
   :param resolution: Resolution for the data
   :type resolution: int
   :param min_x: Minimum value in the xrange
   :type min_x: int
   :param max_x: Maximum value in the xrange
   :type max_x: int
   :param y_slice: Y-slice value
   :type y_slice: int
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param time_slice: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type time_slice: int

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

GET YZ Slice Cutout
-------------------

.. http:post:: (string:host_server_name)/ocp/overlay/(float:alpha_value)/(string:first_server_name)/(string:first_token_name)/(string:first_channel_name)/(string:second_server_name)/(string:second_token_name)/(string:second_channel_name)/yz/(int:resolution)/(int:x_slice)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:time_slice)/
   
   :synopsis: Get an overlay YZ slice cutout

   :param host_server_name: Host Server Name in OCP. In the general case this is ocp.me.
   :type host_server_name: string
   :param first_server_name: First Server Name in OCP. In the general case this is ocp.me.
   :type first_server_name: string
   :param first_token_name: First Token Name in OCP.
   :type first_token_name: string
   :param first_channel_name: First Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type first_channel_name: string
   :param second_server_name: Second Server Name in OCP. In the general case this is ocp.me.
   :type second_server_name: string
   :param second_token_name: Second Token Name in OCP.
   :type second_token_name: string
   :param second_channel_name: Second Channel Name in OCP. *Optional*. If missing will use default channel for the token.
   :type second_channel_name: string
   :param resolution: Resolution for the data
   :type resolution: int
   :param x_slice: X-slice value
   :type x_slice: int
   :param min_y: Minimum value in the yrange
   :type min_y: int
   :param max_y: Maximum value in the yrange
   :type max_y: int
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int
    
   :form CUTOUT: HDF5 group, Post data
   :form CHANNELTYPE: HDF5 group, Channel type(image, annotation, probmap, timeseries)
   :form DATATYPE: HDF5 group, Data type(uint8, uint16, uint32, rgb32, rgb64, float32)

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
