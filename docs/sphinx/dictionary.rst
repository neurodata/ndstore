Explanation Of Terms
********************

Assumptions
===========
The assumption is that the person reading has no experience with our service before this point, but has a sufficient knowledge of basic imaging terms, as in they understand what a pixel is. Second, this document is written primarily for neuro-scientists to become acquainted with what our service can do/does. Finally, it is assumed that the person reading this has sufficient knowledge of how imaging works to know that the image sizes for a given research effort must be consistent. 

Dataset and Related Terms
=========================

A dataset is the basic unit of how data is organized, it contains all of the data of a particular research effort. For example if the data being uploaded is image data of a human cortex that has been annotated, the dataset is where the image and annotation data are stored. Within the dataset there are channel objects, which hold individual types and instances of data (more information below) such as a particular series of annotations. Datasets are accessed indirectly through projects (more information below), as projects access the channels in a dataset.

Dataset Name
++++++++++++
Dataset Name is the overarching name of the research effort. Standard naming convention is to do LabName\_PublicationYear or LeadResearcher\_CurrentYear. 

Image Size
++++++++++

Image size is the pixel count dimensions of the data. For example is the data is stored as a series of 100, 2100x2000 pixel TIFF images, the dimensions are (2100, 2000, 100). 

Voxel Resolution
++++++++++++++++

Voxel Resolution is the number of voxels per unit pixel.

Offset
++++++

(Optional) If your data is not well aligned and there is "excess" image data you do not wish to examine, but are present in your images, offset is how you specify where your actual image starts. Offset is provided a pixel coordinate offset from origin which specifies the "actual" origin of the image. 

Time Range
++++++++++

(Optional) Time Range is a parameter to support storage of Time Series data, so the value of the tuple is a 0 to X range of how many images over time were taken, e.g. (0, 600).

Scaling Levels
++++++++++++++

(Optional)  Scaling levels is the number of levels the data is scalable to (how many zoom levels are present in the data). The highest resolution of the data is at scaling level 0, and for each level up the data is down sampled byt half (per slice).

Scaling
+++++++

(Optional) Scaling is the orientation of the data being stored, 0 corresponds to a Z-slice orientation (as in a collection of tiff images in which each tiff is a slice on the z plane) and 1 corresponds to an isotropic orientation (in which each slice is a slice on the y plane). 

Channel and Related Terms
=========================

Channels are a particular set/series of data in a given research effort. In the above example of the human cortex image and annotation data there are multiple channels; the image channel, truth annotation channel (if it exists), and perhaps some annotation channels with different annotation algorithms. There is no limit on types of channels per dataset/project, meaning that if the data has multiple sets of different images from the same type of data (e.g. multiple mouse cortices on different drugs) that is supported. 

Channel Name
++++++++++++

Channel Name is the specific name of a specific series of data. Standard naming convention is to do ImageType\_IterationNumber or Name\_SubProjectName.

Data Type
+++++++++

The data type is the storage method of data in the channel. It can be uint8, uint16, uint32, uint64, or float32. 

Channel Type
++++++++++++

The channel type is the kind of data being stored in the channel. It can be image, annotation, probmap (probability map), or timeseries. 

Exceptions
++++++++++

(Optional) Exceptions is an option to enable the possibility for annotations to contradict each other (assign different values to the same point). 0 means false, 1 means true.

Resolution
++++++++++

(Optional) Resolution is the starting resolution of the data being uploaded to the channel. 

Window Range
++++++++++++

(Optional) Window range is the maximum and minimum pixel values for a particular image. This is used so that the image can be displayed in a readable way for viewing through RESTful calls. 

Read Only
+++++++++

(Optional) This option allows the user to control if, after the initial data commit, the channel is read-only. Generally this is suggested with data that will be publicly viewable. 1 means enable read-only, 0 means disable read-only. 

Data URL
++++++++

Data URL is the location of where your data to be uploaded is located (E.g. http://ExampleServer.University.edu/MyData/UploadData/). The data must be http accessible (accessible from our servers) so storage systems like s3, dropbox, and others that require authentication keys are not accepted. 

File Format
+++++++++++

File format refers to the overarching kind of data, as in slices (normal image data) or catmaid (tile-based).

File Type
+++++++++

File type refers to the specific type of file that the data is stored in, as in, tiff, png, or tif.

Project and Related Terms
=========================

A project enables channel creation, deletion, and access. Generally they are used to organize data into groups and control access to the data being modified. For example if the research effort is divided into multiple subsections and you wish some data to be publicly viewable, but other data to be private projects are a way to control the access in this way. In the same vein, projects also allow you to control who has read/write access to what data, since different users could have different projects in the same dataset.

Project Name
++++++++++++

Project name is the specific project within a dataset's name. If there is only one project associated with a dataset then standard convention is to name the project the same as its associated dataset. 

Token Name
++++++++++

(Optional) The token name is the default token. If you do not wish to specify one, a default one will be created for you with the same name as the project name. However, if the project is private you must specify a token. 

Public
++++++

(Optional) This option allows users to specify if they want the project/channels to be publicly viewable/search-able. 

Token
=====

A token is how a unique key that accesses a specific project. When creating a project you must have at least one token that is used to access the project. There can be multiple tokens for a single project, with each being used to track who has access. Tokens are used in the API's (python and Matlab) to get project data. 



