OCP Types
*********

.. _ocp-channeltype:

Channel Types
=============

OCP supports three channel types mentioned below.

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
