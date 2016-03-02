#!/bin/bash

# Installation script for ndstore backend
# Maintainer: Kunal Lillaney <lillaney@jhu.edu>

# update the sys packages and upgrade them
sudo apt-get update && upgrade -y

# apt-get install mysql packages
debconf-set-selection <<< 'mysql-server-5.6 mysql-server/root_password password neur0data'
debconf-set-selection <<< 'mysql-server-5.6 mysql-server/root_password_again password neur0data'
sudo apt-get -y install mysql-server-5.6

# apt-get install packages
sudo apt-get -y install nginx git bash-completion python-virtualenv libhdf5-dev libxslt1-dev libmemcached-dev g++ libjpeg-dev virtualenvwrapper python-dev mysql-server-5.6 libmysqlclient-dev xfsprogs supervisor rabbitmq-server uwsgi uwsgi-plugin-python liblapack-dev wget

# pip install packages
sudo pip install cython numpy
sudo pip install django h5py pytest
sudo pip install posix_ipc boto3 nibabel networkx requests lxml pylibmc pillow blosc django-registeration django-celery mysql-python libtiff

sudo mkdir /var/log/neurodata
sudo chown www-data:www-data /var/log/neurodata

# add group and user neurodata
sudo addgroup neurodata
sudo useradd -m -p neur0data -g neurodata -s /bin/bash neurodata

# switch user to neurodata and clone the repo with sub-modules
cd /home/neurodata
sudo -u neurodata git clone https://github.com/neurodata/ndstore
cd /home/neurodata/ndstore
sudo -u neurodata git checkout microns
sudo -u neurodata git submodule init
sudo -u neurodata git submodule update

# switch user to neurodata and make ctypes functions
cd /home/neurodata/ndstore/ndlib/c_version
sudo -u neurodata make -f makefile_LINUX

# configure mysql
cd /home/neurodata/ndstore/django/
sudo service mysql start && mysql -u root -pneur0data -i -e "create user 'neurodata'@'localhost' identified by 'neur0data';" && mysql -u root -pneur0data -i -e "grant all privileges on *.* to 'neurodata'@'localhost' with grant option;" && mysql -u neurodata -pneur0data -i -e "CREATE DATABASE neurodjango;"

# configure django setttings
cd /home/neurodata/ndstore/django/ND/
sudo -u neurodata cp settings.py.example settings.py
sudo ln -s /home/neurodata/ndstore/setup/docker_config/django/settings_secret.py settings_secret.py

# move the nginx config files and start service
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/neurodata/ndstore/setup/docker_config/nginx/neurodata.conf /etc/nginx/sites-enabled/default
sudo service nginx start

# move uwsgi config files and start service
sudo rm /etc/uwsgi/apps-available/neurodata.ini
sudo ln -s /home/neurodata/ndstore/setup/docker_config/uwsgi/neurodata.ini /etc/uwsgi/apps-available/
sudo rm /etc/uwsgi/apps-enabled/neurodata.ini
sudo ln -s /home/neurodata/ndstore/setup/docker_config/uwsgi/neurodata.ini /etc/uwsgi/apps-enabled/
sudo service uwsgi start

# move celery config files and start service
sudo rm /etc/supervisor/conf.d/propagate.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/celery/propagate.conf /etc/supervisor/conf.d/propagate.conf
sudo rm /etc/supervisor/conf.d/ingest.conf
sudo ln -s /home/neurodata/ndstore/setup/docker_config/celery/ingest.conf /etc/supervisor/conf.d/ingest.conf
sudo service supervisor start
sudo service rabbitmq-server start
