#!/bin/bash

# Install basic pacakges
echo -n "Install script should be placed in the open-connectome folder. "

MySQLPass='your_password'
BrainPass=''

sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password '$MySQLPass
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password '$MySQLPass
sudo apt-get -y install mysql-server

sudo apt-get install Python-pip python-mysqldb libmysqld-dev python-dev liblapack-dev gfortran libmemcached-dev Libhdf5-dev python-pytest python-virtualenv

# Setup and install packages to the virtual enviroment
virtualenv ../OCPServer
source ../OCPServer/bin/activate
pip install setuptools
pip install numpy 
pip install Scipy ez_setup
pip install Fipy Django Django-registration Django-celery MySQL-python turbogears --allow-external PEAK-Rules --allow-unverified PEAK-Rules 
pip install Django-registration-redux Cython H5py Pillow Cheetah Registration Pylibmc uWSGI --allow-external PEAK-Rules --allow-unverified PEAK-Rules igraph

# Setup the files needed for first run of the server

cp django/OCP/settings_secret.py.example django/OCP/settings_secret.py
cp django/OCP/settings.py.example django/OCP/settings.py

sudo mkdir /var/log/ocp
sudo chown www-data:www-data /var/log/ocp
sudo touch /var/log/ocp/ocp.log
sudo chmod 777 /var/log/ocp/ocp.log


if [[ "$OSTYPE" == "linux-gnu" ]]; then
        cp ocplib/makefile_LINUX ocplib/makefile
	make -C ocplib/
elif [[ "$OSTYPE" == "darwin"* ]]; then
        cp ocplib/makefile_MAC ocplib/makefile
	make -C ocplib/
else
        # Not supported.
	echo -n "Unsupported Type"
fi

# Edit values in settings_secret.py and settings.py, including location of static files? secret key, user, pass


# Set up Mysql server values
python MySQLInitial.py MySQLPass BrainPass





