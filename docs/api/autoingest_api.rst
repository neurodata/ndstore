Auto-Ingest API
***************

.. _json-autoingest:

autoIngest
----------

.. http:post:: (string:server_name)/nd/ca/autoIngest/

   :synopsis: Create a dataset, project and channels with a JSON file.

   :param server_name: Server Name in NeuroData. In the general case this is openconnecto.me.
   :type server_name: string

   :form JSON: Look at the Tech Sheet

   :statuscode 200: No error
   :statuscode 400: Error in file format or if channel already exists
   :statuscode 404: Error in the syntax

   **Example Request**:

   .. sourcecode:: http
      
      POST /nd/ca/json/ HTTP/1.1
      Host: openconnecto.me
      Content-Type: application/json

      {
        dataset
        project
        metadata
      }

   **Example Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        SUCCESS
      }
