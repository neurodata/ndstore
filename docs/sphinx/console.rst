Adminstrator Console
********************

QuickStart
==========

To upload an image volume: Create a dataset with appropriate names/field values. Then, create a project from that dataset, with a channel of the image type that is being uploaded. Finally, create a token to access the project and use that token to upload the image data. The tutorials to do each of these steps is available below. Scripts for automated upload are available for python and Cajal (formerly ocpMatlab).

To upload annotation data: Using the existing project with the relevant image data create a channel of the annotation type that is being uploaded. Finally, create a token to access the project and use that token to upload the annotation data. The tutorials to do each of these steps is available below. More information on general annotation upload and download is available here.

Overview
========

The Console allows data to be uploaded and downloaded to OCP as well as access other services within OCP. Data in OCP is organized into datasets and projects, see below for a more extensive description of each. The diagram below shows how the overall service is organized;

.. figure:: ../images/ocpservicediagram.png
	:align: center 
	:width: 500
	:height: 200
	
Datasets are present on the OCP server and are accessed through projects. These datasets can hold multiple types of data, including image, annotation, ect. When a specific type of data needs to be accessed in a dataset (via the project), say for example 8-bit image data, a channel is created in the project for that specific datatype. The project (and in turn the channels and the dataset) is accessible by a token, which serves as an access point for anyone that has the token. 

Datasets
========

Overview
++++++++
Datasets contain all the current image/time datasets that the public has access to or any that have been created by the user. 

Dataset Creation Tutorial
+++++++++++++++++++++++++

Navigate to the datasets drop down menu and select create dataset. Fill in the appropriate data fields for each line (a full explanation of each can be found below). Click create data set and you should be re-directed to the data set main page, where you will now see a new data set with the data you selected. To use the data set create a new project/token.

+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Data Field              | Description                                                                                                                    | 
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Dataset Name            | The name of the data set you are uploading (Good practice is lastname and year).                                               |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Description             | A description of the data being uploaded, good things to include may be species and the location of where the images are from. |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|X, Y, Z Image Size       | This is the size of the X, Y and Z plane.                                                                                      |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|X, Y, Z Offset           | Amount to offset in the X, Y and Z plane.                                                                                      |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|PUBLIC                   | Whether or not the template (not the data) is viewable by everyone using OCP.                                                  |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Scaling Level            | Sets the resolution level for the dataset.                                                                                     |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Scaling Options          | 0 - Normal, 1 - Isotropic.                                                                                                     |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|X, Y, Z Voxel Resolution | This is the resolution of the data in X, Y and Z plane.                                                                        |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Start/End Time           | For timeseries data, these are the values of start time and end time. Use the default option if you don't have timeseries data.|
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+

Projects
========

Overview
++++++++
Projects are what allow a user to access datasets as well as manipulate them in various ways, such as adding annotations of viewing datasets at a much lower resolution. Projects are organized into tokens and channels. Tokens allow a user, or many users, to access the project. Channels are the various data that are accessible by a certain project. For example a user might create a dataset and then wish to annotate it. The user would create a project and add (at least) two channels, one with annotation data and one with image data. Following this the user would create a token to allow themselves access to the project.
There also are cases where the user may wish to modify aspects of a project, whether that is the token or the channel. For example after doing the annotations in the above example a user may wish to share the annotations with the public, in which case they would modify the project to be public. However, to prevent data from getting modified unintentionally the user should also modify the channels to be read-only so data cannot be tampered with.

Project Creation Tutorial
+++++++++++++++++++++++++

To create a project navigate to the datasets drop down menu and select create dataset. Fill in the appropriate data fields for each line (a full explanation of each can be found below). Click create data set and you should be re-directed to the data set main page, where you will now see a new data set with the data you selected. To use the data set create a new project/token.

To manage a project navigate to the projects dropdown menu and select view projects. To the right of the project you wish to modify select Update/Details and change the fields as desired.

+--------------------------+----------------------------------------------------------------------------------+
|Data Field                | Description                                                                      |
+--------------------------+----------------------------------------------------------------------------------+
|Project                   | The name of the project.                                                         |
+--------------------------+----------------------------------------------------------------------------------+
|Description               | The description of the project.                                                  |
+--------------------------+----------------------------------------------------------------------------------+
|Public                    | Whether or not the template is viewable to the public.                           |
+--------------------------+----------------------------------------------------------------------------------+
|Dataset                   | The dataset to be used by the project.                                           |
+--------------------------+----------------------------------------------------------------------------------+
|Database Host             | The database host to store the project. Use the default option.                  |
+--------------------------+----------------------------------------------------------------------------------+
|KV Engine                 | The KV engine used to store the project. Use the default option.                 |
+--------------------------+----------------------------------------------------------------------------------+
|KV Server                 | This is the KV key-server. Use the default option.                               |
+--------------------------+----------------------------------------------------------------------------------+
|Link to Existing Database | Use this option if the project database is already present on OCP servers.       |
+--------------------------+----------------------------------------------------------------------------------+
|Create a Default Token    | Creates a default token for the project.                                         | 
+--------------------------+----------------------------------------------------------------------------------+

Channels
========

Overview
++++++++

TODO AE

Channel Creation Tutorial
+++++++++++++++++++++++++

If you have not created a project yet follow this tutorial. Then navigate to the projects drop down menu and select projects. Select the project you wish to create a channel for and select channel, then add channel. 

To modify a channel select the Update button in the channels menu.

+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Data Field              | Description                                                                                                                    | 
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Channel Name             | Name of the Channel.                                                                                                           |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Channel Type             | The channel type you want to create. Refer to :ref:`Channel Types<ocp-channeltype>` for more details.                          |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Datatype                 | The data type of the channel you want to create. Refer to :ref:`Data Types<ocp-datatype>` for more details.                    |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Description              | A description of the channel, usually contains user description of the channel.                                                |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Read Only                | Whether or not you can modify the data existing in the channel.                                                                |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Resolution               | The base resolution of the data you want to store in this channel.                                                             |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Enable Exceptions        | Enable exceptions for an annotation channel. Use the default option.                                                           |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Propagate                | The status of propagation level of the channel. Refer to :ref:`Propagation<ocp-propagation>` for more details.                 |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Start Window             | The lowest pixel value (defaults to 0)                                                                                         |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|End Window               | The highest pixel value (defaults to 65536).                                                                                   |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Set as Default Channel   | Set the current channel to be the default channel in the project. By default the first channel is the default channel.         |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+

Token
=====

Overview
++++++++

TODO AE

Token Creation Tutorial
+++++++++++++++++++++++

If you have not created a project yet follow this tutorial. Then navigate to the projects drop down menu and select projects. Select the project you wish to create another token for and select tokens, then add token. To modify the token navigate to the tokens sub-menu again and select the modify option on the token you wish to edit. 

+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Data Field              | Description                                                                                                                    | 
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Token                    | Name of the token.                                                                                                             |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Description              | A user description of the token.                                                                                               |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Project                  | The project to associate this token to. There can multiple tokens connected to the same project.                               |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
|Public                   | Whether or the not the token is publicly viewable, which then allows people to access the channels of your project.            |
+-------------------------+--------------------------------------------------------------------------------------------------------------------------------+
