### Configuration Information for OCP 

### Ubuntu Installation

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


### MACOS Installation

##### clone the repository and make a virtual env if you want
  ```
  git clone git@github.com:openconnectome/open-connectome.git
  mkvirtualenv ocp
  ```

##### install and configure mysql & memcache. Follow the instructions as ubuntu
  ```
  cd ~/open-connectome/setup/mysql
  ```

##### Install python packages using pip
  ```
  pip install numpy scipy h5py django django-registration-redux django-celery mysql-python pytest pillow pylibmc posix_ipc
  ```
  * Note: MACOSX note: had to follow weird library linking instructions on http://www.strangedata.ninja/2014/08/07/how-to-install-mysql-server-mac-and-python-mysqldb-library/ to get "import MySQLdb" to work

##### Django Settings
  
  * Migrate the databases, collect static files,
    ```
    cd ~/open-connectome/django
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic
    ```

  * configure settings
    ```
    cd ~/open-connectome/django/OCP
    cp settings.py.example settings.py
    cp settings_secret.py.example settings_secret.py
    ```

  * Change the following fields in settings.py
    * STATIC_ROOT
    * STATICFILES_DIRS
    * TEMPLATE_DIRS
    * FORCE_SCRIPT_NAME *for the dev server set to ""*

  * edited the fields in settings_secret.py
    * USER
    * PASSWORD
    * SECRET_KEY
    * BACKUP_PATH

##### make the logfile directory and make it readable
  ```
  sudo mkdir /var/log/ocp
  sudo chown XXX:YYY /var/log/ocp
  ```

##### Build ocplib
  ```
  cd ~/open-connectome/ocplib
  make -f makefile_MAC
  ```

##### Dev Server and tests
  * In one window, start the dev server
    ```
    cd ~/open-connectome/django
    python manage.py runserver
    ```

  * in another window
    ```
    cd ~/open-connectome/test
    py.test
    ```

##### More advanced stuff

  * onto nginx
    ```
    brew install nginx
    ```

  * add clause to nginx for ocp and upstream server (see setup/nginx/default)
  * edit uswgi file ocp.ini
  * change all paths for local system
  * configure uswgi at ~/open-connectome/setup/ocp.ini
  * run uwsgi in foreground
    ```
    uwsgi ocp.ini
    ```

  * Create paths for sockets
    ```
    mkdir /usr/local/var/run/uwsgi
    mkdir /usr/local/var/run/uwsgi/app
    mkdir /usr/local/var/run/uwsgi/app/ocp
    ```

  * Create path for logs
    ```
    mkdir /usr/local/var/log/uwsgi/
    ```

  * run nginx (as user)
    ```
    nginx
    ```

  * stop nginx
    ```
    nginx -s stop
    ```

  * run uwsgi as user
    ```
    workon XXX
    uwsgi ocp.ini
    ```

  * right now nothing is daemonized
