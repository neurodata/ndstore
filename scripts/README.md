### Scripts to downsample the databases and build hierarchy

* All the outdated scripts are now moved into deprecated. 
* imgstack16 works with the current schema and is an example script. 
* The propagate module has now been replace by the propagate web-service and the code resides in webservices/ndwsingest.py

#### Using the aws_interface script

The aws_interface script will act as an interface to manage data on S3
* Upload existing projects in *ndstore* to S3 
  * Upload a project
  * Upload a channel for a given project
  * Upload a resolution for a given channel
  ```sh
  python aws_interface.py kasthuri11 --action upload
  python aws_interface.py kasthuri11 --channel image --action upload
  python aws_interface.py kasthuri11 --channel image --res 5 --action upload
  ```
* Delete an existing project in S3
  * Delete a resolution for a given channel
  * Delete a channel for a given project
  * Delete a project
  ```sh
  python aws_interface.py kasthuri11 --action delete-project
  python aws_interface.py kasthuri11 --channel image --action delete-channel
  python aws_interface.py kasthuri11 --channel image --res 4 --action delete-res
  ```
