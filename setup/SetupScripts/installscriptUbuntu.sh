#!/bin/bash
echo -n "Install script should be placed in the open-connectome folder. "
sudo apt-get install Python-pip mysql-server python-mysqldb libmysqld-dev python-dev liblapack-dev gfortran libmemcached-dev Libhdf5-dev python-pytest

echo -n "Do you wish to create a virtual enviroment (Named OCPServer) (y/n)?" 
read answerenv

if echo "$answerenv" | grep -iq "^y" ;then
	sudo apt-get install python-virtualenv
	sudo virtualenv /home/OCPServer
	source OCPServer/bin/activate
else
    	echo -n "Please note it is easier to install django and other packages in a virtual enviroment."
fi


echo -n "Do you wish to install the python packages through pip (y/n)?" 
read answer
if echo "$answer" | grep -iq "^y" ;then
    	pip install numpy
	pip install Scipy
	pip install ez_setup
	pip install Fipy
	pip install Django
	pip install Django-registration
	pip install Django-celery
	pip install MySQL-python
	pip install TurboGears
	pip install Django-registration-redux
	pip install Cython
	pip install H5py
	pip install Pillow
	pip install Cheetah
	pip install Registration
	pip install Pylibmc
	pip install uWSGI

else
    	echo -n "Please add the packages later manually."
fi

echo -n "test"
