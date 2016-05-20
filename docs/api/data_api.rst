Data API
***********

.. _data-api:

HDF5 Service
============

.. _hdf5-post:

POST
----

.. http:post:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/hdf5/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Post a 3D/4D region of data for a single channel or multiple channels in HDF5 file format to the server. Form parameters describe the datasets within the HDF5 file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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

.. gist:: https://gist.github.com/kunallillaney/19b78e5a83611edf7808

.. _hdf5-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/hdf5/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Get a 3D/4D region of data for a single channel or multiple channels in HDF5 file format from the server. Form parameters describe the datsets within the HDF5 file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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



Blosc Service
=============

.. _blosc-post:

POST
----

.. http:post:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/blosc/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Post a 3D/4D region of data for of a specified channel, resolution and bounds in blosc compression format.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

.. _blosc-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/blosc/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Get a 3D/4D region of data for of a specified channel, resolution and bounds in the blosc compression format.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format


Numpy Service
=============

.. _numpy-post:

POST
----

.. http:post:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/npz/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Post a 3D/4D region of data for of a specified channel, resolution and bounds in the numpy array format.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int

   :form DATA: Numpy Array

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

.. gist:: https://gist.github.com/kunallillaney/19b78e5a83611edf7808

.. _numpy-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/npz/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Download a 3D/4D region of data for of a specified channel, resolution and bounds in the numpy array format. You can load this data into python using the numpy library for anaylsis.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int

   :form DATA: Numpy Array

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format

RAW Service
=============

.. _raw-get:

GET
----

.. http:get:: (string:server_name)/nd/ca/(string:token_name)/(string:channel_name)/raw/(int:resolution)/(int:min_x),(int:max_x)/(int:min_y),(int:max_y)/(int:min_z),(int:max_z)/(int:min_time),(int:max_time)/
   
   :synopsis: Download a 3D/4D region of data for of a specified channel, resolution and bounds in a web readable raw binary representation numpy array format. This service is used by KNOSSOS.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string
   :param token_name: Token Name in NeuroData.
   :type token_name: string
   :param channel_name: Channel Name in NeuroData. *Optional*. If missing will use default channel for the token.
   :type channel_name: string
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
   :param min_z: Minimum value in the zrange
   :type min_z: int
   :param max_z: Maximum value in the zrange
   :type max_z: int
   :param min_time: Minimum value in the timerange. *Optional*. Only used for timeseries channels.
   :type min_time: int
   :param max_time: Maximum value in the timerange. *Optional*. Only used for timeseries channels.
   :type max_time: int

   :form DATA: Web readable raw binary of numpy array in C-style

   :statuscode 200: No error
   :statuscode 404: Error in the syntax or file format
