Statistics API
***************

.. _stats-overview:

Stats Service
===================

The stats service allows a user to compute basic statistics (mean, standard deviation, etc) for an image dataset. Since image datasets can range from a few gigabytes to a few terabytes, NeuroData doesn't compute statistics directly from the image database. Rather, the stats service provides infrastructure for the end user to generate an image histogram, which is then stored in our database. Computation of statistics is done on the fly, based on the stored image histogram. We expose RESTful Web interfaces to both generate and access the histogram, as well as generate statistics based on a stored histogram.

**Note:** Only **integer** datatypes are supported. We currently do not support generating a histogram for a float32 dataset. Furthermore, only **uint8** and **uint16** datatypes are currently supported due to memory constraints.

Additionally, the image channel must **not** be set read only for the histogram service to generate a histogram.

Histograms
==========

.. _stats-hist:

getHistogram
------------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/hist/

   :synopsis: Retrieve the histogram for an image dataset from the database.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: Histogram retrieved.
   :statuscode 404: No histogram for this token / channel.
   :statuscode 400: Web argument syntax error.

.. _stats-roi-all:

getROIs
-------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/hist/roi/

   :synopsis: Retrieve all the ROIs that correspond to stored histograms associated with the given token / channel.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: ROIs retrieved and returned as JSON.
   :statuscode 404: No histograms based on ROIs for this token / channel.
   :statuscode 400: Web argument syntax error.

.. _stats-hist-roi:

getHistogramROI
---------------

   .. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/hist/roi/(string:roi)/

      :synopsis: Retrieve the histogram corresponding to the given token, channel, and ROI.

      :param server_name: NeuroData Server Name (typically openconnecto.me)
      :type server_name: string
      :param token_name: NeuroData Token
      :type token_name: string
      :param channel_name: NeuroData Channel
      :type channel_name: string
      :param roi: ROI (:option:`x0,y0,z0-x1,y1,z1`)
      :type roi: string

      :statuscode 200: Histogram retrieved.
      :statuscode 404: No histograms based on ROIs for this token / channel.
      :statuscode 400: Web argument syntax error.


.. _stats-genhist:

genHistogram
------------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/genHist/

   :synopsis: Generate a histogram for an image dataset and store it in the database.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: Histogram generation started or queued.
   :statuscode 400: Web argument syntax error or unsupported token / channel type.

.. http:post:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/genHist/

   :synopsis: Generate a histogram for an image dataset using parameters set by user and store it in the database.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :jsonparam string roi: Generate one histogram for each of the specified regions of interest. ROIs are specified as the lower and upper coordinates of a rectangle in the following format: :option:`x0,y0,z0-x1,y1,z1` (integer only)



   :statuscode 200: Histogram generation started or queued.
   :statuscode 400: Web argument syntax error or unsupported token / channel type.

Stats
=====

.. _stats-all:

allStatistics
-------------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/all/

   :synopsis: Retrieve the histogram, mean, standard deviation, min, max, and 1st, 50th, and 99th percentile.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: Histogram and various statistics retrieved.
   :statuscode 400: Web argument syntax error.
   :statuscode 404: No histogram in database for specified token / channel.

.. _stats-mean:

Mean
----

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/mean/

   :synopsis: Calculate the mean of an image dataset from the stored histogram.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: Mean calculated and returned.
   :statuscode 400: Web argument syntax error.
   :statuscode 404: No histogram in database for specified token / channel.

.. _stats-std:

Standard Deviation
------------------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/std/

   :synopsis: Calculate the standard deviation of an image dataset from the stored histogram.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string

   :statuscode 200: Standard deviation calculated and returned.
   :statuscode 400: Web argument syntax error.
   :statuscode 404: No histogram in database for specified token / channel.

.. _stats-percentile:

Percentile
----------

.. http:get:: (string:server_name)/nd/stats/(string:token_name)/(string:channel_name)/percentile/(decimal:percentile_value)

   :synopsis: Calculate the standard deviation of an image dataset from the stored histogram.

   :param server_name: NeuroData Server Name (typically openconnecto.me)
   :type server_name: string
   :param token_name: NeuroData Token
   :type token_name: string
   :param channel_name: NeuroData Channel
   :type channel_name: string
   :param percentile_value: Arbitrary percentile expressed as a percent (e.g. 1 for 1%, 95.99 for 95.99%)
   :type percentile_value: decimal

   :statuscode 200: Percentile calculated and returned.
   :statuscode 400: Web argument syntax error.
   :statuscode 404: No histogram in database for specified token / channel.
