### Configuration Information for OCP 

##### Python dependencies 

pip install -r pip.frozen

##### Configuration files

You need to create the following files from the example files in the same directories.
  * open-connectome/django/OCP/settings.py
  * open-connectome/django/OCP/settings_secret.py

##### MySQL 

List of commands needed to configure the database for mysql

  * Create brain user as MySQL root
    
    ```sql
    create user 'brain'@'localhost' identified by 'password_here';
    grant all privileges on *.* to 'brain'@'localhost' with grant option;

    create user 'brain'@'%' identified by 'password_here';
    grant all privileges on *.* to 'brain'@'%' with grant option;
    ```

  * Create the database ocpdjango
    
    ```sql
    create database ocpdjango;
    ```

##### Nginx

  * default
    OCP configuration for /etc/nginx/sites-enabled/default
  
  * ocp.ini
    uWSGI configuration file in /etc/uwsgi/apps-enabled/

##### Celery
  
  * async.conf
    OCP configuration for /etc/supervisor/
