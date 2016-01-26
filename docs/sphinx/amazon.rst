S3 Bucket Upload
****************

//TODO uAlex Integrate this into the data ingest file.

Bucket Policy
=============

In order to make the data in your S3 bucket public and avaliable over HTTP you need to add this bucket policy and save it. Do replace the example bucket with your bucket name.

.. code-block:: json
    {
      "Version":"2012-10-17",
        "Statement":[
          {
            "Sid":"AddPerm",
            "Effect":"Allow",
            "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::examplebucket/*"]
          }
        ]
    }

What do I include in the data_url field?
========================================
You include the data_url as http://<example-bucket>.s3.amazonaws.com/ 
