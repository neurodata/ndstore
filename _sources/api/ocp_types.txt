OCP Types
*********

.. _ocp-channeltype:

Channel Types
=============

Channels in OCP are individual entites inside projects. You can have mulitple same and different channels inside the same project. Each channel has it's unique properties. For example, annotation  channels allow your to store annotation paint data and metadata using RAMON. Image channels allow you to store image data which is 3-dimenisonal in xyz dimensions. Timeseries channels allow you to store time data which is 4-dimenisonal in xyz+time dimensions.

=================   ==========
Channel Type        OCP Value
=================   ==========
Image               image
Timeseries          timseries
Annotation          annnotation
=================   ==========

.. _ocp-datatype:

Data Types
==========

Each channel has an associated datatype. The datatype of the channel represent the type of data stored in that channel. For example, an image channel which has 8-bit data will be of the datatype uint8. A probablity map which has floating point data will be of the type float32.

===============     ==========
Data Type           OCP Value
===============     ==========
8-bit Integer       uint8
16-bit Integer      uint16
32-bit Integer      uint32
32-bit RGBA         rgb32
64-bit RGBA         rgb64
32-bit Float        float32
===============     ==========

.. _ocp-combo:

Possible Combination of Channel Types and Data Types
=====================================================

OCP allows certain set combinations of the above mentioned channel type and data types. The combinations mentioned below.

=============       =======================================
Channel Type        Possible Data Types
=============       =======================================
Image               uint8, uint16, uint32, uint64, float32
Timeseries          uint8, uint16, float32
Annotation          uint32, uint64
=============       =======================================

.. _ocp-propagation:

Propagation Service
===================

OCP allows only downsampling of data via a service called Propagation. This service does not upsample your data. You can post to a specific resolution and call on the :ref:`set propagation service <propagate-set>` to downsample your data in the background. When your data is under propagation, the project is locked and you cannot post data to it. This is done to maintain the consistency of data across different resolutions. You can check the status of your project via the :ref:`get propagation service <propagate-get>`. Both these services return values which have signfies something. You can use the value reference table below to idenitfy the propgation state of your project. 
*WARNING: It make take quite a while for propagation of some projects which are big. Please be patient.*

===================     ==========
Propagation Value       OCP Value
===================     ==========
Not Propagated          0
Under Propagation       1
Propagated              2
===================     ==========
